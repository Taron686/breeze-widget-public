"""Pickers (4e) — CalendarPicker, DatePicker, TimePicker."""
from __future__ import annotations

from PySide6.QtCore import QDate, QTime

from breezewidget import BodyLabel, CalendarPicker, DatePicker, TimePicker

from ._gallery import GalleryPage, _row


class PickersDemoPage(GalleryPage):
    """Phase 4e — CalendarPicker, DatePicker, TimePicker."""

    def __init__(self):
        super().__init__("Pickers", "breezewidget.pickers", "pickers")

        cal = CalendarPicker(QDate.currentDate())
        cal_status = BodyLabel(cal.date().toString())
        cal.dateChanged.connect(lambda d: cal_status.setText(d.toString()))
        self.addExample("CalendarPicker — button opens a calendar Flyout", _row(cal, cal_status))

        date = DatePicker(QDate(2026, 5, 8))
        date_status = BodyLabel(date.date().toString())
        date.dateChanged.connect(lambda d: date_status.setText(d.toString()))
        self.addExample("DatePicker — three-combo roller with day clamp", _row(date, date_status))

        time24 = TimePicker(QTime(14, 30), use_24h=True)
        time24_status = BodyLabel(time24.time().toString())
        time24.timeChanged.connect(lambda t: time24_status.setText(t.toString()))
        self.addExample("TimePicker — 24-hour mode", _row(time24, time24_status))

        time12 = TimePicker(QTime(20, 15), use_24h=False, minute_step=15)
        time12_status = BodyLabel(time12.time().toString())
        time12.timeChanged.connect(lambda t: time12_status.setText(t.toString()))
        self.addExample(
            "TimePicker — 12-hour mode with 15-minute step",
            _row(time12, time12_status),
        )

        self.finish()
