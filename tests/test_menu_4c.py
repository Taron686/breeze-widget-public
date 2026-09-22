"""Smoke tests for Phase 4c: RoundMenu, CheckableMenu, CommandBar."""
from __future__ import annotations

from PySide6.QtGui import QAction, QIcon

from breezewidget import (
    BreezeIcon,
    CheckableMenu,
    CommandBar,
    RoundMenu,
    icon_from,
)


# ---------------------------------------------------------------------------
# RoundMenu
# ---------------------------------------------------------------------------

def test_round_menu_constructs(qapp):
    menu = RoundMenu("File")
    assert menu.title() == "File"
    assert menu.property("breezeRoundMenu") is True


def test_round_menu_add_breeze_action(qapp):
    menu = RoundMenu()
    triggered: list[bool] = []
    action = menu.addBreezeAction(
        icon_from(BreezeIcon.SAVE),
        "Save",
        triggered=lambda: triggered.append(True),
    )
    assert action.text() == "Save"
    assert action in menu.actions()
    action.trigger()
    assert triggered == [True]


def test_round_menu_add_actions_iterable(qapp):
    menu = RoundMenu()
    a1 = QAction("A")
    a2 = QAction("B")
    menu.addActions([a1, a2])
    assert menu.actions() == [a1, a2]


def test_round_menu_add_separator_works(qapp):
    menu = RoundMenu()
    menu.addBreezeAction(None, "One")
    sep = menu.addSeparator()
    menu.addBreezeAction(None, "Two")
    assert sep.isSeparator()
    assert len(menu.actions()) == 3


# ---------------------------------------------------------------------------
# CheckableMenu
# ---------------------------------------------------------------------------

def test_checkable_menu_add_checkable_action(qapp):
    menu = CheckableMenu()
    toggled: list[bool] = []
    action = menu.addCheckableAction(
        None, "Bold", checked=False, toggled=toggled.append
    )
    assert action.isCheckable()
    assert action.isChecked() is False
    action.setChecked(True)
    assert toggled == [True]


def test_checkable_menu_initial_checked(qapp):
    menu = CheckableMenu()
    action = menu.addCheckableAction(None, "Italic", checked=True)
    assert action.isChecked() is True


def test_checkable_menu_exclusive_group(qapp):
    menu = CheckableMenu()
    a1 = menu.addCheckableAction(None, "Left")
    a2 = menu.addCheckableAction(None, "Center")
    a3 = menu.addCheckableAction(None, "Right")
    group = menu.addExclusiveActions([a1, a2, a3])
    assert group.isExclusive()
    a1.setChecked(True)
    assert a1.isChecked()
    a2.setChecked(True)
    assert a2.isChecked()
    assert not a1.isChecked()
    assert not a3.isChecked()


# ---------------------------------------------------------------------------
# CommandBar
# ---------------------------------------------------------------------------

def test_command_bar_constructs(qapp):
    bar = CommandBar()
    assert bar.property("breezeCommandBar") is True
    assert bar.actions() == []


def test_command_bar_add_action_with_callback(qapp):
    bar = CommandBar()
    fired: list[bool] = []
    action = bar.addAction(QIcon(), "Save", lambda: fired.append(True))
    assert action.text() == "Save"
    assert action in bar.actions()
    action.trigger()
    assert fired == [True]


def test_command_bar_add_existing_action(qapp):
    bar = CommandBar()
    action = QAction("Cut")
    returned = bar.addAction(action)
    assert returned is action
    assert bar.actions() == [action]


def test_command_bar_separator(qapp):
    bar = CommandBar()
    bar.addAction(QIcon(), "Cut")
    sep = bar.addSeparator()
    bar.addAction(QIcon(), "Paste")
    assert sep.parent() is bar
    assert len(bar.actions()) == 2


def test_command_bar_overflow_hides_when_narrow(qapp, qtbot):
    bar = CommandBar()
    qtbot.addWidget(bar)
    for i in range(8):
        bar.addAction(QIcon(), f"Item {i}")
    bar.resize(120, 40)
    bar.show()
    qtbot.waitExposed(bar)
    # More button visible because total exceeds 120 px.
    assert bar._more_button.isVisible()
    assert len(bar.overflowMenu().actions()) > 0


def test_command_bar_overflow_empty_when_wide(qapp, qtbot):
    bar = CommandBar()
    qtbot.addWidget(bar)
    bar.addAction(QIcon(), "A")
    bar.addAction(QIcon(), "B")
    bar.resize(800, 40)
    bar.show()
    qtbot.waitExposed(bar)
    assert not bar._more_button.isVisible()
    assert bar.overflowMenu().actions() == []
