"""Shared flat-chevron painter used by every widget that owns a dropdown."""
from __future__ import annotations

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPainter, QPen


def paint_chevron(
    painter: QPainter,
    cx: float,
    cy: float,
    half_size: float = 5.0,
    color: QColor | str = "#000000",
    stroke_width: float = 1.5,
    direction: str = "down",
) -> None:
    """Draw a flat V-chevron centred at (``cx``, ``cy``).

    ``direction`` accepts ``"down"`` (default) or ``"up"``. ``half_size`` is
    half of the chevron's horizontal span — the vertical drop is
    ``half_size / 2`` so the proportions match the Tabler ``chevron-down``
    asset. Drawing happens inside ``painter.save()`` / ``restore()`` so the
    caller's pen state is preserved.
    """
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    pen = QPen(
        QColor(color),
        float(stroke_width),
        Qt.PenStyle.SolidLine,
        Qt.PenCapStyle.RoundCap,
        Qt.PenJoinStyle.RoundJoin,
    )
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    drop = half_size / 2.0
    if direction == "up":
        painter.drawLine(
            QPointF(cx - half_size, cy + drop / 2),
            QPointF(cx, cy - drop),
        )
        painter.drawLine(
            QPointF(cx, cy - drop),
            QPointF(cx + half_size, cy + drop / 2),
        )
    else:
        painter.drawLine(
            QPointF(cx - half_size, cy - drop / 2),
            QPointF(cx, cy + drop),
        )
        painter.drawLine(
            QPointF(cx, cy + drop),
            QPointF(cx + half_size, cy - drop / 2),
        )
    painter.restore()
