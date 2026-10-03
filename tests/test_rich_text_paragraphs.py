import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QTextCursor
from PySide6.QtWidgets import QStyleOptionViewItem, QWidget

from breezewidget import RichTextEdit, RichTextSegment, RichTextTableItemDelegate, RICH_TEXT_ROLE


@pytest.mark.parametrize('segments', [
    (RichTextSegment('A\n', '#ff0000'), RichTextSegment('B', '#0000ff')),
    (RichTextSegment('\n', '#0000ff'), RichTextSegment('A', '#ff0000')),
    (RichTextSegment('A', '#ff0000'), RichTextSegment('\n', '#0000ff')),
    (RichTextSegment('A\n', '#ff0000'), RichTextSegment('\n', '#0000ff'), RichTextSegment('B')),
    (RichTextSegment('\n'), RichTextSegment('\n', '#ff0000'), RichTextSegment('\n', '#0000ff')),
    (RichTextSegment('A'), RichTextSegment('\n', '#ff0000'), RichTextSegment('B')),
])
@pytest.mark.parametrize('commit', [False, True], ids=['extract', 'no-op-commit'])
def test_paragraph_separator_colors_survive_roundtrip(qtbot, segments, commit):
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
        observed = []
        delegate.modelUpdated.connect(lambda i: observed.append(i.data(RICH_TEXT_ROLE)))
        delegate.setModelData(editor, model, index)
        assert observed == [segments]
        assert index.data(Qt.EditRole) == text
    else:
        assert editor.segments() == segments
        assert editor.plainText() == text


@pytest.mark.parametrize('text,start,end', [('A\nB', 1, 2), ('\nA', 0, 1), ('A\n', 1, 2), ('A\n\nB', 1, 3)])
def test_coloring_only_paragraph_separators_is_one_undo_step(qtbot, text, start, end):
    editor = RichTextEdit()
    qtbot.addWidget(editor)
    original = (RichTextSegment(text),)
    editor.setSegments(original)
    cursor = editor.textCursor()
    cursor.setPosition(start)
    cursor.setPosition(end, QTextCursor.KeepAnchor)
    editor.setTextCursor(cursor)
    editor.applyTextColor('#ff0000')
    expected = tuple(segment for segment in (
        RichTextSegment(text[:start]), RichTextSegment(text[start:end], '#ff0000'), RichTextSegment(text[end:])
    ) if segment.text)
    assert editor.segments() == expected
    editor.undo()
    assert editor.segments() == original
    editor.redo()
    assert editor.segments() == expected
