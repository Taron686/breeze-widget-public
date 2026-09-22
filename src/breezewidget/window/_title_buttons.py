from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QToolButton, QWidget

from ..constants import (
    PROP_TITLE_BUTTON_ROLE,
    TITLE_BUTTON_ROLE_CLOSE,
    TITLE_BUTTON_ROLE_MINIMIZE,
    TITLE_BUTTON_ROLE_RESTORE,
)
from ..icons._themed import default_icon_color
from ..theme import getPalette


class _TitleButton(QToolButton):
    def enterEvent(self, event) -> None:
        super().enterEvent(event)
        self._refreshThemedIcon()

    def leaveEvent(self, event) -> None:
        super().leaveEvent(event)
        self._refreshThemedIcon()

    def _refreshThemedIcon(self) -> None:
        themed_icon = getattr(self, "_breezeThemedIcon", None)
        if themed_icon is not None:
            themed_icon.refresh()


class _CaptionButton(QToolButton):
    _GLYPH_SIZE = 10.0
    _RESTORE_OFFSET = 3.0
    _STROKE_WIDTH = 1.2

    def __init__(self, role: str, parent: QWidget | None = None):
        super().__init__(parent)
        self._role = role

    def paintEvent(self, event) -> None:
        del event
        palette = getPalette()
        role = str(self.property(PROP_TITLE_BUTTON_ROLE) or self._role)
        hovered = self.underMouse()

        if role == TITLE_BUTTON_ROLE_CLOSE and hovered:
            background = QColor(palette.danger1)
            glyph = QColor(palette.danger_text)
        elif self.isDown():
            background = QColor(palette.chrome_pressed)
            glyph = QColor(default_icon_color())
        elif hovered:
            background = QColor(palette.chrome_hover)
            glyph = QColor(default_icon_color())
        else:
            background = QColor(0, 0, 0, 0)
            glyph = QColor(default_icon_color())

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(background)
        painter.drawRect(self.rect())

        pen = QPen(glyph, self._STROKE_WIDTH)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        if role == TITLE_BUTTON_ROLE_MINIMIZE:
            self._paintMinimize(painter)
        elif role == TITLE_BUTTON_ROLE_RESTORE:
            self._paintRestore(painter)
        elif role == TITLE_BUTTON_ROLE_CLOSE:
            self._paintClose(painter)
        else:
            self._paintMaximize(painter)
        painter.end()

    def enterEvent(self, event) -> None:
        super().enterEvent(event)
        self.update()

    def leaveEvent(self, event) -> None:
        super().leaveEvent(event)
        self.update()

    def mousePressEvent(self, event) -> None:
        super().mousePressEvent(event)
        self.update()

    def mouseReleaseEvent(self, event) -> None:
        super().mouseReleaseEvent(event)
        self.update()

    def _glyphRect(self, size: float | None = None) -> QRectF:
        size = self._GLYPH_SIZE if size is None else float(size)
        return QRectF(
            (self.width() - size) / 2,
            (self.height() - size) / 2,
            size,
            size,
        )

    def _paintMinimize(self, painter: QPainter) -> None:
        rect = self._glyphRect()
        y = rect.center().y()
        painter.drawLine(rect.left(), y, rect.right(), y)

    def _paintMaximize(self, painter: QPainter) -> None:
        painter.drawRect(self._glyphRect())

    def _paintRestore(self, painter: QPainter) -> None:
        extent = self._GLYPH_SIZE + self._RESTORE_OFFSET
        base = self._glyphRect(extent)
        back = QRectF(
            base.left() + self._RESTORE_OFFSET,
            base.top(),
            self._GLYPH_SIZE,
            self._GLYPH_SIZE,
        )
        front = QRectF(
            base.left(),
            base.top() + self._RESTORE_OFFSET,
            self._GLYPH_SIZE,
            self._GLYPH_SIZE,
        )
        painter.drawRect(back)
        painter.drawRect(front)

    def _paintClose(self, painter: QPainter) -> None:
        rect = self._glyphRect()
        painter.drawLine(rect.topLeft(), rect.bottomRight())
        painter.drawLine(rect.topRight(), rect.bottomLeft())
