from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QWidget

from breezewidget import (
    BreezeIcon,
    Flyout,
    FlyoutAnimationType,
    FlyoutPlacement,
    TeachingTip,
)
from breezewidget.constants import PROP_FLYOUT, PROP_TEACHING_TIP


def test_flyout_constructs_with_content(qapp):
    parent = QWidget()
    label = QLabel("Hello")
    fly = Flyout(content=label, parent=parent)
    assert fly.property(PROP_FLYOUT) is True
    assert fly.content() is label


def test_flyout_disables_native_rectangular_window_shadow(qapp):
    fly = Flyout()
    assert fly.windowFlags() & Qt.WindowType.NoDropShadowWindowHint


def test_flyout_placement_default_is_bottom(qapp):
    fly = Flyout()
    assert fly.placement() == FlyoutPlacement.BOTTOM
    fly.setPlacement(FlyoutPlacement.TOP)
    assert fly.placement() == FlyoutPlacement.TOP


def test_flyout_set_target(qapp):
    target = QPushButton("anchor")
    fly = Flyout()
    assert fly.target() is None
    fly.setTarget(target)
    assert fly.target() is target


def test_flyout_animation_type_enum_values():
    expected = {"none", "fade", "slide_up", "slide_down", "slide_left", "slide_right"}
    assert {a.value for a in FlyoutAnimationType} == expected


def test_teaching_tip_constructs(qapp):
    parent = QWidget()
    tip = TeachingTip("Title", "Content", parent=parent, icon=BreezeIcon.INFO)
    assert tip.property(PROP_TEACHING_TIP) is True
    assert tip.property(PROP_FLYOUT) is True


def test_teaching_tip_setters_update_labels(qapp):
    tip = TeachingTip("A", "B")
    tip.setTitle("New")
    tip.setText("Body")
    assert tip._title_label.text() == "New"
    assert tip._content_label.text() == "Body"


def test_teaching_tip_add_button_returns_pushbutton(qapp):
    tip = TeachingTip("A", "B")
    button = tip.addButton("Got it")
    assert button.text() == "Got it"
    assert tip._has_buttons is True
