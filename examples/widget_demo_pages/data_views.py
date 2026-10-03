"""Data views (6) — ListView, TableView, TreeView, FlipView, CycleListWidget, Avatar."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPixmap, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QHBoxLayout, QTableWidgetItem, QWidget

from breezewidget import Avatar, CycleListWidget, FlipView, ListView, TableView, TreeView
from breezewidget import TableWidget, RichTextTableItemDelegate, RichTextSegment, RICH_TEXT_ROLE
from breezewidget import RichTextBlock, RICH_TEXT_BLOCKS_ROLE

from ._gallery import GalleryPage


def _solid_pixmap(color: str, size: int = 220) -> QPixmap:
    pm = QPixmap(size, size)
    pm.fill(QColor(color))
    return pm


class ViewsDemoPage(GalleryPage):
    """Phase 6 — ListView, TableView, TreeView, FlipView, CycleListWidget, Avatar."""

    def __init__(self):
        super().__init__("Data views", "breezewidget.views", "views")

        # ListView.
        list_view = ListView()
        list_view.setMinimumHeight(140)
        list_model = QStandardItemModel(list_view)
        for s in ("Apple", "Banana", "Cherry", "Date", "Elderberry"):
            list_model.appendRow(QStandardItem(s))
        list_view.setModel(list_model)
        self.addExample("ListView — alternating rows, rounded selection", list_view)

        # TableView.
        table = TableView()
        table.setMinimumHeight(160)
        table_model = QStandardItemModel(0, 3, table)
        table_model.setHorizontalHeaderLabels(["Name", "Status", "Owner"])
        for row in (
            ("Build", "OK", "CI"),
            ("Tests", "OK", "QA"),
            ("Deploy", "Pending", "Ops"),
        ):
            table_model.appendRow([QStandardItem(c) for c in row])
        table.setModel(table_model)
        table.horizontalHeader().setStretchLastSection(True)
        self.addExample("TableView — header, no grid lines", table)

        rich_table = TableWidget()
        rich_table.setRowCount(4)
        rich_table.setColumnCount(2)
        rich_table.setHorizontalHeaderLabels(["Editable rich text", "Notes"])
        rich_table.setColumnWidth(0, 150)
        rich_table.horizontalHeader().setStretchLastSection(True)
        rich_delegate = RichTextTableItemDelegate(rich_table)
        rich_delegate.setChecklistsEnabled(True)
        rich_table.setItemDelegate(rich_delegate)
        for row, text in enumerate((
            "Mathe Sport", "a" * 100,
            "\n".join(f"Line {number}" for number in range(1, 7)), "Short row",
        )):
            item = QTableWidgetItem(text)
            item.setTextAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            rich_table.setItem(row, 0, item)
            rich_table.setItem(row, 1, QTableWidgetItem("Select text → right-click → Text color"))
            rich_table.setMinimumRowHeight(row, 36 if row == 3 else 72)
        rich_table.item(0, 0).setData(RICH_TEXT_ROLE, (
            RichTextSegment("Mathe", "#008000"), RichTextSegment(" "),
            RichTextSegment("Sport", "#0000ff"),
        ))
        blocks = (
            RichTextBlock((RichTextSegment("Copy worksheets", "#008000"),), True),
            RichTextBlock((RichTextSegment("Preparation notes"),)),
            RichTextBlock((RichTextSegment("Inform parents about the upcoming exam", "#0000ff"),), False),
            RichTextBlock((RichTextSegment("a" * 100),), False),
        )
        rich_table.item(2, 0).setText("\n".join("".join(s.text for s in b.segments) for b in blocks))
        rich_table.item(2, 0).setData(RICH_TEXT_BLOCKS_ROLE, blocks)
        rich_table.item(2, 1).setText("Click task markers; right-click while editing to insert/remove/toggle")
        rich_table.setAutoRowHeightEnabled(True)
        rich_table.setMinimumHeight(360)
        self.addExample("Rich text and checklists — resize columns, click tasks, edit colors", rich_table)

        # TreeView.
        tree = TreeView()
        tree.setMinimumHeight(180)
        tree_model = QStandardItemModel(tree)
        tree_model.setHorizontalHeaderLabels(["Project"])
        root = QStandardItem("BreezeWidget")
        for child_text in ("widgets", "navigation", "dialogs", "media"):
            child = QStandardItem(child_text)
            child.appendRow(QStandardItem("…"))
            root.appendRow(child)
        tree_model.appendRow(root)
        tree.setModel(tree_model)
        tree.expandAll()
        self.addExample("TreeView — animated expand/collapse", tree)

        # FlipView.
        flip = FlipView()
        flip.setMinimumHeight(220)
        for color in ("#11d9f3", "#1f6feb", "#22c55e", "#f97316"):
            flip.addPixmap(_solid_pixmap(color, 200))
        self.addExample("FlipView — pixmap carousel with slide+fade", flip)

        # CycleListWidget.
        cycle = CycleListWidget([f"{h:02d}" for h in range(24)])
        cycle.setMaximumWidth(120)
        cycle.setMaximumHeight(160)
        self.addExample("CycleListWidget — list with wrap-around (try Up/Down)", cycle)

        # Avatars.
        avatars = QWidget()
        avatars_layout = QHBoxLayout(avatars)
        avatars_layout.setContentsMargins(0, 0, 0, 0)
        for name in ("Alice", "Bob", "Charlie", "Dora"):
            avatars_layout.addWidget(Avatar(48, name=name))
        avatars_layout.addStretch(1)
        self.addExample("Avatar — circular profile widget (initials fallback)", avatars)

        self.finish()
