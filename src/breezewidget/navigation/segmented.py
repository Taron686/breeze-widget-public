"""SegmentedWidget — connected toggle buttons sharing one rounded surface."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QButtonGroup, QHBoxLayout, QPushButton, QWidget

from ..constants import PROP_SEGMENTED, PROP_SEGMENTED_ITEM


class _SegmentItem(QPushButton):
    def __init__(self, text: str, route_key: str, parent: QWidget | None = None):
        super().__init__(text, parent)
        self.setProperty(PROP_SEGMENTED_ITEM, "true")
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(32)
        self._routeKey = route_key

    def routeKey(self) -> str:
        return self._routeKey


class SegmentedWidget(QWidget):
    """Group of mutually-exclusive toggle buttons rendered as one segmented control.

    Use :meth:`addItem(text, route_key)` to register segments and
    :meth:`setCurrentRoute(key)` to switch. ``currentChanged`` fires
    on each change.
    """

    currentChanged = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setProperty(PROP_SEGMENTED, "true")
        self._items: list[_SegmentItem] = []
        self._current: _SegmentItem | None = None
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addStretch(1)
        self._layout = layout

    def addItem(self, text: str, route_key: str | None = None) -> _SegmentItem:
        key = route_key or text
        item = _SegmentItem(text, key, self)
        item.clicked.connect(lambda checked=False, k=key: self.setCurrentRoute(k))
        self._group.addButton(item)
        self._items.append(item)
        # Insert before trailing stretch
        self._layout.insertWidget(self._layout.count() - 1, item)
        if self._current is None:
            item.setChecked(True)
            self._current = item
        return item

    addRoute = addItem

    def items(self) -> list[_SegmentItem]:
        return list(self._items)

    def currentRoute(self) -> str | None:
        return self._current.routeKey() if self._current is not None else None

    def setCurrentRoute(self, route_key: str) -> None:
        for item in self._items:
            if item.routeKey() == route_key:
                if item is self._current:
                    return
                item.setChecked(True)
                self._current = item
                self.currentChanged.emit(route_key)
                return
