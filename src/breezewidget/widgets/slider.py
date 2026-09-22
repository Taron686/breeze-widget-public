from __future__ import annotations

from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import QSlider, QStyle, QStyleOptionSlider, QWidget

from ..theme import getPalette


class Slider(QSlider):
    HANDLE_DIAMETER = 16
    GROOVE_THICKNESS = 4

    def __init__(self, orientation: Qt.Orientation = Qt.Orientation.Horizontal, parent: QWidget | None = None):
        super().__init__(orientation, parent)
        if orientation == Qt.Orientation.Horizontal:
            self.setMinimumHeight(self.sizeHint().height())
        else:
            self.setMinimumWidth(self.sizeHint().width())

    def sizeHint(self) -> QSize:
        if self.orientation() == Qt.Orientation.Horizontal:
            return QSize(160, 28)
        return QSize(28, 160)

    def paintEvent(self, event) -> None:
        del event
        palette = getPalette()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(Qt.PenStyle.NoPen)

        groove, handle = self._sliderRects()
        radius = self.GROOVE_THICKNESS / 2

        painter.setBrush(QColor(palette.border1))
        painter.drawRoundedRect(groove, radius, radius)

        painter.setBrush(QColor(palette.primary4))
        option = QStyleOptionSlider()
        self.initStyleOption(option)
        if self.orientation() == Qt.Orientation.Horizontal:
            fill = QRectF(groove.left(), groove.top(), handle.center().x() - groove.left(), groove.height())
        else:
            fill = QRectF(groove.left(), handle.center().y(), groove.width(), groove.bottom() - handle.center().y())
        if self.orientation() == Qt.Orientation.Horizontal and option.upsideDown:
            fill = QRectF(handle.center().x(), groove.top(), groove.right() - handle.center().x(), groove.height())
        elif self.orientation() == Qt.Orientation.Vertical and not option.upsideDown:
            fill = QRectF(groove.left(), groove.top(), groove.width(), handle.center().y() - groove.top())
        painter.drawRoundedRect(fill.normalized(), radius, radius)

        painter.setPen(QPen(QColor(palette.surface2), 2))
        painter.setBrush(QColor(palette.primary4))
        painter.drawEllipse(handle)
        painter.end()

    def _sliderRects(self) -> tuple[QRectF, QRectF]:
        option = QStyleOptionSlider()
        self.initStyleOption(option)
        style = self.style()
        def center_at(position):
            option.sliderPosition = position
            return QRectF(style.subControlRect(
                QStyle.ComplexControl.CC_Slider, option,
                QStyle.SubControl.SC_SliderHandle, self,
            )).center()
        center = center_at(self.sliderPosition())
        first = center_at(self.minimum())
        last = center_at(self.maximum())
        if self.orientation() == Qt.Orientation.Horizontal:
            groove = QRectF(min(first.x(), last.x()), center.y() - self.GROOVE_THICKNESS / 2,
                            abs(last.x() - first.x()), self.GROOVE_THICKNESS)
        else:
            groove = QRectF(center.x() - self.GROOVE_THICKNESS / 2, min(first.y(), last.y()),
                            self.GROOVE_THICKNESS, abs(last.y() - first.y()))
        handle = QRectF(center.x() - self.HANDLE_DIAMETER / 2,
                        center.y() - self.HANDLE_DIAMETER / 2,
                        self.HANDLE_DIAMETER, self.HANDLE_DIAMETER)
        return groove, handle


class ClickableSlider(Slider):
    def __init__(self, orientation: Qt.Orientation = Qt.Orientation.Horizontal, parent: QWidget | None = None):
        super().__init__(orientation, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._setValueFromPosition(event.position().toPoint())
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() & Qt.MouseButton.LeftButton:
            self._setValueFromPosition(event.position().toPoint())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def _setValueFromPosition(self, position) -> None:
        option = QStyleOptionSlider()
        self.initStyleOption(option)
        groove, _ = self._sliderRects()
        horizontal = self.orientation() == Qt.Orientation.Horizontal
        span = max(1, round(groove.width() if horizontal else groove.height()))
        offset = position.x() - groove.left() if horizontal else position.y() - groove.top()
        self.setValue(QStyle.sliderValueFromPosition(
            self.minimum(), self.maximum(), max(0, min(span, round(offset))),
            span, option.upsideDown,
        ))
