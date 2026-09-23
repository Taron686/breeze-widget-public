from datetime import date

import pytest
from PySide6.QtCore import QDate, QLocale, QRect, Qt
from PySide6.QtWidgets import QApplication

from breezewidget import CalendarPicker, FastCalendarPicker, Theme, getPalette, setTheme
from breezewidget.calendar_widget import CalendarWidget


@pytest.fixture(params=[CalendarPicker, FastCalendarPicker])
def picker(request, qtbot):
    widget = request.param(date=QDate(2024, 1, 31))
    qtbot.addWidget(widget)
    widget.show()
    yield widget
    if widget._flyout is not None:
        widget._flyout.close()


def open_calendar(picker, qtbot):
    qtbot.mouseClick(picker, Qt.LeftButton)
    assert isinstance(picker._calendar, CalendarWidget)
    return picker._calendar


def test_breeze_popup_selects_and_closes(picker, qtbot):
    calendar = open_calendar(picker, qtbot)
    assert calendar.current_month.month == 1
    selected = next(b for b in calendar.days_numbers if b.property('selected'))
    assert selected.day.date() == date(2024, 1, 31)
    button = next(b for b in calendar.days_numbers if b.day and b.day.day == 12)
    with qtbot.waitSignal(picker.dateChanged) as signal:
        qtbot.mouseClick(button, Qt.LeftButton)
    assert signal.args == [QDate(2024, 1, 12)]
    assert picker.date() == QDate(2024, 1, 12)
    assert picker._flyout is None


def test_keyboard_preview_cancel_and_confirm(picker, qtbot):
    open_calendar(picker, qtbot)
    qtbot.keyClick(QApplication.focusWidget(), Qt.Key_Right)
    assert picker.date() == QDate(2024, 1, 31)
    qtbot.keyClick(QApplication.focusWidget(), Qt.Key_Escape)
    assert picker._flyout is None
    assert picker.date() == QDate(2024, 1, 31)
    open_calendar(picker, qtbot)
    qtbot.keyClick(QApplication.focusWidget(), Qt.Key_Right)
    with qtbot.waitSignal(picker.dateChanged):
        qtbot.keyClick(QApplication.focusWidget(), Qt.Key_Return)
    assert picker.date() == QDate(2024, 2, 1)


def test_locale_and_live_theme(picker, qtbot):
    picker.setLocale(QLocale('de_DE'))
    assert picker.text() == '31.01.24'
    calendar = open_calendar(picker, qtbot)
    assert calendar._month_button.text() == 'JAN'
    assert calendar._year_button.text() == '2024'
    assert calendar._day_letter_labels[0].text().startswith('Mo')
    try:
        setTheme(Theme.DARK)
        assert calendar.colors.background == getPalette().surface2
        assert calendar.colors.text == getPalette().text1
        setTheme(Theme.LIGHT)
        assert calendar.colors.background == getPalette().surface2
    finally:
        setTheme(Theme.LIGHT)


def test_popup_fits_small_screen_and_scrolls(picker, qtbot, monkeypatch):
    from breezewidget.pickers._calendar_popup import _CalendarPopup
    monkeypatch.setattr(_CalendarPopup, '_availableGeometry', lambda self: QRect(0, 0, 280, 240))
    open_calendar(picker, qtbot)
    popup = picker._flyout
    assert QRect(0, 0, 280, 240).contains(popup.geometry())
    assert popup._scroll.verticalScrollBar().maximum() > 0
    qtbot.keyClick(QApplication.focusWidget(), Qt.Key_Right)
    qtbot.keyClick(QApplication.focusWidget(), Qt.Key_Return)
    assert picker.date() == QDate(2024, 2, 1)


def test_calendar_demo_includes_both_pickers(qtbot):
    from examples.widget_demo_pages.calender_view import CalenderViewDemoPage
    page = CalenderViewDemoPage()
    qtbot.addWidget(page)
    assert any(type(w) is CalendarPicker for w in page.findChildren(CalendarPicker))
    assert page.findChildren(FastCalendarPicker)


def test_outside_click_cancels_and_reopening_keeps_date(picker, qtbot):
    from PySide6.QtWidgets import QWidget
    outside = QWidget()
    qtbot.addWidget(outside)
    outside.setGeometry(600, 600, 80, 80)
    outside.show()
    open_calendar(picker, qtbot)
    popup_rect = picker._flyout.geometry()
    outside.move(popup_rect.left() - outside.width() - 50, popup_rect.top())
    emitted = []
    picker.dateChanged.connect(emitted.append)
    qtbot.keyClick(QApplication.focusWidget(), Qt.Key_PageDown)
    qtbot.mouseClick(outside, Qt.LeftButton)
    assert picker._flyout is None
    assert emitted == []
    calendar = open_calendar(picker, qtbot)
    assert calendar.current_month.month == 1
    assert picker.date() == QDate(2024, 1, 31)


def test_same_day_closes_without_duplicate_signal(picker, qtbot):
    calendar = open_calendar(picker, qtbot)
    emitted = []
    picker.dateChanged.connect(emitted.append)
    selected = next(b for b in calendar.days_numbers if b.property('selected'))
    qtbot.mouseClick(selected, Qt.LeftButton)
    assert picker._flyout is None
    assert emitted == []


def test_keyboard_month_and_year_navigation(picker, qtbot):
    open_calendar(picker, qtbot)
    qtbot.keyClick(QApplication.focusWidget(), Qt.Key_PageDown)
    assert QApplication.focusWidget().day.date() == date(2024, 2, 29)
    qtbot.keyClick(QApplication.focusWidget(), Qt.Key_PageDown, Qt.ControlModifier)
    assert QApplication.focusWidget().day.date() == date(2025, 2, 28)
    qtbot.keyClick(QApplication.focusWidget(), Qt.Key_Home)
    assert QApplication.focusWidget().day.date() == date(2025, 2, 1)
    qtbot.keyClick(QApplication.focusWidget(), Qt.Key_Return)
    assert picker.date() == QDate(2025, 2, 1)


def test_last_supported_month_is_reachable(picker, qtbot):
    picker.setDate(QDate(9999, 12, 31))
    calendar = open_calendar(picker, qtbot)
    try:
        assert QApplication.focusWidget().day.date() == date(9999, 12, 31)
        assert not calendar._next_btn.isEnabled()
        qtbot.keyClick(QApplication.focusWidget(), Qt.Key_Right)
        assert QApplication.focusWidget().day.date() == date(9999, 12, 31)
    finally:
        if picker._flyout:
            picker._flyout.close()


def test_popup_uses_demo_today_colors_and_solid_accent_focus(picker, qtbot, qapp):
    from PySide6.QtGui import QColor
    from breezewidget import ThemeManager
    old_theme = ThemeManager.instance().currentTheme
    old_stylesheet = qapp.styleSheet()
    try:
        setTheme(Theme.DARK, qapp)
        calendar = open_calendar(picker, qtbot)
        assert calendar.colors.today == '#f2a900'
        assert calendar.colors.today_text == '#202020'
        assert calendar.colors.resolved_today_hover() == calendar.colors.replace(
            today_hover=None).resolved_today_hover()
        qtbot.keyClick(QApplication.focusWidget(), Qt.Key_Left)
        qapp.processEvents()
        focused = QApplication.focusWidget()
        image = focused.grab().toImage()
        assert image.pixelColor(image.width() // 2, round(image.devicePixelRatio())) == QColor(getPalette().primary4)
        assert picker.date() == QDate(2024, 1, 31)
        setTheme(Theme.LIGHT, qapp)
        assert calendar.colors.today == '#f2a900'
        assert calendar.colors.today_text == '#202020'
    finally:
        if picker._flyout:
            picker._flyout.close()
        setTheme(old_theme, qapp)
        qapp.setStyleSheet(old_stylesheet)


@pytest.mark.parametrize('selected', [QDate(2026, 8, 31), QDate(2026, 10, 1)])
def test_picker_accepts_adjacent_month_day(picker, qtbot, selected):
    picker.setDate(QDate(2026, 9, 15))
    calendar = open_calendar(picker, qtbot)
    matches = [b for b in calendar.days_numbers if b.day and b.day.date() == selected.toPython()]
    assert len(matches) == 1
    with qtbot.waitSignal(picker.dateChanged) as signal:
        qtbot.mouseClick(matches[0], Qt.LeftButton)
    assert signal.args == [selected]
    assert picker.date() == selected
    assert picker._flyout is None


def test_popup_resizes_on_month_navigation(picker, qtbot, qapp):
    picker.setDate(QDate(2026, 9, 15))
    calendar = open_calendar(picker, qtbot)
    qapp.processEvents()
    five_week_height = picker._flyout.height()
    calendar._prev_btn.click()
    qapp.processEvents()
    assert picker._flyout.height() > five_week_height
    calendar._next_btn.click()
    qapp.processEvents()
    assert picker._flyout.height() == five_week_height


def test_popup_has_no_unused_scrollbar_space(picker, qtbot, qapp):
    picker.setDate(QDate(2026, 9, 1))
    calendar = open_calendar(picker, qtbot)
    qapp.processEvents()
    popup = picker._flyout
    assert popup._scroll.viewport().height() == calendar.height()
    assert popup._scroll.viewport().width() == calendar.sizeHint().width()
    assert not popup._scroll.horizontalScrollBar().isVisible()
    assert not popup._scroll.verticalScrollBar().isVisible()


def test_picker_month_year_views_keep_popup_open(picker, qtbot, qapp):
    picker.setDate(QDate(2026, 9, 15))
    calendar = open_calendar(picker, qtbot)
    calendar._month_button.click()
    calendar._choice_buttons[7].click()
    assert calendar.current_month.month == 8
    assert picker._flyout.isVisible()
    calendar._year_button.click()
    chosen = int(calendar._choice_buttons[0].text())
    calendar._choice_buttons[0].click()
    assert calendar.current_month.year == chosen
    assert picker.date() == QDate(2026, 9, 15)
    assert calendar._day_view.isVisible()
    button = next(b for b in calendar.days_numbers if b.day and b.day.date() == date(chosen, 8, 15))
    qtbot.mouseClick(button, Qt.LeftButton)
    assert picker.date() == QDate(chosen, 8, 15)
    assert picker._flyout is None


def test_month_selection_on_small_screen_and_keyboard(picker, qtbot, qapp, monkeypatch):
    from breezewidget.pickers._calendar_popup import _CalendarPopup
    monkeypatch.setattr(_CalendarPopup, '_availableGeometry', lambda self: QRect(0, 0, 280, 240))
    calendar = open_calendar(picker, qtbot)
    calendar._month_button.click()
    qapp.processEvents()
    assert QRect(0, 0, 280, 240).contains(picker._flyout.geometry())
    calendar._choice_buttons[5].setFocus()
    qtbot.keyClick(calendar._choice_buttons[5], Qt.Key_Space)
    assert calendar.current_month.month == 6
    assert calendar._day_view.isVisible()
    assert picker.date() == QDate(2024, 1, 31)


def test_calendar_arrow_focus_keeps_round_button_geometry(picker, qtbot, qapp):
    from PySide6.QtGui import QColor
    calendar = open_calendar(picker, qtbot)
    for button in (calendar._prev_btn, calendar._next_btn):
        button.setFocus()
        qapp.processEvents()
        assert button.size().toTuple() == (30, 30)
        image = button.grab().toImage()
        accent = QColor(calendar.colors.selected)
        edge = image.pixelColor(image.width() // 2, 0)
        assert max(abs(a - b) for a, b in zip(edge.getRgb()[:3], accent.getRgb()[:3])) <= 2
        assert image.pixelColor(0, 0).name() != accent.name()


def test_picker_today_link_navigates_without_committing(picker, qtbot):
    calendar = open_calendar(picker, qtbot)
    emitted = []
    picker.dateChanged.connect(emitted.append)
    calendar._month_button.click()
    calendar._today_button.click()
    today = QDate.currentDate()
    assert (calendar.current_month.year, calendar.current_month.month) == (today.year(), today.month())
    assert picker.date() == QDate(2024, 1, 31)
    assert emitted == []
    assert picker._flyout.isVisible()
    qtbot.keyClick(QApplication.focusWidget(), Qt.Key_Return)
    assert picker.date() == today
    assert picker._flyout is None


def test_today_link_removes_previous_day_highlight(picker, qtbot):
    today = QDate.currentDate()
    previous = QDate(today.year(), today.month(), 1 if today.day() != 1 else 2)
    picker.setDate(previous)
    calendar = open_calendar(picker, qtbot)
    old_button = next(b for b in calendar.days_numbers if b.day and b.day.date() == previous.toPython())
    assert old_button.property('selected')
    calendar._today_button.click()
    assert not old_button.property('selected')
    selected = [b.day.date() for b in calendar.days_numbers if b.property('selected')]
    assert selected == [today.toPython()]
    assert QApplication.focusWidget().day.date() == today.toPython()
