from dataclasses import FrozenInstanceError

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor

import breezewidget as bw


def test_block_validation_and_stable_exports():
    from breezewidget.rich_text import RichTextBlock, RICH_TEXT_BLOCKS_ROLE
    assert bw.RichTextBlock is RichTextBlock
    assert bw.RICH_TEXT_BLOCKS_ROLE == RICH_TEXT_BLOCKS_ROLE == 258
    block = RichTextBlock((bw.RichTextSegment("one", "#AABBCC"),), True,
                          separatorColor="#FF0000")
    assert block.separatorColor == "#ff0000"
    with pytest.raises(FrozenInstanceError):
        block.checked = False
    for state in (0, 1, "yes", [], object()):
        with pytest.raises(TypeError):
            RichTextBlock((), state)
    for text in ("a\nb", "\r", "\u2029"):
        with pytest.raises(ValueError):
            RichTextBlock((bw.RichTextSegment(text),))
    with pytest.raises(TypeError):
        RichTextBlock([bw.RichTextSegment("mutable")])
    with pytest.raises(ValueError):
        RichTextBlock((), separatorColor="red")


def test_blocks_roundtrip_colored_separators_unicode_and_empty_paragraphs(qtbot):
    editor = bw.RichTextEdit()
    qtbot.addWidget(editor)
    editor.setChecklistsEnabled(True)
    blocks = (
        bw.RichTextBlock((bw.RichTextSegment("😀 A\u00a0B\u2028C", "#ff0000"),), True,
                         separatorColor="#0000ff"),
        bw.RichTextBlock((), False, separatorColor="#008000"),
        bw.RichTextBlock((bw.RichTextSegment("normal"),)),
    )
    editor.setBlocks(blocks)
    assert editor.blocks() == blocks
    assert editor.plainText() == "😀 A\u00a0B\u2028C\n\nnormal"
    assert editor.segments() == (
        bw.RichTextSegment("😀 A\u00a0B\u2028C", "#ff0000"),
        bw.RichTextSegment("\n", "#0000ff"),
        bw.RichTextSegment("\n", "#008000"), bw.RichTextSegment("normal"))
    assert not editor.document().isUndoAvailable()


def test_checklist_actions_selection_boundary_and_undo(qtbot):
    editor = bw.RichTextEdit()
    qtbot.addWidget(editor)
    editor.setSegments((bw.RichTextSegment("red\nblue\nnormal", "#ff0000"),))
    editor.insertChecklist()  # disabled by default
    assert all(block.checked is None for block in editor.blocks())
    editor.setChecklistsEnabled(True)
    cursor = editor.textCursor()
    cursor.setPosition(0)
    cursor.setPosition(9, QTextCursor.KeepAnchor)  # start of third paragraph
    editor.setTextCursor(cursor)
    editor.insertChecklist()
    assert [b.checked for b in editor.blocks()] == [False, False, None]
    editor.undo()
    assert [b.checked for b in editor.blocks()] == [None, None, None]
    editor.redo()
    editor.setTextCursor(cursor)
    editor.removeChecklist()
    assert [b.checked for b in editor.blocks()] == [None, None, None]
    assert editor.segments() == (bw.RichTextSegment("red\nblue\nnormal", "#ff0000"),)
    editor.undo()
    assert [b.checked for b in editor.blocks()] == [False, False, None]
    cursor.setPosition(4)
    editor.setTextCursor(cursor)
    editor.toggleChecklistItem()
    assert [b.checked for b in editor.blocks()] == [False, True, None]
    editor.undo()
    assert [b.checked for b in editor.blocks()] == [False, False, None]


def test_enter_continues_task_then_empty_task_ends_list(qtbot):
    editor = bw.RichTextEdit()
    qtbot.addWidget(editor)
    editor.setChecklistsEnabled(True)
    editor.setBlocks((bw.RichTextBlock((bw.RichTextSegment("done"),), True),))
    editor.moveCursor(QTextCursor.End)
    qtbot.keyClick(editor, Qt.Key_Return)
    assert [b.checked for b in editor.blocks()] == [True, False]
    qtbot.keyClick(editor, Qt.Key_Return)
    assert [b.checked for b in editor.blocks()] == [True, None]
    assert editor.plainText() == "done\n"
    editor.undo()
    assert [b.checked for b in editor.blocks()] == [True, False]


def test_readonly_actions_leave_blocks_unchanged(qtbot):
    editor = bw.RichTextEdit()
    qtbot.addWidget(editor)
    editor.setChecklistsEnabled(True)
    blocks = (bw.RichTextBlock((bw.RichTextSegment("task"),), False),)
    editor.setBlocks(blocks)
    editor.setReadOnly(True)
    editor.toggleChecklistItem()
    editor.removeChecklist()
    assert editor.blocks() == blocks


def editor_marker_point(editor, number):
    from PySide6.QtCore import QPointF
    document = editor.document()
    document.size()
    block = document.findBlockByNumber(number)
    rect = document.documentLayout().blockBoundingRect(block)
    points = []
    for y in range(int(rect.top()), int(rect.bottom()) + 1):
        for x in range(min(70, int(document.size().width()))):
            hit = document.documentLayout().blockWithMarkerAt(QPointF(x, y))
            if hit.isValid() and hit.blockNumber() == number:
                points.append(QPointF(x - editor.horizontalScrollBar().value(),
                                      y - editor.verticalScrollBar().value()))
    assert points
    return points[len(points) // 2].toPoint()


def test_editor_marker_click_scroll_doubleclick_and_undo(qtbot):
    editor = bw.RichTextEdit()
    qtbot.addWidget(editor)
    editor.setChecklistsEnabled(True)
    editor.resize(250, 120)
    editor.setBlocks(tuple(bw.RichTextBlock((bw.RichTextSegment(f"task {i}"),), False)
                           for i in range(20)))
    editor.show()
    editor.moveCursor(QTextCursor.End)
    editor.ensureCursorVisible()
    qtbot.wait(20)
    point = editor_marker_point(editor, 19)
    qtbot.mouseClick(editor.viewport(), Qt.LeftButton, pos=point)
    assert [b.checked for b in editor.blocks()] == [False] * 19 + [True]
    qtbot.mouseDClick(editor.viewport(), Qt.LeftButton, pos=point)
    qtbot.mouseRelease(editor.viewport(), Qt.LeftButton, pos=point)
    assert editor.blocks()[-1].checked is True
    editor.undo()
    assert editor.blocks()[-1].checked is False
    editor.redo()
    assert editor.blocks()[-1].checked is True
    editor.setChecklistsEnabled(False)
    qtbot.mouseClick(editor.viewport(), Qt.LeftButton, pos=point)
    assert editor.blocks()[-1].checked is True


def test_enter_before_task_preserves_existing_text_state(qtbot):
    editor = bw.RichTextEdit()
    qtbot.addWidget(editor)
    editor.setChecklistsEnabled(True)
    editor.setBlocks((bw.RichTextBlock((bw.RichTextSegment("done", "#ff0000"),), True),))
    editor.moveCursor(QTextCursor.Start)
    qtbot.keyClick(editor, Qt.Key_Return)
    assert editor.blocks()[1].segments == (bw.RichTextSegment("done", "#ff0000"),)
    assert [b.checked for b in editor.blocks()] == [False, True]
    editor.undo()
    assert editor.blocks()[0].checked is True


def test_deleting_preceding_paragraph_retains_task_state(qtbot):
    editor = bw.RichTextEdit()
    qtbot.addWidget(editor)
    editor.setChecklistsEnabled(True)
    editor.setBlocks((bw.RichTextBlock((bw.RichTextSegment("normal"),)),
                      bw.RichTextBlock((bw.RichTextSegment("done"),), True)))
    cursor = editor.textCursor()
    cursor.setPosition(0)
    cursor.setPosition(7, QTextCursor.KeepAnchor)
    cursor.removeSelectedText()
    assert editor.blocks() == (bw.RichTextBlock((bw.RichTextSegment("done"),), True),)


@pytest.mark.parametrize("cell_mode", [False, True])
@pytest.mark.parametrize("position", [0, 2, 4])
@pytest.mark.parametrize("insertion", ["paste", "plain_text"])
def test_multiline_insertion_preserves_original_task_and_opens_new_tasks(qtbot, cell_mode, position, insertion):
    from PySide6.QtCore import QMimeData

    editor = bw.RichTextEdit(cellMode=cell_mode)
    qtbot.addWidget(editor)
    editor.setChecklistsEnabled(True)
    original = (bw.RichTextBlock((bw.RichTextSegment("done", "#ff0000"),), True),)
    editor.setBlocks(original)
    cursor = editor.textCursor()
    cursor.setPosition(position)
    editor.setTextCursor(cursor)
    text = "first 😀\u00a0\u2028soft\nsecond\nthird"
    if insertion == "paste":
        mime = QMimeData()
        mime.setText(text)
        editor.insertFromMimeData(mime)
    else:
        editor.insertPlainText(text)
    assert editor.plainText() == "done"[:position] + text + "done"[position:]
    assert [b.checked for b in editor.blocks()] == ([False, False, True] if position == 0 else [True, False, False])
    assert editor.segments() == (bw.RichTextSegment(editor.plainText(), "#ff0000"),)
    editor.undo()
    assert editor.blocks() == original
    editor.redo()
    assert [b.checked for b in editor.blocks()] == ([False, False, True] if position == 0 else [True, False, False])


@pytest.mark.parametrize("has_plain_text", [False, True])
@pytest.mark.parametrize("position", [0, 2, 4])
def test_rich_html_paste_preserves_task_state_and_incoming_formats(qtbot, has_plain_text, position):
    from PySide6.QtCore import QMimeData
    from PySide6.QtGui import QFont

    editor = bw.RichTextEdit()
    qtbot.addWidget(editor)
    editor.setChecklistsEnabled(True)
    original = (bw.RichTextBlock((bw.RichTextSegment("done", "#ff0000"),), True),)
    editor.setBlocks(original)
    cursor = editor.textCursor()
    cursor.setPosition(position)
    editor.setTextCursor(cursor)
    mime = QMimeData()
    mime.setHtml('<p><span style="color:#008000;font-weight:700">first😀&nbsp;</span></p>'
                 '<p><span style="color:#0000ff">second</span></p>')
    if has_plain_text:
        mime.setText("first😀\u00a0\nsecond")
    editor.insertFromMimeData(mime)
    assert editor.plainText() == "done"[:position] + "first😀\u00a0\nsecond" + "done"[position:]
    assert [b.checked for b in editor.blocks()] == ([False, True] if position == 0 else [True, False])
    first = editor.document().find("first").charFormat()
    second = editor.document().find("second").charFormat()
    assert first.foreground().color().name() == "#008000"
    assert first.fontWeight() == QFont.Bold
    assert second.foreground().color().name() == "#0000ff"
    for existing_text in ("done"[:position], "done"[position:]):
        if existing_text:
            assert editor.document().find(existing_text).charFormat().foreground().color().name() == "#ff0000"
    editor.undo()
    assert editor.blocks() == original
    editor.redo()
    assert [b.checked for b in editor.blocks()] == ([False, True] if position == 0 else [True, False])
    assert editor.document().find("first").charFormat().fontWeight() == QFont.Bold


@pytest.mark.parametrize("cell_mode", [False, True])
@pytest.mark.parametrize("checked", [None, True])
@pytest.mark.parametrize("insertion", ["paste", "plain_text"])
def test_multiline_selection_replacement_preserves_native_insertion_format(qtbot, cell_mode, checked, insertion):
    from PySide6.QtCore import QMimeData
    from PySide6.QtGui import QFont, QTextCharFormat

    editor = bw.RichTextEdit(cellMode=cell_mode)
    qtbot.addWidget(editor)
    editor.setChecklistsEnabled(True)
    original = (bw.RichTextBlock((bw.RichTextSegment("done", "#ff0000"),), checked),)
    editor.setBlocks(original)
    cursor = editor.textCursor()
    cursor.select(QTextCursor.Document)
    fmt = QTextCharFormat()
    fmt.setFontItalic(True)
    fmt.setFontWeight(QFont.Bold)
    cursor.mergeCharFormat(fmt)
    editor.document().clearUndoRedoStacks()
    editor.setTextCursor(cursor)
    if insertion == "paste":
        mime = QMimeData()
        mime.setText("a\nb")
        editor.insertFromMimeData(mime)
    else:
        editor.insertPlainText("a\nb")
    assert editor.segments() == (bw.RichTextSegment("a\nb", "#ff0000"),)
    for text in ("a", "b"):
        inserted = editor.document().find(text).charFormat()
        assert inserted.fontItalic() and inserted.fontWeight() == QFont.Bold
    editor.undo()
    assert editor.blocks() == original
    assert editor.document().find("done").charFormat().fontItalic()
    editor.redo()
    assert editor.segments() == (bw.RichTextSegment("a\nb", "#ff0000"),)


@pytest.mark.parametrize("enabled", [False, True])
@pytest.mark.parametrize("checked", [None, True])
@pytest.mark.parametrize("paste_method", ["paste", "keyboard"])
def test_empty_html_clipboard_preserves_native_noop_selection(qtbot, enabled, checked, paste_method):
    from PySide6.QtCore import QMimeData
    from PySide6.QtWidgets import QApplication

    editor = bw.RichTextEdit()
    qtbot.addWidget(editor)
    editor.setChecklistsEnabled(enabled)
    original = (bw.RichTextBlock((bw.RichTextSegment("done", "#ff0000"),), checked),)
    editor.setBlocks(original)
    cursor = editor.textCursor()
    cursor.select(QTextCursor.Document)
    editor.setTextCursor(cursor)
    editor.show()
    editor.setFocus()
    mime = QMimeData()
    mime.setHtml("<p></p>")
    assert editor.canInsertFromMimeData(mime)
    clipboard = QApplication.clipboard()
    clipboard.setMimeData(mime)
    try:
        if paste_method == "keyboard":
            qtbot.keyClick(editor, Qt.Key_V, Qt.ControlModifier)
        else:
            editor.paste()
        assert editor.blocks() == original
        assert editor.textCursor().selectionStart() == 0
        assert editor.textCursor().selectionEnd() == 4
        assert not editor.document().isUndoAvailable()
    finally:
        clipboard.clear()


@pytest.mark.parametrize("insertion", ["standalone_plain", "cell_plain", "standalone_html"])
@pytest.mark.parametrize("states", [(True, False), (False, True), (True, None)])
@pytest.mark.parametrize("start,end,text,paragraphs,owners", [
    (0, 5, "prefix\n", ["prefix", "open"], ["new", "end"]),
    (2, 7, "a\nb\n", ["doa", "b", "en"], ["start", "new", "end"]),
    (0, 7, "a\nb\n", ["a", "b", "en"], ["new", "new", "end"]),
    (2, 9, "a\nb", ["doa", "b"], ["start", "new"]),
    (0, 9, "a\nb", ["a", "b"], ["new", "new"]),
])
def test_selected_paragraph_paste_preserves_surviving_task_owners(
        qtbot, insertion, states, start, end, text, paragraphs, owners):
    from PySide6.QtCore import QMimeData
    from PySide6.QtGui import QFont

    editor = bw.RichTextEdit(cellMode=insertion == "cell_plain")
    qtbot.addWidget(editor)
    editor.setChecklistsEnabled(True)
    original = (bw.RichTextBlock((bw.RichTextSegment("done", "#ff0000"),), states[0]),
                bw.RichTextBlock((bw.RichTextSegment("open", "#0000ff"),), states[1]))
    editor.setBlocks(original)
    cursor = editor.textCursor()
    cursor.setPosition(start)
    cursor.setPosition(end, QTextCursor.KeepAnchor)
    editor.setTextCursor(cursor)
    mime = QMimeData()
    if insertion == "standalone_html":
        mime.setHtml("".join(f'<p><b style="color:#008000">{part}</b></p>' for part in text.split("\n")))
    else:
        mime.setText(text)
    editor.insertFromMimeData(mime)
    result = editor.blocks()
    assert ["".join(s.text for s in b.segments) for b in result] == paragraphs
    owner_states = {"start": states[0], "end": states[1], "new": False}
    expected = [owner_states[owner] for owner in owners]
    assert [b.checked for b in result] == expected
    if start == 2:
        assert editor.document().find("do").charFormat().foreground().color().name() == "#ff0000"
    if end < 9:
        surviving = "open" if end == 5 else "en"
        assert editor.document().find(surviving).charFormat().foreground().color().name() == "#0000ff"
    if insertion == "standalone_html":
        pasted = editor.document().find("prefix" if text.startswith("prefix") else "a").charFormat()
        assert pasted.foreground().color().name() == "#008000"
        assert pasted.fontWeight() == QFont.Bold
    editor.undo()
    assert editor.blocks() == original
    editor.redo()
    assert [b.checked for b in editor.blocks()] == expected
