"""calendar_widget — Eigenständiges PySide6-Kalender-Package.

Verwendung:
    from calendar_widget import CalendarWidget, HeaderMode, get_weekday_names

Standalone-Demo:
    python -m calendar_widget
"""
from .calendar_widget import CalendarWidget
from .commons import (
    CalendarColors,
    DayButton,
    DayLetter,
    HeaderMode,
    WeekNumberLabel,
    WEEKDAY_NAMES,
    WEEKDAY_NAMES_DE,
    WEEKDAY_NAMES_EN,
    get_weekday_names,
)

__all__ = [
    "CalendarWidget",
    "CalendarColors",
    "HeaderMode",
    "DayButton",
    "DayLetter",
    "WeekNumberLabel",
    "WEEKDAY_NAMES",
    "WEEKDAY_NAMES_DE",
    "WEEKDAY_NAMES_EN",
    "get_weekday_names",
]
