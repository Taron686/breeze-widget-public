from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem
from breezewidget import TableWidget, RichTextTableItemDelegate, RichTextEdit, Theme, setTheme
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QStyleOptionViewItem


def test_themed_cell_fits_last_line_including_stylesheet_padding(qtbot, qapp):
    setTheme(Theme.LIGHT, qapp)
    table = TableWidget()
    qtbot.addWidget(table)
    table.setRowCount(1)
    table.setColumnCount(1)
    table.setColumnWidth(0, 150)
    item = QTableWidgetItem('one\ntwo\nthree\nfour\nfive\nsix')
    item.setTextAlignment(Qt.AlignTop | Qt.AlignLeft)
    table.setItem(0, 0, item)
    table.setItemDelegate(RichTextTableItemDelegate(table))
    table.setAutoRowHeightEnabled(True)
    table.resize(300, 350)
    table.show()
    qtbot.wait(30)
    table.editItem(item)
    editor = table.findChild(RichTextEdit)
    assert editor.viewport().height() >= editor.document().size().height()


def test_long_word_does_not_leak_native_text_into_right_padding(qtbot, qapp):
    setTheme(Theme.LIGHT, qapp)
    table = TableWidget()
    qtbot.addWidget(table)
    table.setRowCount(1)
    table.setColumnCount(1)
    table.setColumnWidth(0, 150)
    item = QTableWidgetItem('a' * 100)
    item.setForeground(QColor('#ff0000'))
    item.setBackground(QColor('#00ff00'))
    item.setTextAlignment(Qt.AlignTop | Qt.AlignLeft)
    table.setItem(0, 0, item)
    table.setItemDelegate(RichTextTableItemDelegate(table))
    table.setAutoRowHeightEnabled(True)
    table.resize(300, 400)
    table.show()
    table.setCurrentCell(-1, -1)
    table.clearSelection()
    qtbot.wait(30)
    index = table.model().index(0, 0)
    option = QStyleOptionViewItem()
    table.initViewItemOption(option)
    table.itemDelegate().initStyleOption(option, index)
    option.rect = table.visualRect(index)
    text_rect = table.itemDelegate()._text_rect(option)
    image = table.viewport().grab().toImage()
    scale = image.devicePixelRatio()
    for x in range(text_rect.right() + 1, option.rect.right() - 4):
        for y in range(text_rect.top(), text_rect.bottom()):
            assert image.pixelColor(int(x * scale), int(y * scale)) == QColor('#00ff00')
