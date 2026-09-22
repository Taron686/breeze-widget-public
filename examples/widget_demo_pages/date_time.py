"""Date & time — DateEdit, TimeEdit, DateTimeEdit."""
from __future__ import annotations

from PySide6.QtCore import QDate, QDateTime, QTime
from PySide6.QtWidgets import QWidget

from breezewidget import DateEdit, DateTimeEdit, TimeEdit

from ._gallery import GalleryPage, _row


class DateTimeDemoPage(GalleryPage):
    def __init__(self):
        super().__init__("Date & time", "breezewidget.widgets.spin_box", "date-time")
        self.addExample("A simple DateEdit", self._datePreview())
        self.addExample("A TimeEdit with current time", self._timePreview())
        self.addExample("A DateTimeEdit with calendar popup", self._dateTimePreview())
        self.setStatus("Date & time bereit")
        self.finish()

    def _datePreview(self) -> QWidget:
        date = DateEdit()
        date.setDate(QDate.currentDate())
        date.dateChanged.connect(lambda value: self.setStatus(f"DateEdit: {value.toString('yyyy-MM-dd')}"))
        return _row(date)

    def _timePreview(self) -> QWidget:
        time = TimeEdit()
        time.setTime(QTime.currentTime())
        time.timeChanged.connect(lambda value: self.setStatus(f"TimeEdit: {value.toString('HH:mm')}"))
        return _row(time)

    def _dateTimePreview(self) -> QWidget:
        date_time = DateTimeEdit()
        date_time.setDateTime(QDateTime.currentDateTime())
        date_time.dateTimeChanged.connect(
            lambda value: self.setStatus(f"DateTimeEdit: {value.toString('yyyy-MM-dd HH:mm')}")
        )
        return _row(date_time)
