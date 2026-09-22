from __future__ import annotations

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QSizePolicy, QWidget

from ..theme import ThemeManager, getPalette


class PipsPager(QWidget):
    """Row of circular navigation dots indicating the current page.

    The active dot is rendered in the accent colour at a slightly larger
    diameter.  Clicking a dot emits ``currentChanged(index)``.

    Usage::

        pager = PipsPager()
        pager.setPageCount(5)
        pager.setCurrentIndex(0)
        pager.currentChanged.connect(flip_view.setCurrentIndex)
    """

    currentChanged = Signal(int)

    _DOT_ACTIVE = 8      # diameter of the active dot in px
    _DOT_INACTIVE = 6    # diameter of inactive dots in px
    _SPACING = 8         # gap between dot slots (slot width = _DOT_ACTIVE)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._page_count = 0
        self._current = 0
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        ThemeManager.instance().themeChanged.connect(self.update)
        ThemeManager.instance().themeColorChanged.connect(self.update)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def setPageCount(self, count: int) -> None:
        """Set the total number of pages (dots)."""
        self._page_count = max(0, count)
        if self._current >= self._page_count:
            self._current = max(0, self._page_count - 1)
        self.updateGeometry()
        self.update()

    def pageCount(self) -> int:
        return self._page_count

    def setCurrentIndex(self, index: int) -> None:
        """Navigate to *index*.  Emits ``currentChanged`` when the index changes."""
        if 0 <= index < self._page_count and index != self._current:
            self._current = index
            self.currentChanged.emit(index)
            self.update()

    def currentIndex(self) -> int:
        return self._current

    # ------------------------------------------------------------------
    # Size
    # ------------------------------------------------------------------

    def sizeHint(self) -> QSize:
        if self._page_count == 0:
            return QSize(0, self._DOT_ACTIVE)
        slots = self._page_count
        w = slots * self._DOT_ACTIVE + max(0, slots - 1) * self._SPACING
        return QSize(w, self._DOT_ACTIVE)

    def minimumSizeHint(self) -> QSize:
        return self.sizeHint()

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            idx = self._indexAt(event.position().toPoint().x())
            if idx >= 0:
                self.setCurrentIndex(idx)
        super().mousePressEvent(event)

    def paintEvent(self, event) -> None:  # noqa: ARG002
        if self._page_count == 0:
            return

        palette = getPalette()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        start_x = self._startX()
        cy = self.height() // 2

        for i in range(self._page_count):
            slot_x = start_x + i * (self._DOT_ACTIVE + self._SPACING)
            if i == self._current:
                d = self._DOT_ACTIVE
                ox = 0
                color = QColor(palette.primary4)
            else:
                d = self._DOT_INACTIVE
                ox = (self._DOT_ACTIVE - d) // 2  # centre within the slot
                color = QColor(palette.border1)

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(color)
            r = d // 2
            painter.drawEllipse(slot_x + ox, cy - r, d, d)

        painter.end()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _startX(self) -> int:
        """Left edge of the first dot slot, centred in the widget."""
        if self._page_count == 0:
            return 0
        total = self._page_count * self._DOT_ACTIVE + max(0, self._page_count - 1) * self._SPACING
        return (self.width() - total) // 2

    def _indexAt(self, x: int) -> int:
        """Return the dot index under pixel *x*, or ``-1`` if none."""
        start = self._startX()
        for i in range(self._page_count):
            slot_x = start + i * (self._DOT_ACTIVE + self._SPACING)
            if slot_x <= x <= slot_x + self._DOT_ACTIVE:
                return i
        return -1
