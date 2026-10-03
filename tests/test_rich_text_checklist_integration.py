import pytest
from PySide6.QtCore import QPoint, QTimer, Qt
from PySide6.QtGui import QColor, QContextMenuEvent, QIcon, QPixmap, QTextCursor
from PySide6.QtWidgets import QApplication, QStyle, QTableWidgetItem

import breezewidget as bw
from test_rich_text_checklist_delegate import make_table, marker_point, option_for
from test_rich_text_interactions import editor_in_table


@pytest.mark.parametrize("theme", [bw.Theme.LIGHT, bw.Theme.DARK])
def test_checklist_coexists_with_cell_check_icon_background(qtbot, qapp, theme):
    bw.setTheme(theme, qapp)
    try:
        table, delegate, index = make_table(qtbot)
        item = index.model().item(0, 0)
        item.setCheckable(True)
        item.setCheckState(Qt.Unchecked)
        item.setBackground(QColor("#00ff00"))
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor("#0000ff"))
        item.setIcon(QIcon(pixmap))
        table.clearSelection()
        table.setCurrentIndex(index.model().index(-1, -1))
        qtbot.wait(20)
        option = delegate._option(option_for(table, index), index)
        indicator = table.style().subElementRect(QStyle.SE_ItemViewItemCheckIndicator, option, table)
        qtbot.mouseClick(table.viewport(), Qt.LeftButton, pos=indicator.center())
        assert item.checkState() == Qt.Checked
        assert [b.checked for b in index.data(258)] == [False, True, False]
        qtbot.mouseClick(table.viewport(), Qt.LeftButton, pos=marker_point(delegate, table, index, 2))
        assert item.checkState() == Qt.Checked
        assert [b.checked for b in index.data(258)] == [False, True, True]
        table.clearSelection()
        table.setCurrentIndex(index.model().index(-1, -1))
        qtbot.wait(20)
        # visualRect uses logical pixels; normalize high-DPI grab pixels to match.
        image = table.viewport().grab().toImage().scaled(table.viewport().size())
        rect = table.visualRect(index)
        assert image.pixelColor(rect.right() - 15, rect.center().y()) == QColor("#00ff00")
        colors = {image.pixelColor(x, y).name() for x in range(rect.left(), rect.right())
                  for y in range(rect.top(), rect.bottom())}
        assert "#ff0000" in colors and "#0000ff" in colors
    finally:
        bw.setTheme(bw.Theme.LIGHT, qapp)


def test_wrapped_task_uses_same_editor_metrics_and_auto_row_height(qtbot):
    table = bw.TableWidget()
    qtbot.addWidget(table)
    table.setRowCount(1)
    table.setColumnCount(1)
    table.setColumnWidth(0, 140)
    item = QTableWidgetItem("a" * 100)
    item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)
    item.setData(258, (bw.RichTextBlock((bw.RichTextSegment("a" * 100),), False),))
    table.setItem(0, 0, item)
    delegate = bw.RichTextTableItemDelegate(table)
    table.setItemDelegate(delegate)
    table.setAutoRowHeightEnabled(True)
    table.resize(400, 500)
    table.show()
    qtbot.wait(30)
    before = table.rowHeight(0)
    delegate.setChecklistsEnabled(True)
    qtbot.waitUntil(lambda: table.rowHeight(0) > before)
    index = table.model().index(0, 0)
    document, _ = delegate._layout(delegate._option(option_for(table, index), index), index)
    table.editItem(item)
    editor = table.findChild(bw.RichTextEdit)
    qtbot.wait(20)
    assert document.blockCount() == editor.document().blockCount() == 1
    assert document.begin().layout().lineCount() == editor.document().begin().layout().lineCount() > 1
    assert document.size().height() == editor.document().size().height()
    assert table.rowHeight(0) >= document.size().height() + 4


@pytest.mark.parametrize("action_number", [0, 1, 2])
def test_real_checklist_menu_keyboard_actions_keep_editor_until_commit(qtbot, action_number):
    host, table, editor, other, delegate = editor_in_table(qtbot)
    delegate.setChecklistsEnabled(True)
    editor.setChecklistsEnabled(True)
    editor.setChecklistMenuLabels("Als Checkliste", "Checkbox entfernen", "Erledigt umschalten")
    if action_number:
        editor.insertChecklist()
    commits = []
    delegate.modelUpdated.connect(lambda idx: commits.append(idx.data(258)))
    errors = []

    def activate_action():
        menu = QApplication.activePopupWidget()
        try:
            assert editor.isFormattingPopupOpen() and not commits
            action = menu.actions()[-3 + action_number]
            assert action.isEnabled()
            menu.setActiveAction(action)
            qtbot.keyClick(menu, Qt.Key_Return)
        except BaseException as exc:
            errors.append(exc)
            menu.close()

    QTimer.singleShot(20, activate_action)
    event = QContextMenuEvent(QContextMenuEvent.Keyboard, QPoint(10, 10),
                              editor.mapToGlobal(QPoint(10, 10)))
    QApplication.sendEvent(editor.viewport(), event)
    assert not errors
    qtbot.waitUntil(editor.hasFocus)
    assert not commits
    assert editor.blocks()[0].checked is (False, None, True)[action_number]
    other.setFocus()
    qtbot.waitUntil(lambda: len(commits) == 1)
    assert commits[0][0].checked is (False, None, True)[action_number]
