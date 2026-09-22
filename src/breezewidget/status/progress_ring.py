"""Circular progress indicators (determinate + indeterminate)."""
from __future__ import annotations

from PySide6.QtCore import (
    Property,
    QPropertyAnimation,
    QRectF,
    QSize,
    Qt,
)
from PySide6.QtGui import QColor, QFontMetrics, QPainter, QPen
from PySide6.QtWidgets import QWidget

from ..theme import getPalette


def _ring_rect(widget: QWidget, stroke_width: int) -> QRectF:
    side = min(widget.width(), widget.height())
    margin = stroke_width / 2 + 1
    return QRectF(
        (widget.width() - side) / 2 + margin,
        (widget.height() - side) / 2 + margin,
        side - margin * 2,
        side - margin * 2,
    )


def _arc_pen(color: QColor, stroke_width: int, cap: Qt.PenCapStyle) -> QPen:
    pen = QPen(color)
    pen.setWidth(stroke_width)
    pen.setCapStyle(cap)
    return pen


def _paint_ring_track(painter: QPainter, rect: QRectF, color: QColor, stroke_width: int) -> None:
    painter.setPen(_arc_pen(color, stroke_width, Qt.PenCapStyle.FlatCap))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawArc(rect, 0, 360 * 16)


class ProgressRing(QWidget):
    """Circular determinate progress.

    Behaves like a circular ``QProgressBar``: set ``range`` + ``value``,
    optionally show the percentage in the centre via ``setTextVisible``.
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._minimum = 0
        self._maximum = 100
        self._value = 0
        self._stroke_width = 6
        self._text_visible = False
        self.setFixedSize(64, 64)

    def minimum(self) -> int:
        return self._minimum

    def maximum(self) -> int:
        return self._maximum

    def value(self) -> int:
        return self._value

    def setMinimum(self, minimum: int) -> None:
        self.setRange(int(minimum), self._maximum)

    def setMaximum(self, maximum: int) -> None:
        self.setRange(self._minimum, int(maximum))

    def setRange(self, minimum: int, maximum: int) -> None:
        minimum = int(minimum)
        maximum = int(maximum)
        if maximum < minimum:
            maximum = minimum
        self._minimum = minimum
        self._maximum = maximum
        if self._value < minimum:
            self._value = minimum
        elif self._value > maximum:
            self._value = maximum
        self.update()

    def setValue(self, value: int) -> None:
        value = max(self._minimum, min(self._maximum, int(value)))
        if value != self._value:
            self._value = value
            self.update()

    def setStrokeWidth(self, width: int) -> None:
        self._stroke_width = max(1, int(width))
        self.update()

    def strokeWidth(self) -> int:
        return self._stroke_width

    def setTextVisible(self, visible: bool) -> None:
        self._text_visible = bool(visible)
        self.update()

    def isTextVisible(self) -> bool:
        return self._text_visible

    def progress(self) -> float:
        span = self._maximum - self._minimum
        if span <= 0:
            return 0.0
        return (self._value - self._minimum) / span

    def sizeHint(self) -> QSize:
        return QSize(64, 64)

    def paintEvent(self, event) -> None:
        del event
        palette = getPalette()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        side = min(self.width(), self.height())
        rect = _ring_rect(self, self._stroke_width)
        _paint_ring_track(painter, rect, QColor(palette.surface5), self._stroke_width)

        sweep = int(round(self.progress() * 360 * 16))
        if sweep > 0:
            painter.setPen(_arc_pen(QColor(palette.primary4), self._stroke_width, Qt.PenCapStyle.RoundCap))
            painter.drawArc(rect, 90 * 16, -sweep)

        if self._text_visible:
            painter.setPen(QPen(QColor(palette.text1)))
            text = f"{int(self.progress() * 100)}%"
            font = self.font()
            font.setPointSizeF(max(9.0, side / 5.0))
            painter.setFont(font)
            metrics = QFontMetrics(font)
            painter.drawText(
                self.rect(),
                Qt.AlignmentFlag.AlignCenter,
                metrics.elidedText(text, Qt.TextElideMode.ElideRight, self.width()),
            )
        painter.end()


class IndeterminateProgressRing(QWidget):
    """Spinning ring with no fixed value — for unknown-duration work."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._stroke_width = 4
        self._angle = 0
        self._sweep = 100
        self.setFixedSize(28, 28)
        self._animation = QPropertyAnimation(self, b"angle", self)
        self._animation.setDuration(1400)
        self._animation.setStartValue(0)
        self._animation.setEndValue(360)
        self._animation.setLoopCount(-1)
        self._animation.start()

    def setStrokeWidth(self, width: int) -> None:
        self._stroke_width = max(1, int(width))
        self.update()

    def strokeWidth(self) -> int:
        return self._stroke_width

    def setSweepAngle(self, sweep: int) -> None:
        self._sweep = max(20, min(330, int(sweep)))
        self.update()

    def sweepAngle(self) -> int:
        return self._sweep

    def getAngle(self) -> int:
        return self._angle

    def setAngle(self, value: int) -> None:
        self._angle = int(value) % 360
        self.update()

    angle = Property(int, getAngle, setAngle)

    def start(self) -> None:
        if self._animation.state() != QPropertyAnimation.State.Running:
            self._animation.start()

    def stop(self) -> None:
        self._animation.stop()

    def isRunning(self) -> bool:
        return self._animation.state() == QPropertyAnimation.State.Running

    def hideEvent(self, event) -> None:
        self._animation.stop()
        super().hideEvent(event)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.start()

    def sizeHint(self) -> QSize:
        return QSize(28, 28)

    def paintEvent(self, event) -> None:
        del event
        palette = getPalette()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        rect = _ring_rect(self, self._stroke_width)
        _paint_ring_track(painter, rect, QColor(palette.surface5), self._stroke_width)
        painter.setPen(_arc_pen(QColor(palette.primary4), self._stroke_width, Qt.PenCapStyle.RoundCap))
        painter.drawArc(rect, (90 - self._angle) * 16, -self._sweep * 16)
        painter.end()
