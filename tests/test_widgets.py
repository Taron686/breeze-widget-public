from __future__ import annotations

import pytest
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QMenu

from breezewidget import (
    BodyLabel,
    BreezeIcon,
    CaptionLabel,
    CardWidget,
    CheckBox,
    ClickableSlider,
    ComboBox,
    DateEdit,
    DateTimeEdit,
    DoubleSpinBox,
    DropDownPushButton,
    EditableComboBox,
    ElevatedCardWidget,
    HyperlinkButton,
    IconWidget,
    IndeterminateProgressBar,
    LineEdit,
    PasswordLineEdit,
    PlainTextEdit,
    PillPushButton,
    PrimaryPushButton,
    PrimaryToolButton,
    ProgressBar,
    PushButton,
    RadioButton,
    SearchLineEdit,
    SimpleCardWidget,
    Slider,
    SpinBox,
    SplitPushButton,
    StrongBodyLabel,
    SubtitleLabel,
    SwitchButton,
    TableWidget,
    TextEdit,
    TimeEdit,
    TitleLabel,
    ToggleButton,
    ToolButton,
    TransparentPushButton,
    TransparentToolButton,
    getPalette,
)


def test_basic_buttons_construct(qapp):
    PushButton("ok")
    PrimaryPushButton("ok")
    TransparentPushButton("ok")
    ToolButton(BreezeIcon.ADD)
    PrimaryToolButton(BreezeIcon.ADD)
    TransparentToolButton(BreezeIcon.ADD)
    ToggleButton("toggle")
    HyperlinkButton("https://example.com", "click")
    DropDownPushButton("more")
    SplitPushButton("split")
    PillPushButton("pill")


def test_primary_push_button_role_property(qapp):
    button = PrimaryPushButton("ok")
    assert button.property("breezeRole") == "primary"


def test_primary_tool_button_role_property(qapp):
    button = PrimaryToolButton(BreezeIcon.ADD)
    assert button.property("breezeRole") == "primary"


def test_transparent_push_button_role_property(qapp):
    button = TransparentPushButton("ok")
    assert button.property("breezeRole") == "transparent"


def test_toggle_button_is_checkable(qapp):
    button = ToggleButton("toggle")
    assert button.isCheckable() is True


def test_dropdown_and_split_buttons_accept_menus(qapp, qtbot):
    menu = QMenu()
    menu.addAction("One")

    dropdown = DropDownPushButton("open", menu=menu)
    assert dropdown.menu() is menu

    split = SplitPushButton("run")
    split.setMenu(menu)
    with qtbot.waitSignal(split.clicked, timeout=1000):
        split._button.click()
    assert split.menu() is menu


def test_pill_button_sets_property(qapp):
    button = PillPushButton("pill")
    assert button.property("breezePill") == "true"


def test_pill_button_accepts_icon_first_signature(qapp):
    button = PillPushButton(BreezeIcon.ADD, "Tag")
    assert button.text() == "Tag"
    assert not button.icon().isNull()


def test_pill_button_accepts_icon_keyword(qapp):
    button = PillPushButton("Tag", icon=BreezeIcon.ADD)
    assert button.text() == "Tag"
    assert not button.icon().isNull()


def test_pill_button_is_checkable_and_toggles(qapp):
    button = PillPushButton(BreezeIcon.ADD, "Tag")
    assert button.isCheckable() is True
    assert button.isChecked() is False
    button.toggle()
    assert button.isChecked() is True
    button.toggle()
    assert button.isChecked() is False


def test_text_inputs_construct(qapp):
    LineEdit()
    SearchLineEdit()
    pw = PasswordLineEdit()
    assert pw.echoMode() == pw.EchoMode.Password
    TextEdit()
    PlainTextEdit()


def test_search_line_edit_has_clear_button(qapp):
    line = SearchLineEdit()
    assert line.isClearButtonEnabled() is True


def test_combo_boxes_construct(qapp):
    cb = ComboBox()
    cb.addItems(["a", "b", "c"])
    assert cb.count() == 3
    editable = EditableComboBox()
    assert editable.isEditable() is True


def test_spin_and_slider_construct(qapp):
    spin = SpinBox()
    spin.setRange(0, 10)
    spin.setValue(5)
    assert spin.value() == 5
    double_spin = DoubleSpinBox()
    double_spin.setValue(1.5)
    assert double_spin.value() == 1.5
    DateEdit()
    TimeEdit()
    DateTimeEdit()
    Slider()


def test_clickable_slider_sets_value_from_position(qapp, qtbot):
    slider = ClickableSlider()
    slider.setRange(0, 100)
    slider.resize(100, 24)
    slider.show()
    qtbot.mouseClick(slider, Qt.MouseButton.LeftButton, pos=QPoint(75, 12))
    assert 65 <= slider.value() <= 85


def test_progress_bars_construct(qapp):
    bar = ProgressBar()
    bar.setRange(0, 100)
    bar.setValue(42)
    assert bar.value() == 42
    indeterminate = IndeterminateProgressBar()
    assert indeterminate.minimum() == 0 and indeterminate.maximum() == 0


def test_choice_widgets_construct(qapp):
    CheckBox("on")
    RadioButton("opt")
    switch = SwitchButton("dark")
    assert switch.property("breezeSwitch") is True
    assert switch.sizeHint().width() > 42


def test_switch_button_accepts_parent_first_constructor(qapp):
    parent = PushButton("host")
    switch = SwitchButton(parent)
    assert switch.parent() is parent
    assert switch.text() == ""


def test_switch_button_checked_changed_alias(qapp, qtbot):
    switch = SwitchButton("dark")
    with qtbot.waitSignal(switch.checkedChanged, timeout=500) as sig:
        switch.setChecked(True)
    assert sig.args == [True]


def test_icon_widget_accepts_breeze_icon_and_tracks_size(qapp):
    icon = IconWidget(BreezeIcon.HOME)
    assert not icon.pixmap().isNull()
    icon.setFixedSize(48, 48)
    assert icon.iconSize().width() == 48
    assert icon.pixmap().width() == 48


def test_icon_widget_uses_transparent_background(qapp):
    icon = IconWidget(BreezeIcon.HOME)

    assert icon.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) is True
    assert icon.autoFillBackground() is False
    assert "background: transparent" in icon.styleSheet()


def test_switch_button_animates_thumb_position(qapp, qtbot):
    switch = SwitchButton("dark")
    qtbot.addWidget(switch)
    assert switch.thumbPosition == 0.0
    switch.setChecked(True)
    qtbot.waitUntil(lambda: switch.thumbPosition == 1.0, timeout=1000)
    assert switch.thumbPosition == 1.0
    switch.setChecked(False)
    qtbot.waitUntil(lambda: switch.thumbPosition == 0.0, timeout=1000)
    assert switch.thumbPosition == 0.0


@pytest.mark.parametrize(
    "label_cls, expected_property",
    [
        (BodyLabel, None),
        (CaptionLabel, "caption"),
        (StrongBodyLabel, "bodyStrong"),
        (SubtitleLabel, "subtitle"),
        (TitleLabel, "title"),
    ],
)
def test_label_role_property(qapp, label_cls, expected_property):
    label = label_cls("hello")
    assert label.text() == "hello"
    assert label.property("breezeLabel") == expected_property


def test_dropdown_widgets_paint_without_error(qapp, qtbot):
    widgets = [
        ComboBox(),
        EditableComboBox(),
        SpinBox(),
        DoubleSpinBox(),
        DateEdit(),
        TimeEdit(),
        DateTimeEdit(),
        DropDownPushButton("more"),
    ]
    for w in widgets:
        qtbot.addWidget(w)
        w.resize(120, 34)
        w.show()
        qtbot.waitExposed(w)
        w.repaint()


def test_cards_construct_with_role(qapp):
    base = CardWidget()
    assert base.property("breezeCard") == "true"
    SimpleCardWidget()
    elevated = ElevatedCardWidget()
    assert elevated.property("breezeCard") == "elevated"


def test_card_widget_exposes_fluent_card_state_api(qapp):
    card = CardWidget()

    assert card.isClickEnabled() is False
    card.setClickEnabled(True)
    assert card.isClickEnabled() is True

    assert card.borderRadius == 5
    card.setBorderRadius(8)
    assert card.borderRadius == 8


def test_table_widget_empty_area_uses_theme_background(qapp):
    table = TableWidget()
    expected = QColor(getPalette().surface2)

    assert table.viewport().palette().color(QPalette.ColorRole.Base) == expected
    assert table.viewport().palette().color(QPalette.ColorRole.Window) == expected
    assert f"background: {expected.name()}" in table.viewport().styleSheet()
    assert f"background: {expected.name()}" in table.verticalHeader().viewport().styleSheet()
