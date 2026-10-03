import pytest
from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QTextBlockFormat

import breezewidget as bw
from test_rich_text_checklist_delegate import marker_point, option_for
from test_rich_text_checklists import editor_marker_point
from test_rich_text_interactions import editor_in_table


@pytest.mark.parametrize("theme", [bw.Theme.LIGHT, bw.Theme.DARK])
@pytest.mark.parametrize("selected", [False, True])
def test_checked_marker_stays_visible_after_editor_commit_and_reopen(qtbot, qapp, theme, selected):
    bw.setTheme(theme, qapp)
    try:
        host, table, editor, other, delegate = editor_in_table(qtbot)
        delegate.setChecklistsEnabled(True)
        editor.setChecklistsEnabled(True)
        original = (bw.RichTextBlock((bw.RichTextSegment("task"),), False),)
        editor.setBlocks(original)
        other.setFocus()
        qtbot.waitUntil(lambda: table.item(0, 0).data(258) == original)
        qtbot.waitUntil(lambda: not any(e.isVisible() for e in table.findChildren(bw.RichTextEdit)))
        index = table.model().index(0, 0)

        def display_marker():
            table.setCurrentCell(0, 0 if selected else 1)
            if not selected:
                table.clearSelection()
            other.setFocus()
            qtbot.mouseMove(other)
            qtbot.wait(20)
            point = marker_point(delegate, table, index, 0)
            image = table.viewport().grab().toImage().scaled(table.viewport().size())
            return image.copy(QRect(point.x() - 10, point.y() - 10, 21, 21))

        def open_editor():
            rect = table.visualRect(index)
            point = QPoint(rect.left() + 100, rect.top() + 10)
            qtbot.mouseClick(table.viewport(), Qt.LeftButton, pos=point)
            qtbot.mouseDClick(table.viewport(), Qt.LeftButton, pos=point)
            qtbot.waitUntil(lambda: any(e.isVisible() for e in table.findChildren(bw.RichTextEdit)))
            result = next(e for e in table.findChildren(bw.RichTextEdit) if e.isVisible())
            result.setFocus()
            qtbot.waitUntil(result.hasFocus)
            return result

        unchecked_display = display_marker()
        editor = open_editor()
        point = editor_marker_point(editor, 0)
        unchecked_editor = editor.viewport().grab().toImage().scaled(editor.viewport().size()).copy(
            QRect(point.x() - 10, point.y() - 10, 21, 21))
        qtbot.mouseClick(editor.viewport(), Qt.LeftButton, pos=point)
        assert editor.blocks()[0].checked is True
        checked_editor = editor.viewport().grab().toImage().scaled(editor.viewport().size()).copy(
            QRect(point.x() - 10, point.y() - 10, 21, 21))
        assert checked_editor != unchecked_editor
        other.setFocus()
        qtbot.waitUntil(lambda: table.item(0, 0).data(258)[0].checked is True)
        qtbot.waitUntil(lambda: not any(e.isVisible() for e in table.findChildren(bw.RichTextEdit)))
        assert index.data(Qt.DisplayRole) == index.data(Qt.EditRole) == "task"
        assert index.data(257) == (bw.RichTextSegment("task"),)
        document, _ = delegate._layout(delegate._option(option_for(table, index), index), index)
        assert document.begin().blockFormat().marker() == QTextBlockFormat.MarkerType.Checked
        checked_display = display_marker()
        editor = open_editor()
        assert editor.blocks()[0].checked is True
        other.setFocus()
        qtbot.waitUntil(lambda: not any(e.isVisible() for e in table.findChildren(bw.RichTextEdit)))
        assert checked_display != unchecked_display, (
            "Editor, model and display document are checked, but the normal cell marker "
            "paints identically to its unchecked state")
    finally:
        bw.setTheme(bw.Theme.LIGHT, qapp)
