"""CalendarPicker — push button that opens a calendar Flyout."""
from __future__ import annotations

from PySide6.QtCore import QDate, QLocale, Qt, Signal
from PySide6.QtWidgets import QCalendarWidget, QPushButton, QWidget

from ..constants import PROP_CALENDAR_PICKER
from ..flyout.flyout import Flyout, FlyoutPlacement


class CalendarPicker(QPushButton):
    """Button that displays a date and opens a calendar popup on click.

    The selected date is formatted with the current :class:`QLocale`
    short-date pattern.  ``dateChanged`` fires after each user pick.
    Programmatic :meth:`setDate` does **not** open the popup but emits
    the signal when the value actually changes.
    """

    dateChanged = Signal(QDate)

    def __init__(
        self,
        date: QDate | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setProperty(PROP_CALENDAR_PICKER, True)
        self.setMinimumHeight(34)
        self._date = QDate.currentDate() if date is None else QDate(date)
        self._placeholder = "Pick a date"
        self._flyout: Flyout | None = None
        self._calendar: QCalendarWidget | None = None
        self._refreshText()
        self.clicked.connect(self._openCalendar)

    # --- public API -----------------------------------------------------

    def date(self) -> QDate:
        return QDate(self._date)

    def setDate(self, date: QDate) -> None:
        if not date.isValid():
            return
        if date == self._date:
            return
        self._date = QDate(date)
        self._refreshText()
        self.dateChanged.emit(QDate(self._date))

    def setPlaceholderText(self, text: str) -> None:
        self._placeholder = text
        self._refreshText()

    # --- internal -------------------------------------------------------

    def _refreshText(self) -> None:
        if self._date.isValid():
            self.setText(QLocale().toString(self._date, QLocale.FormatType.ShortFormat))
        else:
            self.setText(self._placeholder)

    def _openCalendar(self) -> None:
        calendar = QCalendarWidget()
        calendar.setSelectedDate(self._date if self._date.isValid() else QDate.currentDate())
        calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        calendar.setHorizontalHeaderFormat(
            QCalendarWidget.HorizontalHeaderFormat.SingleLetterDayNames
        )
        calendar.setFirstDayOfWeek(Qt.DayOfWeek.Monday)
        self._calendar = calendar

        flyout = Flyout(content=calendar, target=self, parent=self.window())
        flyout.setPlacement(FlyoutPlacement.BOTTOM)
        calendar.clicked.connect(lambda d: self._onCalendarPicked(d, flyout))
        self._flyout = flyout
        flyout.exec()

    def _onCalendarPicked(self, date: QDate, flyout: Flyout) -> None:
        self.setDate(date)
        flyout.close()
