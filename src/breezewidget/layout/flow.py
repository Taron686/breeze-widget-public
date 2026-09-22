from __future__ import annotations

from PySide6.QtCore import QPoint, QRect, QSize, Qt
from PySide6.QtWidgets import QLayout, QLayoutItem, QWidget


class FlowLayout(QLayout):
    """Left-to-right wrapping layout.

    Items are placed in rows; when a row's width is exceeded the next item
    wraps to a new row.  Hidden widgets are skipped so showing/hiding children
    causes an automatic reflow.

    Usage::

        layout = FlowLayout(parent_widget, h_spacing=8, v_spacing=8)
        layout.addWidget(PushButton("A"))
        layout.addWidget(PushButton("B"))
        layout.addWidget(PushButton("C"))
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        h_spacing: int = 8,
        v_spacing: int = 8,
    ) -> None:
        super().__init__(parent)
        self._items: list[QLayoutItem] = []
        self._h_spacing = h_spacing
        self._v_spacing = v_spacing

    # ------------------------------------------------------------------
    # Spacing API
    # ------------------------------------------------------------------

    def setHorizontalSpacing(self, px: int) -> None:
        self._h_spacing = px
        self.invalidate()

    def setVerticalSpacing(self, px: int) -> None:
        self._v_spacing = px
        self.invalidate()

    def horizontalSpacing(self) -> int:
        return self._h_spacing

    def verticalSpacing(self) -> int:
        return self._v_spacing

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    def addWidget(self, widget: QWidget) -> None:  # type: ignore[override]
        # QLayout.addWidget reparents the widget then calls self.addItem.
        super().addWidget(widget)

    # ------------------------------------------------------------------
    # Required QLayout overrides
    # ------------------------------------------------------------------

    def addItem(self, item: QLayoutItem) -> None:  # type: ignore[override]
        # Do NOT call super().addItem() — PySide6 raises NotImplementedError.
        self._items.append(item)

    def count(self) -> int:
        return len(self._items)

    def itemAt(self, index: int) -> QLayoutItem | None:
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index: int) -> QLayoutItem | None:
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self) -> Qt.Orientation:
        # Does not request extra space in either direction.
        return Qt.Orientation(0)

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width: int) -> int:
        return self._doLayout(QRect(0, 0, width, 0), test_only=True)

    def setGeometry(self, rect: QRect) -> None:
        super().setGeometry(rect)
        # contentsRect() accounts for contentsMargins.
        self._doLayout(self.contentsRect(), test_only=False)

    def sizeHint(self) -> QSize:
        if not self._items:
            return QSize(0, 0)
        size = QSize(0, 0)
        for item in self._items:
            size = size.expandedTo(item.sizeHint())
        m = self.contentsMargins()
        return size + QSize(m.left() + m.right(), m.top() + m.bottom())

    def minimumSize(self) -> QSize:
        if not self._items:
            return QSize(0, 0)
        size = QSize(0, 0)
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        m = self.contentsMargins()
        return size + QSize(m.left() + m.right(), m.top() + m.bottom())

    # ------------------------------------------------------------------
    # Core layout algorithm
    # ------------------------------------------------------------------

    def _doLayout(self, rect: QRect, *, test_only: bool) -> int:
        """Compute (and optionally apply) item positions.

        Returns the total height required to lay out all visible items
        within *rect.width()*.  When *test_only* is ``False``, each
        item's geometry is also updated.
        """
        x = rect.x()
        y = rect.y()
        row_height = 0

        for item in self._items:
            if item.isEmpty():
                # Skip hidden widgets — they take no space.
                continue

            hint = item.sizeHint()
            item_w = hint.width()
            item_h = hint.height()

            next_x = x + item_w + self._h_spacing

            # Wrap to a new row when the item would exceed the right edge,
            # but only if at least one item is already on the current row
            # (row_height > 0).  Without this guard a single item wider than
            # the available width would cause an infinite wrap loop.
            if next_x - self._h_spacing > rect.right() and row_height > 0:
                x = rect.x()
                y += row_height + self._v_spacing
                next_x = x + item_w + self._h_spacing
                row_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), hint))

            x = next_x
            row_height = max(row_height, item_h)

        return y + row_height - rect.y()
