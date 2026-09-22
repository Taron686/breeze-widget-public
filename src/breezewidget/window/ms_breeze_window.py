"""MSBreezeWindow — top-pivot navigation window.

Analogous to QFluentWidgets' ``MSFluentWindow``: a frameless main
window with a horizontal :class:`Pivot` strip beneath the title bar,
backed by a stacked widget and a :class:`BreezeRouter`.
"""
from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout, QWidget

from ..navigation import Pivot
from ..theme import applyTheme
from ._navigation import _StackedWindowBase


class MSBreezeWindow(_StackedWindowBase):
    """Frameless window with title bar + horizontal pivot + stacked content."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._initWindowChrome()
        self.pivot = Pivot(self)
        self._initStackedRouter()

        self.pivot.currentChanged.connect(self.router.push)

        central = QWidget(self)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.titleBar)
        layout.addWidget(self.pivot)
        layout.addWidget(self.stackedWidget, 1)
        self.setCentralWidget(central)

        applyTheme(self)

    # --- public API -----------------------------------------------------

    def addSubInterface(
        self,
        interface: QWidget,
        text: str,
        routeKey: str | None = None,
    ) -> str:
        key = self._routeKey(interface, text, routeKey)
        self._addStackedRoute(key, interface)
        self.pivot.addItem(text, key)
        self._activateInitialRoute(key)
        return key

    # --- internal -------------------------------------------------------

    def _setCurrentRoute(self, key: str) -> None:
        self.pivot.setCurrentRoute(key)
