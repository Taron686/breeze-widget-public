import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import QStyleOptionViewItem, QTableWidgetItem, QWidget

from breezewidget import RichTextSegment, RichTextTableItemDelegate, RICH_TEXT_ROLE, TableWidget


@pytest.mark.parametrize('segments', [
    (RichTextSegment('e', '#ff0000'), RichTextSegment('\u0301', '#0000ff')),
    (RichTextSegment('\U0001f469', '#ff0000'), RichTextSegment('\u200d\U0001f4bb', '#0000ff')),
])
@pytest.mark.parametrize('commit', [False, True], ids=['extract', 'no-op-commit'])
def test_grapheme_internal_colors_survive_roundtrip(qtbot, segments, commit):
    model = QStandardItemModel(1, 1)
    index = model.index(0, 0)
    text = ''.join(segment.text for segment in segments)
    model.setItemData(index, {int(Qt.EditRole): text, RICH_TEXT_ROLE: segments})
    parent = QWidget()
    qtbot.addWidget(parent)
    delegate = RichTextTableItemDelegate(parent)
    editor = delegate.createEditor(parent, QStyleOptionViewItem(), index)
    delegate.setEditorData(editor, index)
    if commit:
        delegate.setModelData(editor, model, index)
        actual = index.data(RICH_TEXT_ROLE)
        assert index.data(Qt.DisplayRole) == text
    else:
        actual = editor.segments()
    assert actual == segments
    assert ''.join(segment.text for segment in actual).encode('utf-8') == text.encode('utf-8')


def test_model_updated_tracks_edited_item_through_sort(qtbot):
    table = TableWidget()
    qtbot.addWidget(table)
    table.setRowCount(2)
    table.setColumnCount(1)
    edited = QTableWidgetItem('a')
    table.setItem(0, 0, edited)
    table.setItem(1, 0, QTableWidgetItem('b'))
    table.setSortingEnabled(True)
    table.sortItems(0, Qt.AscendingOrder)
    delegate = RichTextTableItemDelegate(table)
    table.setItemDelegate(delegate)
    index = table.indexFromItem(edited)
    editor = delegate.createEditor(table, QStyleOptionViewItem(), index)
    delegate.setEditorData(editor, index)
    segments = (RichTextSegment('z', '#ff0000'),)
    editor.setSegments(segments)
    observations = []
    delegate.modelUpdated.connect(lambda i: observations.append(
        (table.itemFromIndex(i), i.row(), i.data(Qt.DisplayRole), i.data(Qt.EditRole), i.data(RICH_TEXT_ROLE))))
    delegate.setModelData(editor, table.model(), index)
    assert table.item(1, 0) is edited
    assert observations == [(edited, 1, 'z', 'z', segments)]


@pytest.mark.parametrize('mutation', ['remove', 'reset'])
def test_model_updated_is_silent_if_commit_invalidates_item(qtbot, mutation):
    class InvalidatingModel(QStandardItemModel):
        def setItemData(self, index, values):
            accepted = super().setItemData(index, values)
            if mutation == 'remove':
                self.removeRow(index.row())
            else:
                self.clear()
            return accepted

    model = InvalidatingModel(1, 1)
    index = model.index(0, 0)
    parent = QWidget()
    qtbot.addWidget(parent)
    delegate = RichTextTableItemDelegate(parent)
    editor = delegate.createEditor(parent, QStyleOptionViewItem(), index)
    editor.setSegments((RichTextSegment('changed'),))
    observations = []
    delegate.modelUpdated.connect(observations.append)
    delegate.setModelData(editor, model, index)
    assert observations == []
