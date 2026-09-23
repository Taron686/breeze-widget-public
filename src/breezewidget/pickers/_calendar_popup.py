"""Breeze calendar adapter and screen-constrained picker popup."""
from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import QDate, QEvent, QLocale, QPoint, Qt
from PySide6.QtWidgets import QApplication, QFrame, QScrollArea

from ..calendar_widget import CalendarColors, CalendarWidget, HeaderMode
from ..calendar_widget.commons import DayButton
from ..flyout.animation import FlyoutAnimationType
from ..flyout.flyout import Flyout, FlyoutPlacement
from ..theme import ThemeManager, getPalette


class _PickerCalendar(CalendarWidget):
    """Keep popup-specific locale, focus and theme behavior out of the base widget."""

    def set_month(self, month: datetime) -> None:
        super().set_month(month)
        for button in self.days_numbers:
            button.setEnabled(button.day is not None)
            if button.day:
                day = QDate(button.day.year, button.day.month, button.day.day)
                button.setAccessibleName(self.locale().toString(day, QLocale.LongFormat))

    def refreshTheme(self, *_args) -> None:
        palette = getPalette()
        self.set_colors(CalendarColors(
            background=palette.surface2, text=palette.text1, text_muted=palette.text2,
            divider=palette.border1, hover=palette.surface4, pressed=palette.surface5,
            today="#f2a900", today_text="#202020",
            selected=palette.primary4,
        ))
        self.setStyleSheet(self.styleSheet() + (
            f"DayButton:focus {{ border: 2px solid {palette.primary4}; }}"
        ))


class _CalendarPopup(Flyout):
    def __init__(self, picker):
        super().__init__(target=picker, parent=picker.window(), animation_type=FlyoutAnimationType.NONE)
        selected = picker.date()
        if not selected.isValid() or not 1 <= selected.year() <= 9999:
            selected = QDate.currentDate()
        self.calendar = _PickerCalendar(
            header_mode=HeaderMode.NAV_ONLY_CENTER, show_week_numbers=False,
            default_month=datetime(selected.year(), selected.month(), 1),
        )
        self.calendar.setLocale(picker.locale())
        self.calendar.setFont(picker.font())
        self.calendar.set_weekday_names([
            picker.locale().standaloneDayName(day, QLocale.ShortFormat) for day in range(1, 8)
        ])
        self.calendar.set_month(self.calendar.current_month)
        self.calendar.set_selected_date(selected.toPython())
        self.calendar._prev_btn.setAccessibleName(self.tr("Previous month"))
        self.calendar._next_btn.setAccessibleName(self.tr("Next month"))
        self.calendar.refreshTheme()
        manager = ThemeManager.instance()
        manager.themeChanged.connect(self.calendar.refreshTheme)
        manager.themeColorChanged.connect(self.calendar.refreshTheme)

        self._scroll = QScrollArea()
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._scroll.setWidgetResizable(True)
        self._scroll.setWidget(self.calendar)
        self._scroll.setMinimumSize(0, 0)
        self.setContent(self._scroll)
        self._body.setMinimumWidth(0)
        self._body.setMaximumWidth(16777215)
        self._body_layout.setContentsMargins(0, 0, 0, 0)
        self._initialDate = selected
        self.calendar._viewChanged.connect(self._resizeToCalendar)

    def _availableGeometry(self):
        screen = QApplication.screenAt(self._target.mapToGlobal(self._target.rect().center()))
        return (screen or self._target.screen()).availableGeometry()

    def exec(self) -> None:
        self._resizeToCalendar()
        super().exec()
        self._focusDate(self._initialDate)

    def _resizeToCalendar(self) -> None:
        area = self._availableGeometry()
        self.calendar.ensurePolished()
        self.calendar._day_view.layout().invalidate()
        self.calendar._day_view.layout().activate()
        self.calendar.layout().invalidate()
        self.calendar.layout().activate()
        hint = self.calendar.sizeHint()
        max_width, max_height = area.width() - 2, area.height() - 11
        vertical = horizontal = False
        # A scrollbar can force the other axis to scroll too. Reserve only
        # the required space; on normal screens the viewport fits the calendar.
        for _ in range(2):
            vertical = hint.height() + (self._scroll.horizontalScrollBar().sizeHint().height() if horizontal else 0) > max_height
            horizontal = hint.width() + (self._scroll.verticalScrollBar().sizeHint().width() if vertical else 0) > max_width
        width = hint.width() + (self._scroll.verticalScrollBar().sizeHint().width() if vertical else 0)
        height = hint.height() + (self._scroll.horizontalScrollBar().sizeHint().height() if horizontal else 0)
        self._scroll.setFixedSize(min(width, max_width), min(height, max_height))
        self._body_layout.invalidate()
        self._body_layout.activate()
        self._outer.invalidate()
        self.adjustSize()
        if self.isVisible():
            self._placeRelativeTo(self._target)

    def _placeRelativeTo(self, target) -> None:
        area = self._availableGeometry()
        top = target.mapToGlobal(QPoint(0, 0))
        below = top.y() + target.height() + 4
        if below + self.height() > area.bottom() + 1:
            self.setPlacement(FlyoutPlacement.TOP)
            below = top.y() - self.height() - 4
        x = max(area.left(), min(top.x(), area.right() - self.width() + 1))
        y = max(area.top(), min(below, area.bottom() - self.height() + 1))
        self.move(x, y)

    def _focusDate(self, day: QDate) -> None:
        if not day.isValid() or not 1 <= day.year() <= 9999:
            return
        month = self.calendar.current_month
        if (month.year, month.month) != (day.year(), day.month()):
            self.calendar.set_month(datetime(day.year(), day.month(), 1))
        for button in self.calendar.days_numbers:
            if button.day and button.day.date() == day.toPython():
                button.setFocus(Qt.PopupFocusReason)
                self._scroll.ensureWidgetVisible(button)
                break

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and (obj is self or self.isAncestorOf(obj)):
            key = event.key()
            if key == Qt.Key_Escape:
                self.close()
                return True
            if isinstance(obj, DayButton) and obj.day:
                day = QDate(obj.day.year, obj.day.month, obj.day.day)
                offsets = {Qt.Key_Left: -1, Qt.Key_Right: 1, Qt.Key_Up: -7, Qt.Key_Down: 7}
                if key in offsets:
                    self._focusDate(day.addDays(offsets[key]))
                    return True
                if key in (Qt.Key_PageUp, Qt.Key_PageDown):
                    step = -1 if key == Qt.Key_PageUp else 1
                    self._focusDate(day.addYears(step) if event.modifiers() & Qt.ControlModifier else day.addMonths(step))
                    return True
                if key in (Qt.Key_Home, Qt.Key_End):
                    self._focusDate(QDate(day.year(), day.month(), 1 if key == Qt.Key_Home else day.daysInMonth()))
                    return True
                if key in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
                    obj.click()
                    return True
        return super().eventFilter(obj, event)
