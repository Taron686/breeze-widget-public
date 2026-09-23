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


def test_adjacent_days_are_gray_selectable_and_keep_visible_month(qapp, qtbot):
    from PySide6.QtGui import QColor, QPalette
    from breezewidget.calendar_widget import CalendarColors
    calendar = CalendarWidget(default_month=datetime(2026, 9, 1), colors=CalendarColors(
        background='#2b2b2b', text_muted='#c8c8c8'))
    qtbot.addWidget(calendar)
    calendar.show()
    qapp.processEvents()
    assert calendar.days_numbers[0].day == datetime(2026, 8, 31)
    assert calendar.days_numbers[34].day == datetime(2026, 10, 4)
    assert calendar.days_numbers[-1].day is None
    for selected in (date(2026, 8, 31), date(2026, 10, 1)):
        button = next(b for b in calendar.days_numbers if b.day and b.day.date() == selected)
        assert button.palette().color(QPalette.ButtonText) == QColor('#797979')
        with qtbot.waitSignal(calendar.datum_angeklickt) as signal:
            button.click()
        assert signal.args == [selected]
        calendar.set_selected_date(selected)
        assert button.property('selected')
        assert calendar.current_month == datetime(2026, 9, 1)


def test_adjacent_days_use_their_own_month_activities(qapp):
    calendar = CalendarWidget(default_month=datetime(2026, 9, 1), default_activities={
        '09-2026': {31: 'wrong month'}, '08-2026': {31: 'August event'},
    })
    assert calendar.days_numbers[0].toolTip() == 'August event'


def test_month_grid_handles_year_rollover_and_date_limits():
    from breezewidget.calendar_widget.month_model import month_cells, week_numbers_for_cells
    cells = month_cells(datetime(2027, 1, 1))
    assert cells[0] == datetime(2026, 12, 28)
    assert cells[34] == datetime(2027, 1, 31)
    assert cells[-1] is None
    assert week_numbers_for_cells(cells) == ['53', '1', '2', '3', '4', '']
    assert month_cells(datetime(1, 1, 1))[0] == datetime(1, 1, 1)
    last = month_cells(datetime(9999, 12, 1))
    assert datetime(9999, 12, 31) in last
    assert last[-1] is None


def test_calendar_hides_unused_weeks_and_resizes(qapp, qtbot):
    calendar = CalendarWidget(default_month=datetime(2026, 9, 1))
    qtbot.addWidget(calendar)
    calendar.show()
    qapp.processEvents()
    assert sum(b.isVisible() for b in calendar.days_numbers) == 35
    assert [w.text() for w in calendar._week_labels if w.isVisible()] == ['36', '37', '38', '39', '40']
    five_week_height = calendar.sizeHint().height()
    calendar.set_month(datetime(2026, 8, 1))
    qapp.processEvents()
    assert sum(b.isVisible() for b in calendar.days_numbers) == 42
    assert calendar.sizeHint().height() > five_week_height
    calendar.set_month(datetime(2027, 2, 1))
    qapp.processEvents()
    assert sum(b.isVisible() for b in calendar.days_numbers) == 28
    assert calendar.sizeHint().height() < five_week_height


def test_calendar_month_and_year_selection_returns_to_days(qapp, qtbot):
    calendar = CalendarWidget(default_month=datetime(2026, 9, 1))
    qtbot.addWidget(calendar)
    calendar.show()
    emitted = []
    calendar.datum_angeklickt.connect(emitted.append)
    calendar._month_button.click()
    assert calendar._selection_panel.isVisible()
    assert not calendar._day_view.isVisible()
    calendar._choice_buttons[1].click()
    assert calendar.current_month == datetime(2026, 2, 1)
    assert calendar._day_view.isVisible()
    calendar._year_button.click()
    first_page = calendar._choice_buttons[0].text()
    calendar._next_btn.click()
    assert calendar._choice_buttons[0].text() != first_page
    chosen = int(calendar._choice_buttons[3].text())
    calendar._choice_buttons[3].click()
    assert calendar.current_month == datetime(chosen, 2, 1)
    assert calendar._day_view.isVisible()
    assert not calendar._selection_panel.isVisible()
    assert emitted == []


def test_selection_pages_respect_year_limits(qapp, qtbot):
    calendar = CalendarWidget(default_month=datetime(1, 1, 1))
    qtbot.addWidget(calendar)
    calendar.show()
    calendar._year_button.click()
    assert calendar._choice_buttons[0].text() == '1'
    assert not calendar._prev_btn.isEnabled()
    calendar.set_month(datetime(9999, 12, 1))
    calendar._year_button.click()
    assert calendar._choice_buttons[-1].text() == '9999'
    assert not calendar._next_btn.isEnabled()
    calendar._choice_buttons[-1].click()
    assert calendar.current_month == datetime(9999, 12, 1)


def test_today_link_is_independent_and_returns_from_selection(qapp, qtbot):
    calendar = CalendarWidget(default_month=datetime(2000, 1, 1))
    qtbot.addWidget(calendar)
    calendar.show()
    text = calendar._today_button.text()
    calendar.set_selected_date(date(2000, 1, 5))
    assert calendar._today_button.text() == text
    calendar._year_button.click()
    calendar._today_button.click()
    today = date.today()
    assert (calendar.current_month.year, calendar.current_month.month) == (today.year, today.month)
    assert calendar._day_view.isVisible()
    assert not calendar._selection_panel.isVisible()
    assert calendar._selected_date == today
    assert calendar.focusWidget().day.date() == today


def test_today_link_refreshes_at_date_rollover(qapp, qtbot, monkeypatch):
    from PySide6.QtCore import QDate, QLocale
    import breezewidget.calendar_widget.calendar_widget as calendar_module
    class Clock:
        value = QDate(2026, 9, 24)
        @classmethod
        def currentDate(cls):
            return cls.value
    monkeypatch.setattr(calendar_module, 'QDate', Clock)
    calendar = CalendarWidget(default_month=datetime(2000, 1, 1))
    qtbot.addWidget(calendar)
    previous = calendar._today_button.text()
    Clock.value = QDate(2026, 9, 25)
    calendar._today_timer.timeout.emit()
    assert calendar._today_button.text() != previous
    calendar._today_button.click()
    assert calendar.current_month == datetime(2026, 9, 1)
    assert calendar._today_button.text().endswith(calendar.locale().toString(Clock.value, QLocale.LongFormat))


def test_demo_today_keeps_selection_border_with_activity(qapp, qtbot):
    from PySide6.QtGui import QColor
    page = CalenderViewDemoPage()
    qtbot.addWidget(page)
    page.show()
    calendar = page._preview._calendar
    today = date.today()
    button = next(b for b in calendar.days_numbers if b.day and b.day.date() == today)
    other = next(b for b in calendar.days_numbers if b.day and b.day.month == today.month and b.day.date() != today)
    for action in (lambda: None, lambda: (other.click(), button.click()), lambda: (other.click(), calendar._today_button.click())):
        action()
        qapp.processEvents()
        assert button.property('selected')
        image = button.grab().toImage()
        assert image.pixelColor(image.width() // 2, round(image.devicePixelRatio())) == QColor(calendar.colors.selected)
