from PySide6.QtCore import QEvent, QPoint, QTimer, Qt
from PySide6.QtGui import QContextMenuEvent, QTextCursor
from PySide6.QtWidgets import QApplication, QDialog, QLineEdit, QMenu, QVBoxLayout, QWidget, QTableWidgetItem
import pytest

from breezewidget import TableWidget, RichTextEdit, RichTextTableItemDelegate, RichTextSegment, RICH_TEXT_ROLE
from breezewidget.dialogs.color_dialog import ColorDialog


def editor_in_table(qtbot):
    host = QWidget()
    qtbot.addWidget(host)
    layout = QVBoxLayout(host)
    table = TableWidget()
    layout.addWidget(table)
    other = QLineEdit()
    layout.addWidget(other)
    table.setRowCount(1)
    table.setColumnCount(2)
    table.setColumnWidth(0, 200)
    table.setRowHeight(0, 48)
    table.setItem(0, 0, QTableWidgetItem('Mathe Sport'))
    table.setItem(0, 1, QTableWidgetItem('next'))
    delegate = RichTextTableItemDelegate(table)
    table.setItemDelegate(delegate)
    host.resize(500, 240)
    host.show()
    host.activateWindow()
    qtbot.waitUntil(host.isActiveWindow)
    table.setCurrentCell(0, 0)
    table.editItem(table.item(0, 0))
    editor = table.findChild(RichTextEdit)
    editor.setFocus()
    qtbot.waitUntil(editor.hasFocus)
    cursor = editor.textCursor()
    cursor.setPosition(0)
    cursor.setPosition(5, QTextCursor.KeepAnchor)
    editor.setTextCursor(cursor)
    return host, table, editor, other, delegate


@pytest.mark.parametrize('accept', [True, False])
def test_real_submenu_custom_dialog_preserves_editor_then_commits_once(qtbot, accept):
    host, table, editor, other, delegate = editor_in_table(qtbot)
    commits = []
    delegate.modelUpdated.connect(lambda i: commits.append((i.data(), i.data(RICH_TEXT_ROLE))))
    errors = []
    dialogs_seen = []

    def dialog_action():
        try:
            dialog = QApplication.activeModalWidget()
            assert isinstance(dialog, ColorDialog)
            dialogs_seen.append(dialog)
            assert QApplication.activePopupWidget() is None
            assert editor.isFormattingPopupOpen()
            assert commits == []
            assert editor.textCursor().selectedText() == 'Mathe'
            dialog.setColor('#123456')
            dialog.accept() if accept else dialog.reject()
        except BaseException as exc:
            errors.append(exc)
            if QApplication.activeModalWidget():
                QApplication.activeModalWidget().reject()

    def menu_action():
        try:
            menu = QApplication.activePopupWidget()
            assert isinstance(menu, QMenu)
            submenu = menu.actions()[-1].menu()
            menu.setActiveAction(menu.actions()[-1])
            qtbot.keyClick(menu, Qt.Key_Right)
            qtbot.waitUntil(submenu.isVisible)
            assert commits == []
            QTimer.singleShot(20, dialog_action)
            qtbot.mouseClick(submenu, Qt.LeftButton, pos=submenu.actionGeometry(submenu.actions()[-1]).center())
            submenu.close()
            menu.close()
        except BaseException as exc:
            errors.append(exc)
            if QApplication.activePopupWidget():
                QApplication.activePopupWidget().close()

    QTimer.singleShot(20, menu_action)
    event = QContextMenuEvent(QContextMenuEvent.Mouse, QPoint(15, 15), editor.mapToGlobal(QPoint(15, 15)))
    QApplication.sendEvent(editor.viewport(), event)
    assert not errors, errors
    assert len(dialogs_seen) == 1
    qtbot.waitUntil(editor.hasFocus)
    assert editor.textCursor().selectedText() == 'Mathe'
    assert commits == []
    other.setFocus()
    qtbot.waitUntil(lambda: len(commits) == 1)
    expected = (RichTextSegment('Mathe', '#123456'), RichTextSegment(' Sport')) if accept else (RichTextSegment('Mathe Sport'),)
    assert commits == [('Mathe Sport', expected)]
    qtbot.wait(30)
    assert len(commits) == 1


def test_enter_is_newline_tab_commits_and_moves(qtbot):
    host, table, editor, other, delegate = editor_in_table(qtbot)
    commits = []
    delegate.modelUpdated.connect(lambda i: commits.append(i.data()))
    cursor = editor.textCursor()
    cursor.movePosition(QTextCursor.End)
    editor.setTextCursor(cursor)
    qtbot.keyClick(editor, Qt.Key_Return)
    qtbot.keyClicks(editor, 'new')
    assert commits == []
    qtbot.keyClick(editor, Qt.Key_Tab)
    qtbot.waitUntil(lambda: len(commits) == 1)
    assert commits == ['Mathe Sport\nnew']
    assert table.currentColumn() == 1
