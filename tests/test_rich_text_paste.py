from PySide6.QtCore import QMimeData
from breezewidget import RichTextEdit, RichTextSegment


def test_html_only_paste_keeps_text_but_discards_formatting(qtbot):
    editor = RichTextEdit(cellMode=True)
    qtbot.addWidget(editor)
    mime = QMimeData()
    mime.setHtml('<b style="color:red">Plain</b><br>next')
    assert editor.canInsertFromMimeData(mime)
    editor.insertFromMimeData(mime)
    assert editor.segments() == (RichTextSegment('Plain\nnext'),)


def test_plain_mime_representation_takes_priority_over_html(qtbot):
    editor = RichTextEdit(cellMode=True)
    qtbot.addWidget(editor)
    mime = QMimeData()
    mime.setText('correct')
    mime.setHtml('<b>other</b>')
    editor.insertFromMimeData(mime)
    assert editor.plainText() == 'correct'
