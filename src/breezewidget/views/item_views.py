"""Breeze-styled item views — `ListView`, `TableView`, `TreeView`."""
from __future__ import annotations

from PySide6.QtWidgets import QListView, QTableView, QTreeView, QWidget

from ..constants import PROP_ITEM_VIEW
from .table_widget import TableItemDelegate


class ListView(QListView):
    """Breeze-styled :class:`QListView` (alternating rows, rounded selection)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty(PROP_ITEM_VIEW, "list")
        self.setAlternatingRowColors(True)
        self.setUniformItemSizes(True)


class TableView(QTableView):
    """Breeze-styled :class:`QTableView` (alternating rows, no grid lines)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty(PROP_ITEM_VIEW, "table")
        self.setAlternatingRowColors(True)
        self.setShowGrid(False)
        self.setMouseTracking(True)
        self.setItemDelegate(TableItemDelegate(self))
        if self.verticalHeader() is not None:
            self.verticalHeader().setVisible(False)


class TreeView(QTreeView):
    """Breeze-styled :class:`QTreeView` (alternating rows, animated, rounded)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty(PROP_ITEM_VIEW, "tree")
        self.setAlternatingRowColors(True)
        self.setAnimated(True)
