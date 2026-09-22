"""TabBar — closable, switchable tab strip."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QButtonGroup, QHBoxLayout, QPushButton, QWidget

from ..constants import PROP_TAB_BAR, PROP_TAB_ITEM
from ..icons import BreezeIcon
from ..widgets.button import TransparentToolButton


class TabItem(QWidget):
    """Single tab — a flat checkable button plus an optional close button."""

    clicked = Signal()
    closeRequested = Signal()

    def __init__(
        self,
        text: str,
        route_key: str,
        parent: QWidget | None = None,
        closable: bool = True,
    ):
        super().__init__(parent)
        self.setProperty(PROP_TAB_ITEM, "true")
        self._routeKey = route_key
        self._button = QPushButton(text, self)
        self._button.setProperty(PROP_TAB_ITEM, "true")
        self._button.setFlat(True)
        self._button.setCheckable(True)
        self._button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._button.setMinimumHeight(34)
        self._button.clicked.connect(lambda checked=False: self.clicked.emit())

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._button, 1)

        if closable:
            self._close_button = TransparentToolButton(BreezeIcon.CLOSE, self)
            self._close_button.setFixedSize(22, 22)
            self._close_button.clicked.connect(self.closeRequested.emit)
            layout.addWidget(self._close_button, 0, Qt.AlignmentFlag.AlignVCenter)
        else:
            self._close_button = None

    def routeKey(self) -> str:
        return self._routeKey

    def text(self) -> str:
        return self._button.text()

    def setText(self, text: str) -> None:
        self._button.setText(text)

    def isCurrent(self) -> bool:
        return self._button.isChecked()

    def setCurrent(self, current: bool) -> None:
        self._button.setChecked(bool(current))


class TabBar(QWidget):
    """Horizontal closable-tab strip.

    Methods:
        addTab(text, route_key, closable=True)
        removeTab(route_key)
        setCurrentRoute(route_key)
        currentRoute()

    Signals:
        currentChanged(route_key)
        tabCloseRequested(route_key)
    """

    currentChanged = Signal(str)
    tabCloseRequested = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setProperty(PROP_TAB_BAR, "true")
        self._tabs: list[TabItem] = []
        self._current: TabItem | None = None
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.addStretch(1)
        self._layout = layout

    def addTab(self, text: str, route_key: str | None = None, closable: bool = True) -> TabItem:
        key = route_key or text
        tab = TabItem(text, key, self, closable=closable)
        tab.clicked.connect(lambda k=key: self.setCurrentRoute(k))
        tab.closeRequested.connect(lambda k=key: self.tabCloseRequested.emit(k))
        self._group.addButton(tab._button)
        self._tabs.append(tab)
        self._layout.insertWidget(self._layout.count() - 1, tab)
        if self._current is None:
            tab.setCurrent(True)
            self._current = tab
        return tab

    def removeTab(self, route_key: str) -> None:
        for tab in list(self._tabs):
            if tab.routeKey() == route_key:
                self._layout.removeWidget(tab)
                self._tabs.remove(tab)
                self._group.removeButton(tab._button)
                tab.setParent(None)
                tab.deleteLater()
                if self._current is tab:
                    self._current = self._tabs[-1] if self._tabs else None
                    if self._current is not None:
                        self._current.setCurrent(True)
                        self.currentChanged.emit(self._current.routeKey())
                return

    def setCurrentRoute(self, route_key: str) -> None:
        for tab in self._tabs:
            if tab.routeKey() == route_key:
                if tab is self._current:
                    return
                tab.setCurrent(True)
                self._current = tab
                self.currentChanged.emit(route_key)
                return

    def currentRoute(self) -> str | None:
        return self._current.routeKey() if self._current is not None else None

    def tabs(self) -> list[TabItem]:
        return list(self._tabs)
