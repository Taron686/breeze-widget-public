from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from test_rich_text_interactions import editor_in_table


def test_clicking_another_cell_commits_once(qtbot):
    host, table, editor, other, delegate = editor_in_table(qtbot)
    commits = []
    delegate.modelUpdated.connect(lambda index: commits.append(index.data()))
    editor.setPlainText('new value')
    rect = table.visualItemRect(table.item(0, 1))
    qtbot.mouseClick(table.viewport(), Qt.LeftButton, pos=rect.center())
    qtbot.waitUntil(lambda: len(commits) == 1)
    assert commits == ['new value']
    qtbot.wait(20)
    assert len(commits) == 1


def test_escape_cancels_without_model_update(qtbot):
    host, table, editor, other, delegate = editor_in_table(qtbot)
    commits = []
    delegate.modelUpdated.connect(lambda index: commits.append(index.data()))
    editor.setPlainText('discard me')
    qtbot.keyClick(editor, Qt.Key_Escape)
    qtbot.wait(20)
    assert commits == []
    assert table.item(0, 0).text() == 'Mathe Sport'


def test_shift_tab_moves_to_previous_cell(qtbot):
    host, table, editor, other, delegate = editor_in_table(qtbot)
    qtbot.keyClick(editor, Qt.Key_Tab)
    qtbot.wait(20)
    from breezewidget import RichTextEdit
    editor = table.focusWidget()
    assert isinstance(editor, RichTextEdit)
    editor.setPlainText('changed second')
    qtbot.keyClick(editor, Qt.Key_Backtab)
    qtbot.wait(20)
    assert table.currentColumn() == 0
    assert table.item(0, 1).text() == 'changed second'
