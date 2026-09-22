from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from ..constants import PROP_WINDOW_CONTENT_HOST
from ..navigation import NavigationItemPosition
from ..theme import applyTheme
from ._navigation import _BreezeWindowBase


class BreezeWindow(_BreezeWindowBase):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._initWindowChrome()
        self._initSideNavigation()
        self._initStackedRouter()

        content = QWidget(self)
        contentLayout = QHBoxLayout(content)
        contentLayout.setContentsMargins(0, 0, 0, 0)
        contentLayout.setSpacing(0)
        contentLayout.addWidget(self.navigationInterface)

        self.contentHost = QWidget(content)
        self.contentHost.setProperty(PROP_WINDOW_CONTENT_HOST, True)
        self.contentHost.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        hostLayout = QVBoxLayout(self.contentHost)
        hostLayout.setContentsMargins(6, 8, 6, 0)
        hostLayout.setSpacing(0)
        hostLayout.addWidget(self.stackedWidget)
        contentLayout.addWidget(self.contentHost, 1)

        central = QWidget(self)
        centralLayout = QVBoxLayout(central)
        centralLayout.setContentsMargins(0, 0, 0, 0)
        centralLayout.setSpacing(0)
        centralLayout.addWidget(self.titleBar)
        centralLayout.addWidget(content, 1)

        self.setCentralWidget(central)
        applyTheme(self)

    def setTitleBarVisible(self, visible: bool) -> None:
        self.titleBar.setVisible(visible)

    def setTitleBarIcon(self, icon) -> None:
        self.titleBar.setIcon(icon)

    def addSubInterface(
        self,
        interface: QWidget,
        icon,
        text: str,
        position: NavigationItemPosition = NavigationItemPosition.TOP,
        routeKey: str | None = None,
    ) -> None:
        key = self._routeKey(interface, text, routeKey)
        self._addStackedRoute(key, interface)
        self._addNavigationRoute(key, icon, text, position)
        self._activateInitialRoute(key)
