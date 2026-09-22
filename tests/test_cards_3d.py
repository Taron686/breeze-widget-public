from __future__ import annotations

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QLabel

from breezewidget import (
    BreezeIcon,
    ComboBoxSettingCard,
    CustomColorSettingCard,
    ExpandSettingCard,
    HeaderCardWidget,
    HyperlinkCard,
    OptionsSettingCard,
    PushSettingCard,
    RangeSettingCard,
    SettingCard,
    SettingCardGroup,
    SwitchSettingCard,
)


def test_header_card_exposes_title_and_content_layout(qapp):
    card = HeaderCardWidget("General")
    child = QLabel("Body")

    card.addWidget(child)
    card.setTitle("Account")

    assert card.title() == "Account"
    assert card.viewLayout.count() == 1
    assert child.parent() is card
    assert card.property("breezeCard") == "true"


def test_setting_card_sets_icon_title_caption_and_action(qapp):
    action = QLabel("Action")
    card = SettingCard(BreezeIcon.SETTINGS, "Theme", "Choose app colors", action=action)

    assert card.title() == "Theme"
    assert card.caption() == "Choose app colors"
    assert card.icon() == BreezeIcon.SETTINGS
    assert card.iconLabel.isHidden() is False
    assert card.actionWidget() is action
    assert card.property("breezeCard") == "true"

    card.setCaption("")
    assert card.captionLabel.isVisible() is False


def test_setting_card_group_tracks_cards(qapp):
    group = SettingCardGroup("Appearance")
    card = SettingCard(BreezeIcon.SUN, "Theme")

    assert group.addSettingCard(card) is card
    assert group.cards() == [card]
    assert group.cardLayout.count() == 1


def test_switch_setting_card_exposes_checked_state(qapp, qtbot):
    card = SwitchSettingCard(BreezeIcon.MOON, "Dark mode", checked=True)
    assert card.isChecked() is True

    with qtbot.waitSignal(card.checkedChanged, timeout=1000) as blocker:
        card.setChecked(False)

    assert blocker.args == [False]
    assert card.isChecked() is False


def test_combo_box_setting_card_exposes_selection(qapp, qtbot):
    card = ComboBoxSettingCard(["Small", "Medium", "Large"], BreezeIcon.SETTINGS, "Density", current_index=1)

    assert card.currentText() == "Medium"
    with qtbot.waitSignal(card.currentTextChanged, timeout=1000) as blocker:
        card.setCurrentIndex(2)

    assert blocker.args == ["Large"]


def test_range_setting_card_syncs_value_label(qapp, qtbot):
    card = RangeSettingCard(BreezeIcon.SETTINGS, "Volume", minimum=0, maximum=10, value=4)

    assert card.value() == 4
    assert card.valueLabel.text() == "4"
    with qtbot.waitSignal(card.valueChanged, timeout=1000) as blocker:
        card.setValue(8)

    assert blocker.args == [8]
    assert card.valueLabel.text() == "8"


def test_range_setting_card_action_container_is_transparent(qapp):
    card = RangeSettingCard(BreezeIcon.SETTINGS, "Volume", minimum=0, maximum=10, value=4)
    action = card.actionWidget()

    assert action is not None
    assert action.property("_breezeSettingAction") is True
    assert "background: transparent" in action.styleSheet()


def test_push_and_hyperlink_cards_construct_actions(qapp, qtbot):
    push = PushSettingCard("Run", BreezeIcon.CHECK, "Job")
    with qtbot.waitSignal(push.actionClicked, timeout=1000):
        push.button.click()

    link = HyperlinkCard("https://example.com", "Open", BreezeIcon.INFO, "Docs")
    assert link.url == "https://example.com"
    assert link.button.text() == "Open"


def test_expand_setting_card_toggles_content(qapp, qtbot):
    card = ExpandSettingCard(BreezeIcon.MORE, "Advanced")
    child = QLabel("Details")
    card.addWidget(child)

    assert card.isExpanded() is False
    assert card.contentWidget.isHidden() is True
    assert not card.expandButton.icon().isNull()
    collapsed_bounds = _icon_opaque_bounds(card.expandButton.icon().pixmap(card.expandButton.iconSize()).toImage())
    assert collapsed_bounds is not None
    # A right-facing chevron is taller than it is wide.
    assert collapsed_bounds[3] - collapsed_bounds[1] + 1 >= 12
    assert collapsed_bounds[3] - collapsed_bounds[1] > collapsed_bounds[2] - collapsed_bounds[0]

    with qtbot.waitSignal(card.expandedChanged, timeout=1000) as blocker:
        card.toggleExpanded()

    assert blocker.args == [True]
    assert card.isExpanded() is True
    assert card.contentWidget.isHidden() is False
    assert card.viewLayout.count() == 1
    assert not card.expandButton.icon().isNull()
    expanded_bounds = _icon_opaque_bounds(card.expandButton.icon().pixmap(card.expandButton.iconSize()).toImage())
    assert expanded_bounds is not None
    assert expanded_bounds[2] - expanded_bounds[0] > expanded_bounds[3] - expanded_bounds[1]


def test_options_setting_card_tracks_current_option(qapp, qtbot):
    card = OptionsSettingCard([("Light", "light"), ("Dark", "dark")], BreezeIcon.SUN, "Theme")

    assert card.currentOption() == "light"
    with qtbot.waitSignal(card.currentChanged, timeout=1000) as blocker:
        card.setCurrentOption("dark")

    assert blocker.args == ["dark"]
    assert card.currentOption() == "dark"


def test_custom_color_setting_card_sets_color(qapp, qtbot):
    card = CustomColorSettingCard("#0067c0", BreezeIcon.EDIT, "Accent")

    with qtbot.waitSignal(card.colorChanged, timeout=1000) as blocker:
        card.setColor("#ff0000")

    assert blocker.args[0] == QColor("#ff0000")
    assert card.color() == QColor("#ff0000")
    assert "#ff0000" in card.swatch.styleSheet()


def test_custom_color_setting_card_action_container_is_transparent(qapp):
    card = CustomColorSettingCard("#0067c0", BreezeIcon.EDIT, "Accent")
    action = card.actionWidget()

    assert action is not None
    assert action.property("_breezeSettingAction") is True
    assert "background: transparent" in action.styleSheet()


def _icon_opaque_bounds(image) -> tuple[int, int, int, int] | None:
    points = [
        (x, y)
        for y in range(image.height())
        for x in range(image.width())
        if image.pixelColor(x, y).alpha() > 32
    ]
    if not points:
        return None
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)
