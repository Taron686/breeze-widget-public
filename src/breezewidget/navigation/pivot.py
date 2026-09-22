"""Pivot — top-tab navigation à la MS Office.

A row of text buttons; the active item is underlined with a sliding
accent bar. Suitable for switching between sibling pages without the
heavier sidebar of :class:`NavigationInterface`.
"""
from __future__ import annotations

from PySide6.QtCore import (
    QEasingCurve,
    QRect,
    QSize,
    Qt,
    QVariantAnimation,
    Signal,
)
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QButtonGroup, QHBoxLayout, QPushButton, QWidget

from ..constants import PROP_PIVOT, PROP_PIVOT_ITEM
from ..theme import getPalette


class PivotItem(QPushButton):
    """Single Pivot tab — visually a flat checkable button."""

    def __init__(self, text: str, route_key: str | None = None, parent: QWidget | None = None):
        super().__init__(text, parent)
        self.setProperty(PROP_PIVOT_ITEM, "true")
        self.setCheckable(True)
        self.setFlat(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(34)
        self._routeKey = route_key or text

    def routeKey(self) -> str:
        return self._routeKey

    def setRouteKey(self, key: str) -> None:
        self._routeKey = key


class Pivot(QWidget):
    """Horizontal tab strip with an animated accent indicator.

    Use :meth:`addItem` (or :meth:`addRoute`) to register tabs, then
    :meth:`setCurrentRoute` to switch. The :pyattr:`currentChanged`
    signal fires on every change with the new route key.
    """

    currentChanged = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setProperty(PROP_PIVOT, "true")

        self._items: list[PivotItem] = []
        self._current: PivotItem | None = None
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._indicator_x: float = 0.0
        self._indicator_w: float = 0.0
        self._x_animation = QVariantAnimation(self)
        self._x_animation.setDuration(180)
        self._x_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._x_animation.valueChanged.connect(self._onXChanged)
        self._w_animation = QVariantAnimation(self)
        self._w_animation.setDuration(180)
        self._w_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._w_animation.valueChanged.connect(self._onWChanged)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.addStretch(1)
        self._layout = layout
        self.setMinimumHeight(40)

    # --- public API -----------------------------------------------------

    def addItem(self, text: str, route_key: str | None = None) -> PivotItem:
        item = PivotItem(text, route_key, self)
        item.clicked.connect(lambda checked=False, key=item.routeKey(): self.setCurrentRoute(key))
        self._group.addButton(item)
        self._items.append(item)
        self._layout.insertWidget(self._layout.count() - 1, item)
        if self._current is None:
            item.setChecked(True)
            self._current = item
        return item

    addRoute = addItem  # alias

    def items(self) -> list[PivotItem]:
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
                self._animateIndicator(item)
                self.currentChanged.emit(route_key)
                return

    # --- indicator animation -------------------------------------------

    def _animateIndicator(self, item: PivotItem) -> None:
        self.ensurePolished()
        item.ensurePolished()
        target_x = float(item.x() + 8)
        target_w = float(max(item.width() - 16, 20))
        if self._indicator_w == 0.0:
            self._indicator_x = target_x
            self._indicator_w = target_w
            self.update()
            return
        self._x_animation.stop()
        self._x_animation.setStartValue(float(self._indicator_x))
        self._x_animation.setEndValue(float(target_x))
        self._x_animation.start()
        self._w_animation.stop()
        self._w_animation.setStartValue(float(self._indicator_w))
        self._w_animation.setEndValue(float(target_w))
        self._w_animation.start()

    def _onXChanged(self, value) -> None:
        self._indicator_x = float(value)
        self.update()

    def _onWChanged(self, value) -> None:
        self._indicator_w = float(value)
        self.update()

    # --- painting -------------------------------------------------------

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self._current is not None:
            self._snapIndicatorTo(self._current)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        if self._current is not None:
            self._snapIndicatorTo(self._current)

    def _snapIndicatorTo(self, item: PivotItem) -> None:
        self.ensurePolished()
        item.ensurePolished()
        self._indicator_x = float(item.x() + 8)
        self._indicator_w = float(max(item.width() - 16, 20))
        self.update()

    def paintEvent(self, event) -> None:
        del event
        if self._current is None or self._indicator_w <= 0:
            return
        palette = getPalette()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(palette.primary4))
        rect = QRect(int(self._indicator_x), self.height() - 4, int(self._indicator_w), 3)
        painter.drawRoundedRect(rect, 1.5, 1.5)
        painter.end()

    def sizeHint(self) -> QSize:
        return QSize(super().sizeHint().width(), 40)
