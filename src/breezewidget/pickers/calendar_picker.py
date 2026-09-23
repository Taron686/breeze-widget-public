"""CalendarPicker — push button that opens a calendar Flyout."""
from __future__ import annotations

from PySide6.QtCore import QDate, QEvent, QLocale, Signal
from PySide6.QtWidgets import QPushButton, QWidget

from ..constants import PROP_CALENDAR_PICKER
from ..calendar_widget import CalendarWidget
from ..flyout.flyout import Flyout
from ._calendar_popup import _CalendarPopup


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
        self._calendar: CalendarWidget | None = None
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
            self.setText(self.locale().toString(self._date, QLocale.FormatType.ShortFormat))
        else:
            self.setText(self._placeholder)

    def _openCalendar(self) -> None:
        if self._flyout is not None:
            return
        flyout = _CalendarPopup(self)
        self._calendar = flyout.calendar
        self._calendar.datum_angeklickt.connect(
            lambda d: self._onCalendarPicked(QDate(d.year, d.month, d.day), flyout)
        )
        flyout.closed.connect(self._calendarClosed)
        self._flyout = flyout
        flyout.exec()

    def _calendarClosed(self) -> None:
        self._flyout = None
        self._calendar = None
        self.setFocus()

    def changeEvent(self, event) -> None:
        super().changeEvent(event)
        if event.type() == QEvent.Type.LocaleChange and hasattr(self, "_date"):
            self._refreshText()

    def _onCalendarPicked(self, date: QDate, flyout: Flyout) -> None:
        self.setDate(date)
        flyout.close()
