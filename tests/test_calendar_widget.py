from __future__ import annotations

from datetime import date, datetime

from breezewidget.calendar_widget import CalendarWidget, HeaderMode, get_weekday_names
from examples.widget_demo_pages.calender_view import CalenderViewDemoPage


def test_calendar_widget_constructs_with_42_day_buttons(qapp):
    calendar = CalendarWidget(header_mode=HeaderMode.NAV_ONLY_CENTER)
    assert len(calendar.days_numbers) == 42
    assert calendar.current_month.month == datetime.now().month


def test_calendar_widget_uses_weekday_names(qapp):
    calendar = CalendarWidget(weekday_names=get_weekday_names("de"))
    labels = [label.text() for label in calendar._day_letter_labels]
    assert labels == ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


def test_calendar_widget_click_selects_day(qapp, qtbot):
    selected = date(2026, 5, 12)
    calendar = CalendarWidget(default_month=datetime(2026, 5, 1))
    button = next(
        button for button in calendar.days_numbers if button.day and button.day.date() == selected
    )

    with qtbot.waitSignal(calendar.datum_angeklickt) as blocker:
        button.click()

    assert blocker.args == [selected]


def test_calendar_widget_bordered_days_keep_fixed_button_size(qapp):
    selected = date.today()
    calendar = CalendarWidget(
        default_month=datetime(selected.year, selected.month, 1),
        default_activities={selected.strftime("%m-%Y"): {selected.day: "Heute"}},
    )
    calendar.show()
    qapp.processEvents()

    event_button = next(
        button for button in calendar.days_numbers if button.day and button.day.date() == selected
    )
    assert event_button.size().toTuple() == (38, 38)

    calendar.set_selected_date(selected)
    assert event_button.size().toTuple() == (38, 38)

    normal_button = next(
        button for button in calendar.days_numbers if button.day and button.day.date() != selected
    )
    calendar.set_selected_date(normal_button.day.date())
    assert normal_button.size().toTuple() == (38, 38)


def test_calendar_demo_keeps_activities_but_uses_plain_visual_style(qapp):
    page = CalenderViewDemoPage()
    calendar = page._preview._calendar

    assert calendar._header_mode is HeaderMode.NAV_ONLY_CENTER
    assert calendar.activities
    assert any(button.objectName() == "day_number_event" for button in calendar.days_numbers)
    assert calendar.colors.today == "#f2a900"
    assert "DayButton#day_number_event     { background: transparent;" in calendar.styleSheet()
    assert "padding: 0;" in calendar.styleSheet()
