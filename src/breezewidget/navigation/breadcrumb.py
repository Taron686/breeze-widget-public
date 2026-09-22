"""BreadcrumbBar — hierarchical path navigation with chevron separators."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QSizePolicy, QWidget

from ..constants import PROP_BREADCRUMB, PROP_BREADCRUMB_ITEM
from ..theme import getPalette
from ..widgets._chevron import paint_chevron


class BreadcrumbItem(QPushButton):
    """Single breadcrumb crumb — flat text button with a route key."""

    def __init__(self, text: str, route_key: str, parent: QWidget | None = None):
        super().__init__(text, parent)
        self.setProperty(PROP_BREADCRUMB_ITEM, "true")
        self.setFlat(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(28)
        self._routeKey = route_key

    def routeKey(self) -> str:
        return self._routeKey


class _BreadcrumbSeparator(QWidget):
    """Right-pointing flat chevron between crumbs."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setFixedSize(16, 28)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def paintEvent(self, event) -> None:
        del event
        palette = getPalette()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        # Reuse the down-chevron helper but rotate by 90° to point right.
        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(-90)
        paint_chevron(
            painter,
            cx=0,
            cy=0,
            half_size=4.0,
            color=QColor(palette.text2),
            stroke_width=1.4,
            direction="down",
        )
        painter.end()


class BreadcrumbBar(QWidget):
    """Path navigation showing ancestors with right-chevron separators.

    Items are added in display order (root first). Clicking an item
    emits :pyattr:`currentChanged` with that item's route key. The
    last added item is treated as the current location and rendered
    in the primary text colour while ancestors are subdued.
    """

    currentChanged = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setProperty(PROP_BREADCRUMB, "true")
        self._items: list[BreadcrumbItem] = []
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addStretch(1)
        self._layout = layout

    def addItem(self, text: str, route_key: str | None = None) -> BreadcrumbItem:
        key = route_key or text
        if self._items:
            sep = _BreadcrumbSeparator(self)
            self._layout.insertWidget(self._layout.count() - 1, sep)
        item = BreadcrumbItem(text, key, self)
        item.clicked.connect(lambda checked=False, k=key: self._onItemClicked(k))
        self._items.append(item)
        self._layout.insertWidget(self._layout.count() - 1, item)
        self._refreshActiveStyle()
        return item

    def clear(self) -> None:
        while self._layout.count() > 1:
            widget = self._layout.takeAt(0).widget()
            if widget is not None:
                widget.deleteLater()
        self._items = []

    def truncateTo(self, route_key: str) -> None:
        """Drop every crumb after the one with ``route_key``.

        The matching crumb stays and becomes the new active leaf.
        No-op if the key is unknown or already the leaf.
        """
        target_index = -1
        for index, item in enumerate(self._items):
            if item.routeKey() == route_key:
                target_index = index
                break
        if target_index < 0 or target_index == len(self._items) - 1:
            return
        # Remove every layout entry after the target's slot. The layout
        # alternates: item, separator, item, separator, ... so the
        # target item sits at layout index ``target_index * 2``.
        keep_count = target_index * 2 + 1
        while self._layout.count() - 1 > keep_count:
            widget = self._layout.takeAt(keep_count).widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
        self._items = self._items[: target_index + 1]
        self._refreshActiveStyle()

    def _onItemClicked(self, route_key: str) -> None:
        self.truncateTo(route_key)
        self.currentChanged.emit(route_key)

    def items(self) -> list[BreadcrumbItem]:
        return list(self._items)

    def currentRoute(self) -> str | None:
        return self._items[-1].routeKey() if self._items else None

    def _refreshActiveStyle(self) -> None:
        for index, item in enumerate(self._items):
            is_last = index == len(self._items) - 1
            item.setProperty("breezeBreadcrumbActive", "true" if is_last else "false")
            item.style().unpolish(item)
            item.style().polish(item)
