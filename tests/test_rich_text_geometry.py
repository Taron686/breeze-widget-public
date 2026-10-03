import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QIcon, QPixmap, QTextOption
from PySide6.QtWidgets import QStyle, QStyleOptionViewItem, QTableWidgetItem

from breezewidget import TableWidget, RichTextTableItemDelegate, RichTextEdit, Theme, setTheme


def table_with_cell(qtbot, text, *, wrap=QTextOption.WrapAtWordBoundaryOrAnywhere):
    table = TableWidget()
    qtbot.addWidget(table)
    table.setRowCount(1)
    table.setColumnCount(1)
    table.setColumnWidth(0, 150)
    table.setItem(0, 0, QTableWidgetItem(text))
    table.item(0, 0).setTextAlignment(Qt.AlignTop | Qt.AlignLeft)
    table.setItemDelegate(RichTextTableItemDelegate(table, wrapMode=wrap))
    table.resize(300, 400)
    table.setAutoRowHeightEnabled(True)
    table.show()
    qtbot.wait(30)
    return table


@pytest.mark.parametrize('text', ['a' * 100, 'Normal words ' * 15,
                                 'one\ntwo\nthree\nfour\nfive\nsix'])
def test_editor_and_renderer_have_identical_line_layout(qtbot, text):
    table = table_with_cell(qtbot, text)
    index = table.model().index(0, 0)
    option = QStyleOptionViewItem()
    table.initViewItemOption(option)
    option.rect = table.visualRect(index)
    delegate = table.itemDelegate()
    document, rect = delegate._layout(delegate._option(option, index), index)
    table.editItem(table.item(0, 0))
    editor = table.findChild(RichTextEdit)
    qtbot.wait(20)
    assert editor.viewport().width() == rect.width()
    assert editor.document().textWidth() == document.textWidth()
    assert editor.document().size().height() == document.size().height()
    assert table.rowHeight(0) >= document.size().height() + 4
    assert editor.plainText() == text
    block = document.begin()
    edit_block = editor.document().begin()
    while block.isValid():
        assert block.layout().lineCount() == edit_block.layout().lineCount()
        block, edit_block = block.next(), edit_block.next()


def test_font_role_and_column_resize_reflow_both_documents(qtbot):
    table = table_with_cell(qtbot, 'Words to wrap ' * 10)
    before = table.rowHeight(0)
    font = QFont(table.font())
    font.setPointSize(24)
    table.item(0, 0).setFont(font)
    qtbot.waitUntil(lambda: table.rowHeight(0) > before)
    tall = table.rowHeight(0)
    table.setColumnWidth(0, 280)
    qtbot.waitUntil(lambda: table.rowHeight(0) < tall)


@pytest.mark.parametrize('theme', [Theme.LIGHT, Theme.DARK])
def test_rich_delegate_preserves_background_foreground_icons_and_check_hit(qtbot, qapp, theme):
    setTheme(theme, qapp)
    table = table_with_cell(qtbot, 'MMMM')
    item = table.item(0, 0)
    item.setForeground(QColor('#ff0000'))
    item.setBackground(QColor('#00ff00'))
    item.setCheckState(Qt.Unchecked)
    icon = QPixmap(16, 16)
    icon.fill(QColor('#0000ff'))
    item.setIcon(QIcon(icon))
    table.clearSelection()
    table.setCurrentCell(-1, -1)
    qtbot.wait(20)
    index = table.model().index(0, 0)
    rect = table.visualRect(index)
    # visualRect uses logical pixels; normalize high-DPI grab pixels to match.
    image = table.viewport().grab().toImage().scaled(table.viewport().size())
    assert image.pixelColor(rect.right() - 15, rect.center().y()) == QColor('#00ff00')
    colors = {image.pixelColor(x, y).name() for x in range(rect.left(), rect.right())
              for y in range(rect.top(), rect.bottom())}
    assert '#ff0000' in colors
    assert '#0000ff' in colors
    option = QStyleOptionViewItem()
    table.initViewItemOption(option)
    table.itemDelegate().initStyleOption(option, index)
    option.rect = rect
    indicator = table.style().subElementRect(QStyle.SE_ItemViewItemCheckIndicator, option, table)
    qtbot.mouseClick(table.viewport(), Qt.LeftButton, pos=indicator.center())
    assert item.checkState() == Qt.Checked
    assert table.findChild(RichTextEdit) is None
    setTheme(Theme.LIGHT, qapp)


def test_wrap_mode_is_configurable(qtbot):
    table = table_with_cell(qtbot, 'a' * 100, wrap=QTextOption.NoWrap)
    assert table.rowHeight(0) < 50


def test_auto_height_maximum_across_columns_and_minimums_follow_row_mutations(qtbot):
    table = table_with_cell(qtbot, 'short')
    table.setColumnCount(2)
    table.setMinimumRowHeight(0, 72)
    table.setItem(0, 1, QTableWidgetItem('\n'.join(['line'] * 8)))
    qtbot.waitUntil(lambda: table.rowHeight(0) > 72)
    table.insertRow(0)
    table.setMinimumRowHeight(0, 36)
    table.item(1, 1).setText('short')
    qtbot.waitUntil(lambda: table.rowHeight(1) == 72)
    assert table.rowHeight(0) == 36
    table.removeRow(0)
    qtbot.waitUntil(lambda: table.rowHeight(0) == 72)


def test_auto_height_reflows_when_delegate_installed_after_enabling(qtbot):
    table = TableWidget()
    qtbot.addWidget(table)
    table.setRowCount(1)
    table.setColumnCount(1)
    table.setColumnWidth(0, 150)
    table.setItem(0, 0, QTableWidgetItem('a' * 100))
    table.setAutoRowHeightEnabled(True)
    table.show()
    qtbot.wait(30)
    before = table.rowHeight(0)
    table.setItemDelegate(RichTextTableItemDelegate(table))
    qtbot.waitUntil(lambda: table.rowHeight(0) > before)
