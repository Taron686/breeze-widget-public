"""Calender_view - CalendarWidget demo page."""
from __future__ import annotations

from datetime import date, datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget

from breezewidget import BodyLabel, CalendarPicker, FastCalendarPicker, ThemeManager, getPalette, isDarkTheme
from breezewidget.calendar_widget import CalendarColors, CalendarWidget, HeaderMode, get_weekday_names

from ._gallery import GalleryPage


class CalenderViewDemoPage(GalleryPage):
    def __init__(self):
        super().__init__("Calender_view", "breezewidget.calendar_widget", "calender-view")
        self._preview = _CalendarPreview(self)
        self.addExample("CalendarWidget", self._preview)
        for picker_type in (CalendarPicker, FastCalendarPicker):
            picker = picker_type(parent=self)
            picker.dateChanged.connect(lambda d: self._onDateSelected(d.toPython()))
            self.addExample(picker_type.__name__, picker)
        self.setStatus("Kalender bereit")
        self._preview.dateSelected.connect(self._onDateSelected)
        self.finish()

    def _onDateSelected(self, selected: date) -> None:
        self.setStatus(f"Ausgewahlt: {selected.isoformat()}")


class _CalendarPreview(QWidget):
    dateSelected = Signal(date)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        now = datetime.now()
        self._activities = {
            now.strftime("%m-%Y"): {
                3: "Meeting",
                7: "Review",
                12: "Release",
                now.day: "Heute",
                21: "Planung",
            }
        }

        self._status = BodyLabel("Klicke auf einen Tag.", self)
        self._calendar = CalendarWidget(
            header_mode=HeaderMode.NAV_ONLY_CENTER,
            show_week_numbers=True,
            show_week_line=True,
            weekday_names=get_weekday_names("de"),
            default_month=now,
            default_activities=self._activities,
            colors=self._makeColors(),
            parent=self,
        )
        self._calendar.setFixedWidth(450)
        self._calendar.set_selected_date(date.today())
        self._calendar.datum_angeklickt.connect(self._selectDate)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addWidget(self._calendar, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self._status, 0, Qt.AlignmentFlag.AlignHCenter)

        manager = ThemeManager.instance()
        manager.themeChanged.connect(self._refreshTheme)
        manager.themeColorChanged.connect(self._refreshTheme)

    def _selectDate(self, selected: date) -> None:
        self._calendar.set_selected_date(selected)
        self._status.setText(selected.strftime("%d.%m.%Y"))
        self.dateSelected.emit(selected)

    def _refreshTheme(self, *_args) -> None:
        self._calendar.set_colors(self._makeColors())

    def _makeColors(self) -> CalendarColors:
        palette = getPalette()
        dark = isDarkTheme()
        return CalendarColors(
            today="#f2a900",
            today_text="#202020",
            event=palette.primary2 if dark else palette.primary1,
            event_text=palette.text1,
            selected=palette.primary4,
            background=palette.surface2,
            text=palette.text1,
            text_muted=palette.text2,
            divider=palette.border1,
            week_line=palette.border1,
            hover=palette.surface4,
            pressed=palette.surface5,
        )
