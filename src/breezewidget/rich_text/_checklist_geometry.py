"""Document coordinates shared by native marker hit-testing and painting."""
from PySide6.QtCore import QPointF, Qt

from ._blocks import _checked


def _document_origin(document, rect, alignment):
    y = rect.top()
    spare = max(0, rect.height() - document.size().height())
    if alignment & Qt.AlignmentFlag.AlignBottom:
        y += spare
    elif alignment & Qt.AlignmentFlag.AlignVCenter:
        y += spare / 2
    return QPointF(rect.left(), y)


def _marker_at(document, point):
    # Qt's public API (available since before our Qt 6.6 floor) owns marker
    # geometry, including text direction, font, wrapping and paint-device DPI.
    block = document.documentLayout().blockWithMarkerAt(point)
    return block if block.isValid() and _checked(block) is not None else None
