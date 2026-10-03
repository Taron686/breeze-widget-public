from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import QTableWidgetItem
from breezewidget import TableWidget, RichTextTableItemDelegate, RichTextEdit, Theme, setTheme


def test_themed_editor_honors_item_font_and_default_foreground(qtbot, qapp):
    setTheme(Theme.DARK, qapp)
    table = TableWidget()
    qtbot.addWidget(table)
    table.setRowCount(1)
    table.setColumnCount(1)
    table.setItemDelegate(RichTextTableItemDelegate(table))
    item = QTableWidgetItem('Mathe Sport')
    font = QFont('Arial', 24)
    item.setFont(font)
    item.setForeground(QColor('#ff0000'))
    table.setItem(0, 0, item)
    table.show()
    table.editItem(item)
    editor = table.findChild(RichTextEdit)
    qtbot.wait(20)
    assert editor.document().defaultFont().pointSize() == 24
    assert editor.palette().color(QPalette.Text) == QColor('#ff0000')
    setTheme(Theme.LIGHT, qapp)
    qtbot.wait(20)
    assert editor.document().defaultFont().pointSize() == 24
    assert editor.palette().color(QPalette.Text) == QColor('#ff0000')
