import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextOption
from PySide6.QtWidgets import QStyleOptionViewItem, QTableWidgetItem
import breezewidget as bw


def make_table(qtbot, text="a" * 100):
    table = bw.TableWidget()
    qtbot.addWidget(table)
    table.setRowCount(2)
    table.setColumnCount(2)
    table.setItemDelegate(bw.RichTextTableItemDelegate(table))
    table.setColumnWidth(0, 150)
    table.setItem(0, 0, QTableWidgetItem(text))
    table.setItem(1, 0, QTableWidgetItem("x"))
    table.resize(420, 400)
    table.show()
    return table


def test_auto_height_wraps_grows_and_shrinks(qtbot):
    table = make_table(qtbot)
    table.setMinimumRowHeight(0, 72)
    table.setMinimumRowHeight(1, 36)
    table.setAutoRowHeightEnabled(True)
    qtbot.waitUntil(lambda: table.rowHeight(0) > 72)
    before = table.rowHeight(0)
    table.setColumnWidth(0, 80)
    qtbot.waitUntil(lambda: table.rowHeight(0) > before)
    table.item(0, 0).setText("short")
    qtbot.waitUntil(lambda: table.rowHeight(0) == 72)
    assert table.rowHeight(1) == 36
    table.setAutoRowHeightEnabled(False)
    table.item(0, 0).setText("line\n" * 20)
    qtbot.wait(30)
    assert table.rowHeight(0) == 72


def test_commit_observer_receives_coherent_roles(qtbot):
    table = make_table(qtbot, "Mathe Sport")
    delegate = table.itemDelegate()
    index = table.model().index(0, 0)
    option = QStyleOptionViewItem()
    option.widget = table
    option.rect = table.visualRect(index)
    editor = delegate.createEditor(table.viewport(), option, index)
    delegate.setEditorData(editor, index)
    segments = (bw.RichTextSegment("Math", "#ff0000"), bw.RichTextSegment("\n😀"))
    editor.setSegments(segments)
    observed = []
    delegate.modelUpdated.connect(lambda i: observed.append((i.data(Qt.EditRole), i.data(bw.RICH_TEXT_ROLE))))
    delegate.setModelData(editor, table.model(), index)
    assert observed == [("Math\n😀", segments)]
    assert index.data(Qt.DisplayRole) == "Math\n😀"


def test_invalid_metadata_loads_plain_text(qtbot):
    table = make_table(qtbot, "Plain")
    table.item(0, 0).setData(bw.RICH_TEXT_ROLE, (bw.RichTextSegment("wrong", "#ff0000"),))
    index = table.model().index(0, 0)
    editor = table.itemDelegate().createEditor(table.viewport(), QStyleOptionViewItem(), index)
    table.itemDelegate().setEditorData(editor, index)
    assert editor.segments() == (bw.RichTextSegment("Plain"),)


def test_default_table_remains_opt_out(qtbot):
    table = bw.TableWidget()
    qtbot.addWidget(table)
    table.setRowCount(1)
    table.setColumnCount(1)
    table.setRowHeight(0, 42)
    table.setItem(0, 0, QTableWidgetItem("long " * 100))
    qtbot.wait(20)
    assert type(table.itemDelegate()) is bw.TableItemDelegate
    assert not table.isAutoRowHeightEnabled()
    assert table.rowHeight(0) == 42
