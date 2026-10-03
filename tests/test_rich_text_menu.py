from PySide6.QtCore import QPoint, QTimer, Qt
from PySide6.QtGui import QContextMenuEvent
from PySide6.QtWidgets import QApplication
import pytest

from breezewidget import RichTextSegment, RICH_TEXT_ROLE
from test_rich_text_interactions import editor_in_table


@pytest.mark.parametrize('number,color', list(enumerate([
    '#008000', '#ffff00', '#ff0000', '#0000ff', '#800080', '#ffa500', '#ffffff', '#000000',
])))
def test_mouse_preset_uses_saved_selection_and_keeps_editor(qtbot, number, color):
    host, table, editor, other, delegate = editor_in_table(qtbot)
    commits = []
    delegate.modelUpdated.connect(lambda i: commits.append(i.data(RICH_TEXT_ROLE)))
    errors = []
    actions_seen = []

    def click_preset():
        menu = QApplication.activePopupWidget()
        try:
            submenu = menu.actions()[-1].menu()
            menu.setActiveAction(menu.actions()[-1])
            qtbot.keyClick(menu, Qt.Key_Right)
            qtbot.waitUntil(submenu.isVisible)
            action = submenu.actions()[number]
            assert action.text()
            assert not action.icon().isNull()
            actions_seen.append(action.text())
            qtbot.mouseClick(submenu, Qt.LeftButton, pos=submenu.actionGeometry(action).center())
        except BaseException as exc:
            errors.append(exc)
            if menu is not None:
                menu.close()

    QTimer.singleShot(20, click_preset)
    event = QContextMenuEvent(QContextMenuEvent.Mouse, QPoint(10, 10), editor.mapToGlobal(QPoint(10, 10)))
    QApplication.sendEvent(editor.viewport(), event)
    assert not errors, errors
    assert len(actions_seen) == 1
    qtbot.waitUntil(editor.hasFocus)
    assert commits == []
    expected = (RichTextSegment('Mathe', color), RichTextSegment(' Sport'))
    assert editor.segments() == expected
    editor.undo()
    assert editor.segments() == (RichTextSegment('Mathe Sport'),)
    editor.redo()
    assert editor.segments() == expected
    other.setFocus()
    qtbot.waitUntil(lambda: len(commits) == 1)
    assert commits == [expected]


def test_custom_labels_presets_and_disabled_without_selection(qtbot):
    host, table, editor, other, delegate = editor_in_table(qtbot)
    editor.setColorPresets([('Grün', '#008000')])
    editor.setColorMenuLabels('Textfarbe', 'Eigene Farbe …')
    cursor = editor.textCursor()
    cursor.clearSelection()
    editor.setTextCursor(cursor)
    observed = []

    def inspect_menu():
        menu = QApplication.activePopupWidget()
        submenu = menu.actions()[-1].menu()
        observed.append((submenu.title(), submenu.isEnabled(), [a.text() for a in submenu.actions()]))
        menu.close()

    QTimer.singleShot(20, inspect_menu)
    event = QContextMenuEvent(QContextMenuEvent.Mouse, QPoint(10, 10), editor.mapToGlobal(QPoint(10, 10)))
    QApplication.sendEvent(editor.viewport(), event)
    assert observed == [('Textfarbe', False, ['Grün', '', 'Eigene Farbe …'])]
