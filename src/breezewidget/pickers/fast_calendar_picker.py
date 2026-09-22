from __future__ import annotations

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QWidget

from .calendar_picker import CalendarPicker


class FastCalendarPicker(CalendarPicker):
    """Compatibility wrapper matching qfluentwidgets' parent-first constructor."""

    def __init__(self, parent: QWidget | None = None, date: QDate | None = None) -> None:
        super().__init__(date=date, parent=parent)
