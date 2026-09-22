from __future__ import annotations

from PySide6.QtCore import QEvent, Qt
from PySide6.QtWidgets import QMainWindow, QStackedWidget, QWidget

from ..constants import PROP_WINDOW_CONTENT
from ..core import BreezeRouter
from ..icons import BreezeIcon
from ..navigation import NavigationInterface, NavigationItemPosition
from .title_bar import BreezeTitleBar


class _WindowChromeMixin:
    def _initWindowChrome(self) -> None:
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.titleBar = BreezeTitleBar(self)
        self.windowTitleChanged.connect(self.titleBar.setTitle)
        if hasattr(self, "windowIconChanged"):
            self.windowIconChanged.connect(self.titleBar.setWindowIcon)

    def refreshTheme(self) -> None:
        self.update()

    def changeEvent(self, event: QEvent) -> None:
        super().changeEvent(event)
        if event.type() == QEvent.Type.WindowStateChange:
            self.titleBar.syncWindowState()


class _StackedRouterMixin:
    def _initStackedRouter(self) -> None:
        self.stackedWidget = QStackedWidget(self)
        self.stackedWidget.setProperty(PROP_WINDOW_CONTENT, True)
        self.stackedWidget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.router = BreezeRouter(self)
        self.router.routeChanged.connect(self._onRouteChanged)

    def _routeKey(self, interface: QWidget, text: str, routeKey: str | None) -> str:
        key = routeKey or interface.objectName() or text
        if not interface.objectName():
            interface.setObjectName(key)
        return key

    def _addStackedRoute(self, key: str, interface: QWidget) -> None:
        if interface.property(PROP_WINDOW_CONTENT) is None:
            interface.setProperty(PROP_WINDOW_CONTENT, True)
        if interface.property(PROP_WINDOW_CONTENT) is True:
            interface.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.stackedWidget.addWidget(interface)
        self.router.addRoute(key, interface)

    def _activateInitialRoute(self, key: str) -> None:
        if self.stackedWidget.count() == 1:
            self.router.replace(key)

    def switchTo(self, interface: QWidget | str) -> None:
        if isinstance(interface, str):
            self.router.push(interface)
            return
        key = self.router.keyForWidget(interface)
        if key is not None:
            self.router.push(key)

    def _onRouteChanged(self, key: str) -> None:
        widget = self.router.widget(key)
        if widget is not None:
            self.stackedWidget.setCurrentWidget(widget)
        self._setCurrentRoute(key)

    def _setCurrentRoute(self, key: str) -> None:
        pass


class _SideNavigationMixin:
    def _initSideNavigation(self) -> None:
        self.navigationInterface = NavigationInterface(self)
        self._navigationMenuButtonConnected = False

    def setNavigationCompact(self, compact: bool, animated: bool = False) -> None:
        self.navigationInterface.setCompact(compact, animated=animated)

    def toggleNavigation(self, animated: bool = True) -> None:
        self.navigationInterface.setCompact(
            not self.navigationInterface.isCompact(), animated=animated
        )

    def enableNavigationMenuButton(self, visible: bool = True) -> None:
        self.titleBar.setBackButtonVisible(visible)
        self.titleBar.setBackButtonIcon(BreezeIcon.MENU)
        if visible and not self._navigationMenuButtonConnected:
            self.titleBar.backRequested.connect(self.toggleNavigation)
            self._navigationMenuButtonConnected = True
        elif not visible and self._navigationMenuButtonConnected:
            self.titleBar.backRequested.disconnect(self.toggleNavigation)
            self._navigationMenuButtonConnected = False

    def _addNavigationRoute(
        self,
        key: str,
        icon,
        text: str,
        position: NavigationItemPosition,
    ) -> None:
        self.navigationInterface.addItem(
            key,
            icon,
            text,
            onClick=lambda k=key: self.router.push(k),
            position=position,
        )

    def _setCurrentRoute(self, key: str) -> None:
        self.navigationInterface._syncCurrentItem(key)


class _BreezeWindowBase(_SideNavigationMixin, _StackedRouterMixin, _WindowChromeMixin, QMainWindow):
    pass


class _StackedWindowBase(_StackedRouterMixin, _WindowChromeMixin, QMainWindow):
    pass
