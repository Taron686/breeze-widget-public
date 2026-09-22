from __future__ import annotations

from PySide6.QtCore import Property, Qt, Signal
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPainterPath
from PySide6.QtWidgets import QFrame, QSizePolicy, QWidget

from ..constants import CARD_DEFAULT, CARD_ELEVATED, PROP_CARD
from ..theme import isDarkTheme


class CardWidget(QFrame):
    clicked = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setProperty(PROP_CARD, CARD_DEFAULT)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        self.setMouseTracking(True)
        self._is_click_enabled = False
        self._is_hover = False
        self._is_pressed = False
        self._border_radius = 5

    def setClickEnabled(self, is_enabled: bool) -> None:
        self._is_click_enabled = is_enabled
        self.update()

    def isClickEnabled(self) -> bool:
        return self._is_click_enabled

    def getBorderRadius(self) -> int:
        return self._border_radius

    def setBorderRadius(self, radius: int) -> None:
        self._border_radius = max(0, int(radius))
        self.update()

    def enterEvent(self, event) -> None:
        super().enterEvent(event)
        self._is_hover = True
        self.update()

    def leaveEvent(self, event) -> None:
        super().leaveEvent(event)
        self._is_hover = False
        self._is_pressed = False
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_pressed = True
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        was_pressed = self._is_pressed
        super().mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_pressed = False
            self.update()
            if was_pressed and self.rect().contains(event.position().toPoint()):
                self.clicked.emit()

    def _background_color(self) -> QColor:
        if isDarkTheme():
            alpha = 8 if self._is_pressed else 21 if self._is_hover else 13
            return QColor(255, 255, 255, alpha)
        alpha = 64 if (self._is_hover or self._is_pressed) else 170
        return QColor(255, 255, 255, alpha)

    def _top_border_color(self) -> QColor:
        if isDarkTheme():
            alpha = 18 if self._is_pressed else 13 if self._is_hover else 10
            return QColor(255, 255, 255, alpha)
        return QColor(0, 0, 0, 15)

    def _bottom_border_color(self) -> QColor:
        if not isDarkTheme() and self._is_hover and not self._is_pressed:
            return QColor(0, 0, 0, 27)
        return self._top_border_color()

    def paintEvent(self, event) -> None:
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        radius = self._border_radius
        diameter = radius * 2

        path = QPainterPath()
        path.arcMoveTo(1, height - diameter - 1, diameter, diameter, 240)
        path.arcTo(1, height - diameter - 1, diameter, diameter, 225, -60)
        path.lineTo(1, radius)
        path.arcTo(1, 1, diameter, diameter, -180, -90)
        path.lineTo(width - radius, 1)
        path.arcTo(width - diameter - 1, 1, diameter, diameter, 90, -90)
        path.lineTo(width - 1, height - radius)
        path.arcTo(width - diameter - 1, height - diameter - 1, diameter, diameter, 0, -60)
        painter.strokePath(path, self._top_border_color())

        path = QPainterPath()
        path.arcMoveTo(1, height - diameter - 1, diameter, diameter, 240)
        path.arcTo(1, height - diameter - 1, diameter, diameter, 240, 30)
        path.lineTo(width - radius - 1, height - 1)
        path.arcTo(width - diameter - 1, height - diameter - 1, diameter, diameter, 270, 30)
        painter.strokePath(path, self._bottom_border_color())

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._background_color())
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), radius, radius)
        painter.end()

    borderRadius = Property(int, getBorderRadius, setBorderRadius)


class SimpleCardWidget(CardWidget):
    pass


class ElevatedCardWidget(CardWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setProperty(PROP_CARD, CARD_ELEVATED)
