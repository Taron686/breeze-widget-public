from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QTextCursor
from PySide6.QtWidgets import QStyleOptionViewItem, QWidget

from breezewidget import RichTextEdit, RichTextSegment, RichTextTableItemDelegate, RICH_TEXT_ROLE


def test_custom_role_roundtrip_and_rejected_update_does_not_signal(qtbot):
    class Model(QStandardItemModel):
        reject = False

        def setItemData(self, index, values):
            if self.reject:
                return False
            return super().setItemData(index, values)

    model = Model(1, 1)
    index = model.index(0, 0)
    model.setData(index, 'A😀\n\nB\u2028C\u00a0 ', Qt.EditRole)
    role = int(Qt.UserRole) + 50
    segments = (RichTextSegment('A😀\n', '#ff0000'), RichTextSegment('\nB\u2028C\u00a0 '))
    model.setData(index, segments, role)
    parent = QWidget()
    qtbot.addWidget(parent)
    delegate = RichTextTableItemDelegate(parent, richTextRole=role)
    editor = delegate.createEditor(parent, QStyleOptionViewItem(), index)
    delegate.setEditorData(editor, index)
    assert editor.segments() == segments
    updated = []
    delegate.modelUpdated.connect(lambda i: updated.append(i.data(role)))
    delegate.setModelData(editor, model, index)
    assert updated == [segments]
    assert index.data(RICH_TEXT_ROLE) is None
    model.reject = True
    editor.setPlainText('changed')
    delegate.setModelData(editor, model, index)
    assert updated == [segments]
    assert index.data(Qt.EditRole) == 'A😀\n\nB\u2028C\u00a0 '


def test_multi_paragraph_color_edit_preserves_blank_lines_and_emoji(qtbot):
    editor = RichTextEdit()
    qtbot.addWidget(editor)
    editor.setSegments((RichTextSegment('😀\n\nA\u2028B\u00a0'),))
    editor.selectAll()
    editor.applyTextColor('#800080')
    assert editor.segments() == (RichTextSegment('😀\n\nA\u2028B\u00a0', '#800080'),)
    editor.undo()
    assert editor.segments() == (RichTextSegment('😀\n\nA\u2028B\u00a0'),)
