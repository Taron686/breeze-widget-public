import pytest
from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QMouseEvent, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QStyleOptionViewItem

import breezewidget as bw


def sample_blocks():
    return tuple(bw.RichTextBlock((bw.RichTextSegment(text, color),), state)
                 for text, color, state in (("one", "#ff0000", False),
                                            ("two", None, True), ("three", "#0000ff", False)))


def make_table(qtbot, *, enabled=True, model=None, color_role=257, blocks_role=258):
    table = bw.TableView()
    qtbot.addWidget(table)
    model = model or QStandardItemModel(1, 1, table)
    item = QStandardItem("one\ntwo\nthree")
    item.setData(sample_blocks(), blocks_role)
    item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)
    model.setItem(0, 0, item)
    table.setModel(model)
    delegate = bw.RichTextTableItemDelegate(table, richTextRole=color_role,
                                            richTextBlocksRole=blocks_role)
    delegate.setChecklistsEnabled(enabled)
    table.setItemDelegate(delegate)
    table.resize(400, 260)
    table.setColumnWidth(0, 240)
    table.setRowHeight(0, 170)
    table.show()
    qtbot.wait(20)
    return table, delegate, model.index(0, 0)


def option_for(table, index):
    option = QStyleOptionViewItem()
    table.initViewItemOption(option)
    option.rect = table.visualRect(index)
    return option


def marker_point(delegate, table, index, block_number):
    # Probe Qt's public hit test, independent of our event-coordinate helper.
    option = delegate._option(option_for(table, index), index)
    doc, rect = delegate._layout(option, index)
    y = rect.top()
    if option.displayAlignment & Qt.AlignBottom:
        y += max(0, rect.height() - doc.size().height())
    elif option.displayAlignment & Qt.AlignVCenter:
        y += max(0, (rect.height() - doc.size().height()) / 2)
    doc.size()
    points = []
    for py in range(int(doc.size().height())):
        for px in range(min(70, int(doc.size().width()))):
            block = doc.documentLayout().blockWithMarkerAt(QPointF(px, py))
            if block.isValid() and block.blockNumber() == block_number:
                points.append(QPointF(px + rect.left(), py + y))
    assert points, "Qt must render a marker for the requested task"
    return points[len(points) // 2].toPoint()


def test_role_collision_rejected_and_disabled_fallback(qtbot):
    with pytest.raises(ValueError):
        bw.RichTextTableItemDelegate(richTextRole=258, richTextBlocksRole=258)
    table, delegate, index = make_table(qtbot, enabled=False)
    option = option_for(table, index)
    editor = delegate.createEditor(table, option, index)
    qtbot.addWidget(editor)
    delegate.setEditorData(editor, index)
    assert [b.checked for b in editor.blocks()] == [None, None, None]
    delegate.setModelData(editor, index.model(), index)
    assert index.data(258) == sample_blocks()


def test_external_click_updates_every_role_before_one_signal(qtbot):
    table, delegate, index = make_table(qtbot, color_role=270, blocks_role=271)
    observations = []
    delegate.checklistItemToggled.connect(lambda idx, number, checked: observations.append(
        (idx.data(Qt.DisplayRole), idx.data(Qt.EditRole), idx.data(270), idx.data(271), number, checked)))
    updates = []
    delegate.modelUpdated.connect(lambda idx: updates.append(idx.row()))
    for number in range(3):
        qtbot.mouseClick(table.viewport(), Qt.LeftButton, pos=marker_point(delegate, table, index, number))
    assert len(observations) == len(updates) == 3
    assert [entry[-2:] for entry in observations] == [(0, True), (1, False), (2, True)]
    assert [b.checked for b in index.data(271)] == [True, False, True]
    assert observations[-1][0] == observations[-1][1] == "one\ntwo\nthree"
    assert observations[-1][2] == (bw.RichTextSegment("one", "#ff0000"),
        bw.RichTextSegment("\ntwo\n"), bw.RichTextSegment("three", "#0000ff"))
    assert table.findChild(bw.RichTextEdit) is None


@pytest.mark.parametrize("metadata", [None, (), ["invalid"],
    (bw.RichTextBlock((bw.RichTextSegment("stale"),), True),)])
def test_bad_blocks_preserve_plain_text_and_legacy_colors(qtbot, metadata):
    table, delegate, index = make_table(qtbot)
    model = index.model()
    model.setData(index, metadata, 258)
    colors = (bw.RichTextSegment("one\ntwo\nthree", "#123456"),)
    model.setData(index, colors, 257)
    editor = delegate.createEditor(table, option_for(table, index), index)
    qtbot.addWidget(editor)
    delegate.setEditorData(editor, index)
    assert editor.plainText() == "one\ntwo\nthree"
    assert editor.segments() == colors
    assert [b.checked for b in editor.blocks()] == [None, None, None]


def test_editor_commit_blocks_authoritative_over_stale_colors(qtbot):
    table, delegate, index = make_table(qtbot)
    index.model().setData(index, (bw.RichTextSegment("one\ntwo\nthree", "#008000"),), 257)
    editor = delegate.createEditor(table, option_for(table, index), index)
    qtbot.addWidget(editor)
    delegate.setEditorData(editor, index)
    assert editor.blocks() == sample_blocks()
    editor.moveCursor(editor.textCursor().MoveOperation.Start)
    editor.toggleChecklistItem()
    toggles = []
    delegate.checklistItemToggled.connect(lambda *args: toggles.append(args))
    delegate.setModelData(editor, index.model(), index)
    assert index.data(258)[0].checked is True
    assert index.data(257)[0] == bw.RichTextSegment("one", "#ff0000")
    assert not toggles


def test_temporary_layout_does_not_invalidate_live_viewport(qtbot):
    from shiboken6 import isValid
    table, delegate, index = make_table(qtbot)
    viewport = table.viewport()
    document, _ = delegate._layout(delegate._option(option_for(table, index), index), index)
    document.size()
    del document
    assert isValid(viewport)


@pytest.mark.parametrize("alignment", [Qt.AlignTop, Qt.AlignVCenter, Qt.AlignBottom])
def test_marker_follows_alignment_scroll_and_resize(qtbot, alignment):
    table, delegate, index = make_table(qtbot)
    model = index.model()
    model.item(0, 0).setTextAlignment(Qt.AlignLeft | alignment)
    for row in range(1, 15):
        model.setItem(row, 0, QStandardItem("filler"))
    table.setColumnWidth(0, 450)
    table.horizontalScrollBar().setValue(35)
    qtbot.wait(20)
    for width, height in ((450, 170), (180, 100), (280, 140)):
        table.setColumnWidth(0, width)
        table.setRowHeight(0, height)
        qtbot.wait(10)
        point = marker_point(delegate, table, index, 1)
        qtbot.mouseClick(table.viewport(), Qt.LeftButton, pos=point)
    assert [b.checked for b in index.data(258)] == [False, False, False]


@pytest.mark.parametrize("restriction", ["not_editable", "not_enabled", "widget_disabled"])
def test_marker_never_edits_restricted_item(qtbot, restriction):
    table, delegate, index = make_table(qtbot)
    point = marker_point(delegate, table, index, 0)
    item = index.model().item(0, 0)
    if restriction == "not_editable":
        item.setEditable(False)
    elif restriction == "not_enabled":
        item.setEnabled(False)
    else:
        table.setEnabled(False)
    qtbot.mouseClick(table.viewport(), Qt.LeftButton, pos=point)
    assert index.data(258) == sample_blocks()


def test_marker_drag_off_and_doubleclick_do_not_toggle_twice(qtbot):
    table, delegate, index = make_table(qtbot)
    first = marker_point(delegate, table, index, 0)
    second = marker_point(delegate, table, index, 1)
    qtbot.mousePress(table.viewport(), Qt.LeftButton, pos=first)
    qtbot.mouseRelease(table.viewport(), Qt.LeftButton, pos=second)
    assert index.data(258) == sample_blocks()
    calls = []
    delegate.checklistItemToggled.connect(lambda *args: calls.append(args))
    qtbot.mouseClick(table.viewport(), Qt.LeftButton, pos=first)
    qtbot.mouseDClick(table.viewport(), Qt.LeftButton, pos=first)
    qtbot.mouseRelease(table.viewport(), Qt.LeftButton, pos=first)
    assert len(calls) == 1
    assert table.findChild(bw.RichTextEdit) is None


class UpdatingModel(QStandardItemModel):
    mode = "reject"

    def setItemData(self, index, roles):
        if self.mode == "reject":
            return False
        accepted = super().setItemData(index, roles)
        if self.mode == "remove":
            self.removeRow(index.row())
        elif self.mode == "reset":
            self.clear()
        elif self.mode == "sort":
            self.sort(0)
        return accepted


@pytest.mark.parametrize("mode", ["reject", "remove", "reset", "sort"])
def test_model_mutation_controls_success_observation(qtbot, mode):
    model = UpdatingModel(1, 1)
    model.mode = mode
    table, delegate, index = make_table(qtbot, model=model)
    model.setItem(1, 0, QStandardItem("aaa"))
    calls, updates = [], []
    delegate.checklistItemToggled.connect(lambda idx, number, checked: calls.append((idx.row(), number, checked)))
    delegate.modelUpdated.connect(lambda idx: updates.append(idx.row()))
    qtbot.mouseClick(table.viewport(), Qt.LeftButton, pos=marker_point(delegate, table, index, 0))
    if mode == "sort":
        assert calls == [(1, 0, True)]
        assert updates == [1]
    else:
        assert not calls and not updates
    if mode == "reject":
        assert index.data(258) == sample_blocks()


def test_model_updated_subscriber_reset_suppresses_invalid_toggle_signal(qtbot):
    table, delegate, index = make_table(qtbot)
    model = index.model()
    delegate.modelUpdated.connect(lambda idx: model.clear())
    calls = []
    delegate.checklistItemToggled.connect(lambda *args: calls.append(args))
    qtbot.mouseClick(table.viewport(), Qt.LeftButton, pos=marker_point(delegate, table, index, 0))
    assert not calls


@pytest.mark.parametrize("enabled", [False, True])
def test_legacy_color_role_258_loads_and_commits_without_implicit_collision(qtbot, enabled):
    table = bw.TableWidget()
    qtbot.addWidget(table)
    table.setRowCount(1)
    table.setColumnCount(1)
    from PySide6.QtGui import QTextCursor
    from PySide6.QtWidgets import QTableWidgetItem

    delegate = bw.RichTextTableItemDelegate(table, richTextRole=258)
    assert delegate.richTextRole() == 258
    assert delegate.richTextBlocksRole() == 259
    assert not delegate.isChecklistsEnabled()
    delegate.setChecklistsEnabled(enabled)
    table.setItemDelegate(delegate)
    segments = (bw.RichTextSegment("one", "#ff0000"),
                bw.RichTextSegment("\ntwo", "#0000ff"))
    item = QTableWidgetItem("one\ntwo")
    item.setData(258, segments)
    blocks = (bw.RichTextBlock((segments[0],), False, separatorColor="#0000ff"),
              bw.RichTextBlock((bw.RichTextSegment("two", "#0000ff"),), True))
    item.setData(259, blocks)
    table.setItem(0, 0, item)
    index = table.model().index(0, 0)
    editor = delegate.createEditor(table, option_for(table, index), index)
    qtbot.addWidget(editor)
    delegate.setEditorData(editor, index)
    assert editor.segments() == segments
    assert [b.checked for b in editor.blocks()] == ([False, True] if enabled else [None, None])
    editor.moveCursor(QTextCursor.End)
    editor.insertPlainText("!")
    delegate.setModelData(editor, table.model(), index)
    assert item.text() == "one\ntwo!"
    assert item.data(258) == (segments[0], bw.RichTextSegment("\ntwo!", "#0000ff"))
    if enabled:
        assert [b.checked for b in item.data(259)] == [False, True]
        assert item.data(259)[1].segments == (bw.RichTextSegment("two!", "#0000ff"),)
    else:
        assert item.data(259) == blocks
