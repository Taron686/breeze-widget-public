from __future__ import annotations

from enum import Enum
from typing import Callable

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Property, QSize, Signal, Qt
from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QButtonGroup, QFrame, QVBoxLayout, QWidget

from ..constants import (
    PROP_NAVIGATION,
    PROP_NAVIGATION_COMPACT,
    PROP_NAVIGATION_INDICATOR,
    PROP_NAVIGATION_ITEM,
    PROP_NAVIGATION_ITEM_COMPACT,
)
from ..widgets.button import ToggleButton


class NavigationItemPosition(str, Enum):
    TOP = "top"
    SCROLL = "scroll"
    BOTTOM = "bottom"


class NavigationInterface(QWidget):
    currentItemChanged = Signal(str)
    COMPACT_WIDTH = 50
    EXPANDED_MIN_WIDTH = 190
    EXPANDED_MAX_WIDTH = 260
    ITEM_WIDTH = 42
    ITEM_HEIGHT = 40
    LEFT_MARGIN = 4
    TOP_MARGIN = 6
    COMPACT_SPACER_TEXT = " "

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setProperty(PROP_NAVIGATION, True)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._compact = False
        self._navigationWidth = self.EXPANDED_MIN_WIDTH
        self.setFixedWidth(self._navigationWidth)
        self._animation = QPropertyAnimation(self, b"navigationWidth", self)
        self._animation.setDuration(180)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.finished.connect(self._finishWidthAnimation)
        self._pendingCompact: bool | None = None
        self._buttons: dict[str, ToggleButton] = {}
        self._callbacks: dict[str, Callable[[], None]] = {}
        self._icons: dict[str, object] = {}
        self._labels: dict[ToggleButton, str] = {}
        self._compactLabels: dict[ToggleButton, str] = {}
        self._indicators: dict[ToggleButton, QFrame] = {}

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(self.LEFT_MARGIN, self.TOP_MARGIN, self.LEFT_MARGIN, self.TOP_MARGIN)
        self._layout.setSpacing(4)
        self._top = QVBoxLayout()
        self._bottom = QVBoxLayout()
        self._top.setSpacing(4)
        self._bottom.setSpacing(4)
        self._layout.addLayout(self._top)
        self._layout.addStretch(1)
        self._layout.addLayout(self._bottom)

    def getNavigationWidth(self) -> int:
        return self._navigationWidth

    def setNavigationWidth(self, width: int) -> None:
        self._navigationWidth = int(width)
        self.setMinimumWidth(self._navigationWidth)
        self.setMaximumWidth(self._navigationWidth)

    navigationWidth = Property(int, getNavigationWidth, setNavigationWidth)

    def setCompact(self, compact: bool, animated: bool = False) -> None:
        if self._compact == compact:
            return
        self._animation.stop()

        if animated:
            self._pendingCompact = compact
            self._setVisualCompact(compact, labelsVisible=not compact)
            self._animation.setStartValue(self._navigationWidth)
            self._animation.setEndValue(self.COMPACT_WIDTH if compact else self.EXPANDED_MIN_WIDTH)
            self._animation.start()
            return

        self._pendingCompact = None
        self._setVisualCompact(compact, labelsVisible=not compact)
        self.setNavigationWidth(self.COMPACT_WIDTH if compact else self.EXPANDED_MIN_WIDTH)

    def _finishWidthAnimation(self) -> None:
        if self._pendingCompact is None:
            return
        compact = self._pendingCompact
        self._pendingCompact = None
        self._setVisualCompact(compact, labelsVisible=not compact)
        self.setNavigationWidth(self.COMPACT_WIDTH if compact else self.EXPANDED_MIN_WIDTH)

    def _setVisualCompact(self, compact: bool, labelsVisible: bool) -> None:
        self._compact = compact
        self.setProperty(PROP_NAVIGATION_COMPACT, compact)
        for button in self._buttons.values():
            self._applyButtonMode(button, labelsVisible=labelsVisible)
        self._layout.setContentsMargins(self.LEFT_MARGIN, self.TOP_MARGIN, self.LEFT_MARGIN, self.TOP_MARGIN)
        self.style().unpolish(self)
        self.style().polish(self)

    def addItem(
        self,
        routeKey: str,
        icon,
        text: str,
        onClick: Callable[[], None] | None = None,
        selectable: bool = True,
        position: NavigationItemPosition = NavigationItemPosition.TOP,
        tooltip: str | None = None,
    ) -> ToggleButton:
        button = ToggleButton(text, self, icon)
        button.setProperty(PROP_NAVIGATION_ITEM, True)
        button.setIconSize(QSize(22, 22))
        button.setCheckable(selectable)
        button.setToolTip(tooltip or text)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.clicked.connect(lambda checked=False, key=routeKey: self.setCurrentItem(key))

        if selectable:
            self._group.addButton(button)
            button.toggled.connect(lambda checked, target=button: self._updateIndicator(target, checked))
        if onClick is not None:
            self._callbacks[routeKey] = onClick

        indicator = QFrame(button)
        indicator.setProperty(PROP_NAVIGATION_INDICATOR, True)
        indicator.setFixedSize(3, 26)
        indicator.hide()

        self._buttons[routeKey] = button
        self._icons[routeKey] = icon
        self._labels[button] = text
        self._compactLabels[button] = self.COMPACT_SPACER_TEXT
        self._indicators[button] = indicator
        target_layout = self._bottom if position == NavigationItemPosition.BOTTOM else self._top
        target_layout.addWidget(button)
        self._applyButtonMode(button, labelsVisible=not self._compact)
        return button

    def _applyButtonMode(self, button: ToggleButton, labelsVisible: bool | None = None) -> None:
        labelsVisible = not self._compact if labelsVisible is None else labelsVisible
        button.setProperty(PROP_NAVIGATION_ITEM_COMPACT, self._compact)
        button.style().unpolish(button)
        button.style().polish(button)
        if self._compact:
            button.setText(self._compactLabels.get(button, self.COMPACT_SPACER_TEXT))
            button.setFixedSize(self.ITEM_WIDTH, self.ITEM_HEIGHT)
        else:
            button.setText(self._labels.get(button, button.text()) if labelsVisible else self._compactLabels.get(button, self.COMPACT_SPACER_TEXT))
            button.setFixedHeight(self.ITEM_HEIGHT)
            button.setMinimumWidth(self.ITEM_WIDTH)
            button.setMaximumWidth(self.EXPANDED_MAX_WIDTH - (self.LEFT_MARGIN * 2))
        self._positionIndicator(button)

    def isCompact(self) -> bool:
        return self._compact

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        for button in self._buttons.values():
            self._applyButtonMode(button, labelsVisible=not self._compact)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        for button in self._buttons.values():
            self._positionIndicator(button)

    def _updateIndicator(self, button: ToggleButton, checked: bool) -> None:
        indicator = self._indicators.get(button)
        if indicator is None:
            return
        indicator.setVisible(checked)
        self._positionIndicator(button)

    def _positionIndicator(self, button: ToggleButton) -> None:
        indicator = self._indicators.get(button)
        if indicator is None:
            return
        indicator.move(0, max(0, (button.height() - indicator.height()) // 2))

    def refreshTheme(self) -> None:
        self.update()

    def addSeparator(self) -> None:
        self._top.addSpacing(8)

    def setCurrentItem(self, routeKey: str) -> None:
        button = self._buttons.get(routeKey)
        if button is None:
            return
        if button.isCheckable():
            button.setChecked(True)
        callback = self._callbacks.get(routeKey)
        if callback is not None:
            callback()
        self.currentItemChanged.emit(routeKey)

    def _syncCurrentItem(self, routeKey: str) -> None:
        already_current = self.currentItem() == routeKey
        button = self._buttons.get(routeKey)
        if button is None:
            return
        if button.isCheckable():
            button.setChecked(True)
        if not already_current:
            self.currentItemChanged.emit(routeKey)

    def currentItem(self) -> str | None:
        for key, button in self._buttons.items():
            if button.isChecked():
                return key
        return None

    def item(self, routeKey: str) -> ToggleButton | None:
        return self._buttons.get(routeKey)
