from dataclasses import FrozenInstanceError

import pytest
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QTextCursor

import breezewidget as bw


def test_rich_text_public_api():
    assert hasattr(bw, "RichTextSegment")
    from breezewidget.rich_text import RichTextSegment, RICH_TEXT_ROLE
    assert bw.RichTextSegment is RichTextSegment
    assert RICH_TEXT_ROLE > int(Qt.UserRole)
    with pytest.raises(FrozenInstanceError):
        RichTextSegment("x").text = "y"


def test_segments_preserve_emoji_blank_paragraphs_and_soft_breaks(qtbot):
    editor = bw.RichTextEdit()
    qtbot.addWidget(editor)
    segments = (bw.RichTextSegment("😀  Mathe", "#ff0000"),
                bw.RichTextSegment("\n\nSport\u2028Ende "))
    editor.setSegments(segments)
    assert editor.segments() == segments
    assert editor.plainText() == "😀  Mathe\n\nSport\u2028Ende "


@pytest.mark.parametrize("color", ["#008000", "#ffff00", "#ff0000", "#0000ff",
                                  "#800080", "#ffa500", "#ffffff", "#000000", "#123456"])
def test_color_changes_only_selection_and_is_one_undo_step(qtbot, color):
    editor = bw.RichTextEdit()
    qtbot.addWidget(editor)
    editor.setPlainText("Mathe Sport")
    cursor = editor.textCursor()
    cursor.setPosition(5, QTextCursor.KeepAnchor)
    editor.setTextCursor(cursor)
    editor.applyTextColor(color)
    assert editor.segments() == (bw.RichTextSegment("Mathe", color), bw.RichTextSegment(" Sport"))
    editor.undo()
    assert editor.segments() == (bw.RichTextSegment("Mathe Sport"),)
    editor.redo()
    assert editor.segments()[0].color == color


def test_cell_mode_pastes_plain_text_and_standalone_minimum_unchanged(qtbot):
    editor = bw.RichTextEdit(cellMode=True)
    qtbot.addWidget(editor)
    mime = QMimeData()
    mime.setText("Plain")
    mime.setHtml('<b style="color:red">Plain</b>')
    editor.insertFromMimeData(mime)
    assert editor.segments() == (bw.RichTextSegment("Plain"),)
    assert editor.minimumHeight() == 0
    ordinary = bw.TextEdit()
    qtbot.addWidget(ordinary)
    assert ordinary.minimumHeight() == 90
