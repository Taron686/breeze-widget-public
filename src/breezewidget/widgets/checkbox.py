from __future__ import annotations

from PySide6.QtCore import QPointF, QRect, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPaintEvent, QPen
from PySide6.QtWidgets import QAbstractButton, QCheckBox, QRadioButton

from ..theme import getPalette


_INDICATOR_SIZE = 18
_INDICATOR_SPACING = 8
_BORDER_WIDTH = 1.4
_RADIUS = 4.0


def _resolve_colors(checked: bool, hover: bool, enabled: bool):
    palette = getPalette()
    if not enabled:
        border = QColor(palette.border1)
        border.setAlphaF(0.45)
        return (
            QColor(palette.surface2),
            border,
            QColor(palette.text2),
            False,
        )
    if checked:
        return (
            QColor(palette.primary4),
            QColor(palette.primary4),
            QColor(palette.primary_text),
            True,
        )
    fill = QColor(palette.surface2 if hover else palette.surface1)
    return (
        fill,
        QColor(palette.border1),
        QColor(palette.text1),
        False,
    )


def _indicator_rect(widget: QAbstractButton) -> QRectF:
    rect = widget.rect()
    indicator_y = (rect.height() - _INDICATOR_SIZE) // 2
    return QRectF(0, indicator_y, _INDICATOR_SIZE, _INDICATOR_SIZE).adjusted(
        _BORDER_WIDTH / 2,
        _BORDER_WIDTH / 2,
        -_BORDER_WIDTH / 2,
        -_BORDER_WIDTH / 2,
    )


def _text_rect(widget: QAbstractButton) -> QRect:
    rect = widget.rect()
    return QRect(
        _INDICATOR_SIZE + _INDICATOR_SPACING,
        0,
        rect.width() - _INDICATOR_SIZE - _INDICATOR_SPACING,
        rect.height(),
    )


def _paint_text(painter: QPainter, widget: QAbstractButton, enabled: bool) -> None:
    if not widget.text():
        return
    text_color = QColor(getPalette().text1)
    if not enabled:
        text_color.setAlphaF(0.55)
    painter.setPen(text_color)
    painter.drawText(
        _text_rect(widget),
        int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft),
        widget.text(),
    )


class _ChoiceRepaintMixin:
    def sizeHint(self):  # noqa: D401
        hint = super().sizeHint()
        hint.setHeight(max(hint.height(), _INDICATOR_SIZE + 4))
        return hint

    def enterEvent(self, event):  # noqa: D401
        super().enterEvent(event)
        self.update()

    def leaveEvent(self, event):  # noqa: D401
        super().leaveEvent(event)
        self.update()


class CheckBox(_ChoiceRepaintMixin, QCheckBox):
    """Repainted check box with square indicator and Breeze theme colors.

    Supports two-state and three-state (PartiallyChecked) modes -- the
    indeterminate state renders a horizontal bar instead of a check glyph.
    """

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: D401
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        state = self.checkState()
        enabled = self.isEnabled()
        hover = self.underMouse() and enabled
        checked = state != Qt.CheckState.Unchecked
        fill, border, glyph, _ = _resolve_colors(checked, hover, enabled)
        indicator = _indicator_rect(self)

        painter.setPen(QPen(border, _BORDER_WIDTH))
        painter.setBrush(fill)
        painter.drawRoundedRect(indicator, _RADIUS, _RADIUS)

        if state == Qt.CheckState.Checked:
            self._paintCheck(painter, indicator, glyph)
        elif state == Qt.CheckState.PartiallyChecked:
            self._paintPartial(painter, indicator, glyph)

        _paint_text(painter, self, enabled)

    def _paintCheck(self, painter: QPainter, rect: QRectF, color: QColor) -> None:
        pen = QPen(
            color,
            2.0,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
            Qt.PenJoinStyle.RoundJoin,
        )
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        path = QPainterPath()
        path.moveTo(rect.left() + rect.width() * 0.22, rect.top() + rect.height() * 0.55)
        path.lineTo(rect.left() + rect.width() * 0.43, rect.top() + rect.height() * 0.74)
        path.lineTo(rect.left() + rect.width() * 0.78, rect.top() + rect.height() * 0.30)
        painter.drawPath(path)

    def _paintPartial(self, painter: QPainter, rect: QRectF, color: QColor) -> None:
        pen = QPen(color, 2.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        y = rect.center().y()
        painter.drawLine(
            QPointF(rect.left() + rect.width() * 0.25, y),
            QPointF(rect.right() - rect.width() * 0.25, y),
        )


class RadioButton(_ChoiceRepaintMixin, QRadioButton):
    """Repainted radio button with circular indicator."""

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: D401
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        enabled = self.isEnabled()
        hover = self.underMouse() and enabled
        checked = self.isChecked()
        fill, border, glyph, _ = _resolve_colors(checked, hover, enabled)
        indicator = _indicator_rect(self)

        painter.setPen(QPen(border, _BORDER_WIDTH))
        painter.setBrush(fill)
        painter.drawEllipse(indicator)

        if checked:
            inner = indicator.adjusted(
                indicator.width() * 0.28,
                indicator.height() * 0.28,
                -indicator.width() * 0.28,
                -indicator.height() * 0.28,
            )
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(glyph)
            painter.drawEllipse(inner)

        _paint_text(painter, self, enabled)
