"""RoundMenu — frameless QMenu with rounded corners and Breeze styling."""
from __future__ import annotations

from typing import Any, Callable, Iterable

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMenu, QWidget

from ..constants import PROP_ROUND_MENU
from ..icons._themed import ThemedActionIcons
from ..widgets._popup import apply_breeze_popup_window


class RoundMenu(QMenu):
    """QMenu styled by the Breeze theme with rounded corners.

    Behaves like a normal :class:`QMenu` — actions, separators and submenus
    work as usual.  Use :meth:`addAction` for plain entries; convenience
    helpers :meth:`addBreezeAction` accept ``(icon, text, callback)`` in
    one call.
    """

    def __init__(
        self,
        title: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(title, parent)
        self.setProperty(PROP_ROUND_MENU, True)
        self._icons = ThemedActionIcons()
        apply_breeze_popup_window(self)

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def addBreezeAction(
        self,
        icon: Any,
        text: str,
        triggered: Callable[[], None] | None = None,
    ) -> QAction:
        action = QAction(QIcon(), text, self)
        self._icons.set(action, icon)
        if triggered is not None:
            action.triggered.connect(lambda checked=False, cb=triggered: cb())
        self.addAction(action)
        return action

    def refreshTheme(self) -> None:
        self._icons.refresh()

    def addActions(self, actions: Iterable[QAction]) -> None:  # type: ignore[override]
        for action in actions:
            self.addAction(action)
