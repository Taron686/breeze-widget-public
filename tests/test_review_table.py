from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap, QColor
from PySide6.QtWidgets import QStyle, QStyleOptionViewItem, QTableWidgetItem
from breezewidget import TableWidget, Theme, setTheme


def test_table_delegate_renders_check_state_and_icon(qapp, qtbot):
    setTheme(Theme.LIGHT, qapp)
    table = TableWidget()
    qtbot.addWidget(table)
    table.setRowCount(1)
    table.setColumnCount(1)
    item = QTableWidgetItem("Task")
    item.setCheckState(Qt.Unchecked)
    table.setItem(0, 0, item)
    table.resize(300, 150)
    table.show()
    unchecked = table.viewport().grab().toImage()
    item.setCheckState(Qt.Checked)
    checked = table.viewport().grab().toImage()
    assert checked != unchecked
    pixmap = QPixmap(16, 16)
    pixmap.fill(QColor("#ff0000"))
    item.setIcon(QIcon(pixmap))
    assert table.viewport().grab().toImage() != checked


def test_table_delegate_preserves_background_role_and_checkbox_hit_area(qapp, qtbot):
    setTheme(Theme.LIGHT, qapp)
    table = TableWidget()
    qtbot.addWidget(table)
    table.setRowCount(1)
    table.setColumnCount(1)
    item = QTableWidgetItem("Task")
    item.setCheckState(Qt.Unchecked)
    item.setBackground(QColor("#ff00ff"))
    table.setItem(0, 0, item)
    table.resize(300, 150)
    table.show()
    table.clearSelection()
    table.setCurrentCell(-1, -1)
    index = table.model().index(0, 0)
    rect = table.visualRect(index)
    image = table.viewport().grab().toImage()
    assert image.pixelColor(rect.right() - 15, rect.center().y()) == QColor("#ff00ff")

    option = QStyleOptionViewItem()
    option.widget = table
    table.itemDelegate().initStyleOption(option, index)
    option.rect = rect
    indicator = table.style().subElementRect(QStyle.SE_ItemViewItemCheckIndicator, option, table)
    qtbot.mouseClick(table.viewport(), Qt.LeftButton, pos=indicator.center())
    assert item.checkState() == Qt.Checked
