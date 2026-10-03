import pytest
from PySide6.QtWidgets import QStyleOptionViewItem, QTableWidgetItem

from breezewidget import TableWidget, RichTextTableItemDelegate


def span_table(qtbot, grid=False):
    table = TableWidget()
    qtbot.addWidget(table)
    table.setRowCount(1)
    table.setColumnCount(3)
    table.setShowGrid(grid)
    for column in range(3):
        table.setColumnWidth(column, 100)
    table.setItem(0, 0, QTableWidgetItem('a' * 100))
    table.setItemDelegate(RichTextTableItemDelegate(table))
    table.resize(400, 400)
    table.show()
    return table


def rendered_height(table):
    index = table.model().index(0, 0)
    option = QStyleOptionViewItem()
    table.initViewItemOption(option)
    option.rect = table.visualRect(index)
    return table.itemDelegateForIndex(index).sizeHint(option, index).height() + int(table.showGrid())


@pytest.mark.parametrize('grid', [False, True])
def test_auto_height_uses_horizontal_span_width(qtbot, grid):
    table = span_table(qtbot, grid)
    table.setSpan(0, 0, 1, 2)
    table.setAutoRowHeightEnabled(True)
    qtbot.waitUntil(lambda: table.rowHeight(0) == rendered_height(table))


def test_adding_and_clearing_span_reflows_enabled_auto_height(qtbot):
    table = span_table(qtbot)
    table.setAutoRowHeightEnabled(True)
    qtbot.waitUntil(lambda: table.rowHeight(0) == rendered_height(table))
    unspanned_height = table.rowHeight(0)
    table.setSpan(0, 0, 1, 2)
    qtbot.waitUntil(lambda: table.rowHeight(0) == rendered_height(table))
    assert table.rowHeight(0) < unspanned_height
    table.clearSpans()
    qtbot.waitUntil(lambda: table.rowHeight(0) == unspanned_height)


def test_covered_cell_text_does_not_drive_spanned_row_height(qtbot):
    table = span_table(qtbot)
    table.setItem(0, 1, QTableWidgetItem('\n'.join(['covered'] * 50)))
    table.setSpan(0, 0, 1, 2)
    table.setAutoRowHeightEnabled(True)
    qtbot.waitUntil(lambda: table.rowHeight(0) == rendered_height(table))
    table.clearSpans()
    qtbot.waitUntil(lambda: table.rowHeight(0) > rendered_height(table))


@pytest.mark.parametrize('hidden', [0, 1])
def test_span_width_tracks_hidden_anchor_or_covered_column(qtbot, hidden):
    table = span_table(qtbot)
    table.setSpan(0, 0, 1, 3)
    table.setAutoRowHeightEnabled(True)
    qtbot.waitUntil(lambda: table.rowHeight(0) == rendered_height(table))
    wide_height = table.rowHeight(0)
    table.hideColumn(hidden)
    qtbot.waitUntil(lambda: table.rowHeight(0) == rendered_height(table))
    assert table.rowHeight(0) > wide_height
    table.setMinimumRowHeight(0, 300)
    qtbot.waitUntil(lambda: table.rowHeight(0) == 300)
