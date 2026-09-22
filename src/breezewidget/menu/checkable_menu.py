"""CheckableMenu — RoundMenu with helpers for checkable and exclusive actions."""
from __future__ import annotations

from typing import Callable, Iterable

from PySide6.QtGui import QAction, QActionGroup, QIcon
from PySide6.QtWidgets import QWidget

from .round_menu import RoundMenu


class CheckableMenu(RoundMenu):
    """RoundMenu where actions can be checkable.

    ``addCheckableAction`` mirrors :meth:`addBreezeAction` but flips the
    action into checkable mode.  ``addExclusiveActions`` wires several
    checkable actions into a single :class:`QActionGroup` so only one is
    active at a time.
    """

    def __init__(self, title: str = "", parent: QWidget | None = None) -> None:
        super().__init__(title, parent)

    def addCheckableAction(
        self,
        icon: QIcon | None,
        text: str,
        checked: bool = False,
        toggled: Callable[[bool], None] | None = None,
    ) -> QAction:
        action = QAction(icon if icon is not None else QIcon(), text, self)
        action.setCheckable(True)
        action.setChecked(checked)
        if toggled is not None:
            action.toggled.connect(toggled)
        self.addAction(action)
        return action

    def addExclusiveActions(self, actions: Iterable[QAction]) -> QActionGroup:
        group = QActionGroup(self)
        group.setExclusive(True)
        for action in actions:
            action.setCheckable(True)
            group.addAction(action)
            if action.parent() is None:
                action.setParent(self)
            if action not in self.actions():
                self.addAction(action)
        return group
