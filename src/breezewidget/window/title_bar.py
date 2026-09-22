from __future__ import annotations

from typing import Callable, Any

from PySide6.QtCore import QPoint, QSize, Signal, Qt
from PySide6.QtGui import QIcon, QMouseEvent
from PySide6.QtWidgets import QHBoxLayout, QLabel, QMainWindow, QToolButton, QWidget

from ..constants import (
    PROP_TITLE_BAR,
    PROP_TITLE_BUTTON,
    PROP_TITLE_BUTTON_ROLE,
    PROP_TITLE_ICON,
    PROP_TITLE_LABEL,
    TITLE_BUTTON_ROLE_ACTION,
    TITLE_BUTTON_ROLE_BACK,
    TITLE_BUTTON_ROLE_CLOSE,
    TITLE_BUTTON_ROLE_MAXIMIZE,
    TITLE_BUTTON_ROLE_MINIMIZE,
    TITLE_BUTTON_ROLE_RESTORE,
)
from ..icons import BreezeIcon
from ..icons._themed import ThemedIcon
from ._title_buttons import _CaptionButton, _TitleButton


class BreezeTitleBar(QWidget):
    backRequested = Signal()

    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        self.setProperty(PROP_TITLE_BAR, True)
        self.setFixedHeight(40)
        self._dragPosition: QPoint | None = None
        self._titleIcon: Any | None = None
        self._titleIconSize = QSize(20, 20)
        self._titleThemedIcon: ThemedIcon | None = None
        self._actionButtons: list[QToolButton] = []

        self.backButton = self._createButton("", TITLE_BUTTON_ROLE_BACK, BreezeIcon.BACK, width=42)
        self.backButton.clicked.connect(self.backRequested)
        self.backButton.hide()

        self.iconLabel = QLabel(self)
        self.iconLabel.setProperty(PROP_TITLE_ICON, True)
        self.iconLabel.setFixedSize(32, 40)
        self.iconLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.titleLabel = QLabel(parent.windowTitle(), self)
        self.titleLabel.setProperty(PROP_TITLE_LABEL, True)
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        self.minButton = self._createCaptionButton(TITLE_BUTTON_ROLE_MINIMIZE)
        self.maxButton = self._createCaptionButton(TITLE_BUTTON_ROLE_MAXIMIZE)
        self.closeButton = self._createCaptionButton(TITLE_BUTTON_ROLE_CLOSE)

        self.minButton.clicked.connect(parent.showMinimized)
        self.maxButton.clicked.connect(self.toggleMaximized)
        self.closeButton.clicked.connect(parent.close)

        self._customLayout = QHBoxLayout()
        self._customLayout.setContentsMargins(0, 0, 8, 0)
        self._customLayout.setSpacing(6)

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(4, 0, 0, 0)
        self._layout.setSpacing(0)
        self._layout.addWidget(self.backButton)
        self._layout.addWidget(self.iconLabel)
        self._layout.addWidget(self.titleLabel, 1)
        self._layout.addLayout(self._customLayout)
        self._layout.addWidget(self.minButton)
        self._layout.addWidget(self.maxButton)
        self._layout.addWidget(self.closeButton)

        self.setWindowIcon(parent.windowIcon())

    def _createButton(self, text: str, role: str, icon=None, width: int = 46) -> QToolButton:
        button = _TitleButton(self)
        button.setText(text)
        button.setProperty(PROP_TITLE_BUTTON, True)
        button.setProperty(PROP_TITLE_BUTTON_ROLE, role)
        button.setFixedSize(width, 40)
        button.setIconSize(QSize(20, 20))
        button.setCursor(Qt.CursorShape.ArrowCursor)
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        button._breezeThemedIcon = ThemedIcon(button.setIcon, size=20)  # type: ignore[attr-defined]
        if icon is not None:
            button._breezeThemedIcon.set(icon)  # type: ignore[attr-defined]
        return button

    def _createCaptionButton(self, role: str) -> QToolButton:
        button = _CaptionButton(role, self)
        button.setProperty(PROP_TITLE_BUTTON, True)
        button.setProperty(PROP_TITLE_BUTTON_ROLE, role)
        button.setProperty("_breezeCaptionRole", role)
        button.setFixedSize(46, 40)
        button.setCursor(Qt.CursorShape.ArrowCursor)
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        return button

    def setTitle(self, title: str) -> None:
        self.titleLabel.setText(title)

    def setIcon(self, icon) -> None:
        self._titleIcon = icon
        self._titleThemedIcon = ThemedIcon(self._applyTitleIcon, size=self._titleIconSize.width())
        self._titleThemedIcon.set(icon)

    def _applyTitleIcon(self, icon: QIcon) -> None:
        pixmap = icon.pixmap(self._titleIconSize)
        self.iconLabel.setPixmap(pixmap)
        self.iconLabel.setVisible(not pixmap.isNull())

    def setWindowIcon(self, icon: QIcon) -> None:
        self._titleIcon = icon
        self._titleThemedIcon = None
        pixmap = icon.pixmap(self._titleIconSize)
        self.iconLabel.setPixmap(pixmap)
        self.iconLabel.setVisible(not pixmap.isNull())

    def setBackButtonVisible(self, visible: bool) -> None:
        self.backButton.setVisible(visible)

    def setBackButtonIcon(self, icon) -> None:
        self.backButton._breezeThemedIcon.set(icon)  # type: ignore[attr-defined]

    def addWidget(self, widget: QWidget, stretch: int = 0) -> QWidget:
        widget.setParent(self)
        self._customLayout.addWidget(widget, stretch)
        return widget

    def addActionButton(self, icon, tooltip: str = "", callback: Callable[[], None] | None = None) -> QToolButton:
        button = self._createButton("", TITLE_BUTTON_ROLE_ACTION, icon, width=40)
        button.setToolTip(tooltip)
        if callback is not None:
            button.clicked.connect(callback)
        self._customLayout.addWidget(button)
        self._actionButtons.append(button)
        return button

    def refreshTheme(self) -> None:
        self.minButton.update()
        self.maxButton.update()
        self.closeButton.update()
        self._refreshButtonIcon(self.backButton)
        for button in self._actionButtons:
            self._refreshButtonIcon(button)
        if self._titleThemedIcon is not None:
            self._titleThemedIcon.refresh()

    def _refreshButtonIcon(self, button: QToolButton) -> None:
        themed_icon = getattr(button, "_breezeThemedIcon", None)
        if themed_icon is not None:
            themed_icon.refresh()

    def syncWindowState(self) -> None:
        role = TITLE_BUTTON_ROLE_RESTORE if self.window().isMaximized() else TITLE_BUTTON_ROLE_MAXIMIZE
        self.maxButton.setProperty(PROP_TITLE_BUTTON_ROLE, role)
        self.maxButton.setProperty("_breezeCaptionRole", role)
        self.maxButton.update()

    def toggleMaximized(self) -> None:
        window = self.window()
        if window.isMaximized():
            window.showNormal()
        else:
            window.showMaximized()
        self.syncWindowState()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragPosition = event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._dragPosition is not None and event.buttons() & Qt.MouseButton.LeftButton:
            window = self.window()
            if not window.isMaximized():
                window.move(event.globalPosition().toPoint() - self._dragPosition)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._dragPosition = None
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggleMaximized()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)
