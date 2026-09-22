"""SplitBreezeWindow — sidebar nav with user-resizable boundary.

Same routing contract as :class:`BreezeWindow`, but the navigation
sidebar is wrapped in a :class:`QSplitter` so the user can drag the
divider to resize it.  The default split (240 px nav, rest content) is
configurable via :meth:`setNavigationWidth`.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from ..constants import PROP_WINDOW_CONTENT_HOST
from ..navigation import NavigationInterface, NavigationItemPosition
from ..theme import applyTheme
from ._navigation import _BreezeWindowBase


class SplitBreezeWindow(_BreezeWindowBase):
    """Frameless window with resizable sidebar navigation."""

    _DEFAULT_NAV_WIDTH = NavigationInterface.EXPANDED_MIN_WIDTH

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._initWindowChrome()
        self._initSideNavigation()
        self._initStackedRouter()

        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.splitter.setHandleWidth(1)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.addWidget(self.navigationInterface)

        self.contentHost = QWidget(self.splitter)
        self.contentHost.setProperty(PROP_WINDOW_CONTENT_HOST, True)
        self.contentHost.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        hostLayout = QVBoxLayout(self.contentHost)
        hostLayout.setContentsMargins(6, 8, 6, 0)
        hostLayout.setSpacing(0)
        hostLayout.addWidget(self.stackedWidget)
        self.splitter.addWidget(self.contentHost)

        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([self._DEFAULT_NAV_WIDTH, 800])

        central = QWidget(self)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.titleBar)
        layout.addWidget(self.splitter, 1)
        self.setCentralWidget(central)

        applyTheme(self)

    # --- public API -----------------------------------------------------

    def setNavigationWidth(self, width: int) -> None:
        self.navigationInterface.setNavigationWidth(width)
        total = max(self.splitter.width(), width + 200)
        self.splitter.setSizes([width, total - width])

    def navigationWidth(self) -> int:
        return self.navigationInterface.width()

    def addSubInterface(
        self,
        interface: QWidget,
        icon,
        text: str,
        position: NavigationItemPosition = NavigationItemPosition.TOP,
        routeKey: str | None = None,
    ) -> str:
        key = self._routeKey(interface, text, routeKey)
        self._addStackedRoute(key, interface)
        self._addNavigationRoute(key, icon, text, position)
        self._activateInitialRoute(key)
        return key
