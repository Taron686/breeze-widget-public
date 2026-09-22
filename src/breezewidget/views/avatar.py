"""Avatar — circular profile widget with image or initials fallback."""
from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QPainter,
    QPainterPath,
    QPixmap,
)
from PySide6.QtWidgets import QWidget

from ..constants import PROP_AVATAR
from ..theme import getPalette


class Avatar(QWidget):
    """Circular avatar.

    Shows the assigned :class:`QPixmap` clipped to a circle.  When no
    pixmap is set, renders a solid circle (palette accent) with the
    first letter of the configured name centered in white.

    Construct with ``Avatar(diameter, name="…", pixmap=…)``.  Mutate
    via :meth:`setPixmap`, :meth:`setName`, :meth:`setDiameter`.
    """

    def __init__(
        self,
        diameter: int = 40,
        name: str = "",
        pixmap: QPixmap | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setProperty(PROP_AVATAR, True)
        self._diameter = diameter
        self._name = name
        self._pixmap = pixmap if pixmap is not None and not pixmap.isNull() else None
        self.setFixedSize(diameter, diameter)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def setDiameter(self, diameter: int) -> None:
        self._diameter = max(8, diameter)
        self.setFixedSize(self._diameter, self._diameter)
        self.update()

    def diameter(self) -> int:
        return self._diameter

    def setName(self, name: str) -> None:
        self._name = name
        self.update()

    def name(self) -> str:
        return self._name

    def setPixmap(self, pixmap: QPixmap | None) -> None:
        if pixmap is None or pixmap.isNull():
            self._pixmap = None
        else:
            self._pixmap = pixmap
        self.update()

    def pixmap(self) -> QPixmap | None:
        return self._pixmap

    # ------------------------------------------------------------------
    # Painting
    # ------------------------------------------------------------------

    def paintEvent(self, event) -> None:
        del event
        rect = QRectF(0, 0, self._diameter, self._diameter)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        path = QPainterPath()
        path.addEllipse(rect)
        painter.setClipPath(path)

        if self._pixmap is not None:
            scaled = self._pixmap.scaled(
                self._diameter,
                self._diameter,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            x_offset = (scaled.width() - self._diameter) // 2
            y_offset = (scaled.height() - self._diameter) // 2
            painter.drawPixmap(0, 0, scaled, x_offset, y_offset, self._diameter, self._diameter)
        else:
            palette = getPalette()
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(palette.primary4)))
            painter.drawEllipse(rect)
            initial = (self._name.strip()[:1] or "?").upper()
            font = QFont(self.font())
            font.setPointSizeF(max(8, self._diameter * 0.4))
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(QColor(palette.primary_text))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, initial)

        painter.end()
