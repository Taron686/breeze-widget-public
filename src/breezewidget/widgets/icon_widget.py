from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel, QWidget

from ..icons import icon_from


class IconWidget(QLabel):
    """Small icon display widget accepting Breeze icons, names, paths, and QIcon."""

    def __init__(self, icon=None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._icon = QIcon()
        self._iconSource = None
        self._iconSize = QSize(32, 32)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)
        self.setStyleSheet("background: transparent; border: none;")
        self.setFixedSize(self._iconSize)
        if icon is not None:
            self.setIcon(icon)

    def icon(self) -> QIcon:
        return QIcon(self._icon)

    def setIcon(self, icon) -> None:
        self._iconSource = icon
        self.refreshTheme()

    def refreshTheme(self) -> None:
        self._icon = icon_from(self._iconSource)
        self._updatePixmap()

    def setFixedSize(self, *args) -> None:
        super().setFixedSize(*args)
        size = self.size()
        if size.isValid():
            self._iconSize = QSize(size.width(), size.height())
            self._updatePixmap()

    def setIconSize(self, size: QSize) -> None:
        self._iconSize = QSize(size)
        self.setFixedSize(size)

    def iconSize(self) -> QSize:
        return QSize(self._iconSize)

    def _updatePixmap(self) -> None:
        if self._icon.isNull():
            self.clear()
            return
        self.setPixmap(self._icon.pixmap(self._iconSize))
