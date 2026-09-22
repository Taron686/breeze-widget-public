"""DatePicker — three combo boxes (day / month / year) for date entry."""
from __future__ import annotations

from PySide6.QtCore import QDate, QLocale, Signal
from PySide6.QtWidgets import QHBoxLayout, QWidget

from ..constants import PROP_DATE_PICKER
from ..widgets.combo_box import ComboBox


class DatePicker(QWidget):
    """Three-combo date entry widget (day, month, year).

    The widget always exposes a valid :class:`QDate`.  Day count
    automatically adjusts to the active month/year (e.g. switching to
    February clamps day 31 to 28 or 29).  ``dateChanged`` fires after
    every change; the signal is suspended while internal sync runs to
    avoid duplicate emissions when a single user edit triggers a chain
    of updates.
    """

    dateChanged = Signal(QDate)

    def __init__(
        self,
        date: QDate | None = None,
        year_range: tuple[int, int] = (1900, 2100),
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setProperty(PROP_DATE_PICKER, True)
        self._suspend = False
        self._year_min, self._year_max = year_range

        self._dayCombo = ComboBox(self)
        self._monthCombo = ComboBox(self)
        self._yearCombo = ComboBox(self)

        self._populateMonths()
        self._populateYears()
        # Days are populated dynamically based on month/year.

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(self._dayCombo, 1)
        layout.addWidget(self._monthCombo, 2)
        layout.addWidget(self._yearCombo, 1)

        self._dayCombo.currentIndexChanged.connect(self._onChanged)
        self._monthCombo.currentIndexChanged.connect(self._onMonthOrYearChanged)
        self._yearCombo.currentIndexChanged.connect(self._onMonthOrYearChanged)

        self.setDate(date or QDate.currentDate())

    # --- public API -----------------------------------------------------

    def date(self) -> QDate:
        year = self._currentYear()
        month = self._monthCombo.currentIndex() + 1
        day = self._dayCombo.currentIndex() + 1
        return QDate(year, month, day)

    def setDate(self, date: QDate) -> None:
        if not date.isValid():
            return
        clamped_year = max(self._year_min, min(self._year_max, date.year()))
        self._suspend = True
        try:
            year_idx = clamped_year - self._year_min
            self._yearCombo.setCurrentIndex(year_idx)
            self._monthCombo.setCurrentIndex(date.month() - 1)
            self._refreshDays(preserve_day=date.day())
        finally:
            self._suspend = False
        self.dateChanged.emit(self.date())

    # --- internal -------------------------------------------------------

    def _populateMonths(self) -> None:
        locale = QLocale()
        names = [locale.monthName(m, QLocale.FormatType.LongFormat) for m in range(1, 13)]
        self._monthCombo.addItems(names)

    def _populateYears(self) -> None:
        self._yearCombo.addItems([str(y) for y in range(self._year_min, self._year_max + 1)])

    def _currentYear(self) -> int:
        idx = max(0, self._yearCombo.currentIndex())
        return self._year_min + idx

    def _onMonthOrYearChanged(self, *_) -> None:
        if self._suspend:
            return
        previous_day = self._dayCombo.currentIndex() + 1
        self._suspend = True
        try:
            self._refreshDays(preserve_day=previous_day)
        finally:
            self._suspend = False
        self.dateChanged.emit(self.date())

    def _onChanged(self, *_) -> None:
        if self._suspend:
            return
        self.dateChanged.emit(self.date())

    def _refreshDays(self, preserve_day: int) -> None:
        year = self._currentYear()
        month = self._monthCombo.currentIndex() + 1
        days_in_month = QDate(year, month, 1).daysInMonth()
        self._dayCombo.clear()
        self._dayCombo.addItems([str(d) for d in range(1, days_in_month + 1)])
        clamped = max(1, min(days_in_month, preserve_day))
        self._dayCombo.setCurrentIndex(clamped - 1)
