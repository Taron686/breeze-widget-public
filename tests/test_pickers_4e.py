"""Smoke tests for Phase 4e: CalendarPicker, DatePicker, TimePicker."""
from __future__ import annotations

from PySide6.QtCore import QDate, QTime
from PySide6.QtWidgets import QWidget

from breezewidget import CalendarPicker, DatePicker, FastCalendarPicker, TimePicker


# ---------------------------------------------------------------------------
# CalendarPicker
# ---------------------------------------------------------------------------

def test_calendar_picker_initial_date(qapp):
    picker = CalendarPicker(QDate(2024, 6, 15))
    assert picker.date() == QDate(2024, 6, 15)
    assert picker.property("breezeCalendarPicker") is True


def test_calendar_picker_default_is_today(qapp):
    picker = CalendarPicker()
    assert picker.date() == QDate.currentDate()


def test_fast_calendar_picker_parent_first_constructor(qapp):
    parent = QWidget()
    date = QDate(2026, 5, 15)
    picker = FastCalendarPicker(parent, date=date)
    assert picker.parent() is parent
    assert picker.date() == date


def test_calendar_picker_set_date_emits(qapp, qtbot):
    picker = CalendarPicker(QDate(2020, 1, 1))
    with qtbot.waitSignal(picker.dateChanged, timeout=500) as sig:
        picker.setDate(QDate(2025, 5, 8))
    assert sig.args == [QDate(2025, 5, 8)]


def test_calendar_picker_same_date_no_signal(qapp):
    picker = CalendarPicker(QDate(2020, 1, 1))
    fired: list[QDate] = []
    picker.dateChanged.connect(fired.append)
    picker.setDate(QDate(2020, 1, 1))
    assert fired == []


def test_calendar_picker_invalid_date_ignored(qapp):
    picker = CalendarPicker(QDate(2020, 1, 1))
    picker.setDate(QDate())  # invalid
    assert picker.date() == QDate(2020, 1, 1)


def test_calendar_picker_text_reflects_date(qapp):
    picker = CalendarPicker(QDate(2024, 6, 15))
    assert picker.text() != ""


# ---------------------------------------------------------------------------
# DatePicker
# ---------------------------------------------------------------------------

def test_date_picker_initial_value(qapp):
    picker = DatePicker(QDate(2024, 3, 10))
    assert picker.date() == QDate(2024, 3, 10)
    assert picker.property("breezeDatePicker") is True


def test_date_picker_set_date_emits(qapp, qtbot):
    picker = DatePicker(QDate(2024, 1, 1))
    with qtbot.waitSignal(picker.dateChanged, timeout=500) as sig:
        picker.setDate(QDate(2025, 12, 31))
    assert sig.args[0] == QDate(2025, 12, 31)


def test_date_picker_clamps_day_when_month_has_fewer(qapp):
    picker = DatePicker(QDate(2024, 1, 31))
    # Switch to February (non-leap behavior on 2024 leap year: 29 days).
    picker._monthCombo.setCurrentIndex(1)  # February
    d = picker.date()
    assert d.month() == 2
    assert d.day() <= 29


def test_date_picker_year_range_clamps(qapp):
    picker = DatePicker(QDate(2050, 6, 1), year_range=(2000, 2100))
    assert picker.date().year() == 2050


def test_date_picker_default_is_today(qapp):
    picker = DatePicker()
    today = QDate.currentDate()
    assert picker.date() == today


# ---------------------------------------------------------------------------
# TimePicker
# ---------------------------------------------------------------------------

def test_time_picker_initial_value(qapp):
    picker = TimePicker(QTime(13, 45))
    assert picker.time() == QTime(13, 45)
    assert picker.property("breezeTimePicker") is True


def test_time_picker_set_time_emits(qapp, qtbot):
    picker = TimePicker(QTime(8, 0))
    with qtbot.waitSignal(picker.timeChanged, timeout=500) as sig:
        picker.setTime(QTime(22, 30))
    assert sig.args[0] == QTime(22, 30)


def test_time_picker_12h_mode_pm(qapp):
    picker = TimePicker(QTime(14, 15), use_24h=False)
    t = picker.time()
    assert t == QTime(14, 15)
    # Display hour is 2, period is PM.
    assert picker._hourCombo.currentIndex() == 1  # 2 - 1
    assert picker._periodCombo.currentIndex() == 1


def test_time_picker_12h_mode_midnight(qapp):
    picker = TimePicker(QTime(0, 0), use_24h=False)
    assert picker.time() == QTime(0, 0)
    # 12 AM displayed as hour=12, period=AM.
    assert picker._hourCombo.currentText() == "12"
    assert picker._periodCombo.currentIndex() == 0


def test_time_picker_minute_step(qapp):
    picker = TimePicker(QTime(10, 14), minute_step=15)
    # 14 // 15 == 0, so minute clamps to 0.
    assert picker.time().minute() == 0
    # Combo only has 4 entries (0, 15, 30, 45).
    assert picker._minuteCombo.count() == 4
