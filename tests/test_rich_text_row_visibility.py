import pytest
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QStyleOptionViewItem, QTableWidgetItem

from breezewidget import TableWidget, RichTextTableItemDelegate


def settle(app):
    # Drain geometry and coalesced resize work before the next visibility step.
    for _ in range(20):
        app.processEvents()


def visible_table(qtbot, qapp, delegate_type=RichTextTableItemDelegate):
    table = TableWidget()
    qtbot.addWidget(table)
    table.setRowCount(2)
    table.setColumnCount(1)
    table.setColumnWidth(0, 100)
    table.setItem(0, 0, QTableWidgetItem('a' * 100))
    table.setItem(1, 0, QTableWidgetItem('short'))
    table.setItemDelegate(delegate_type(table))
    table.resize(350, 400)
    table.show()
    settle(qapp)
    return table


def content_height(table):
    index = table.model().index(0, 0)
    option = QStyleOptionViewItem()
    table.initViewItemOption(option)
    option.rect = table.visualRect(index)
    return table.itemDelegateForIndex(index).sizeHint(option, index).height() + int(table.showGrid())


@pytest.mark.parametrize('route', ['row', 'hidden', 'header'])
@pytest.mark.parametrize('change', ['content', 'column', 'font', 'enable'])
def test_shown_row_reflows_after_changes_while_hidden(qtbot, qapp, route, change):
    table = visible_table(qtbot, qapp)
    if change != 'enable':
        table.setAutoRowHeightEnabled(True)
        settle(qapp)
        assert table.rowHeight(0) == content_height(table)
    if route == 'row':
        table.hideRow(0)
    elif route == 'hidden':
        table.setRowHidden(0, True)
    else:
        table.verticalHeader().hideSection(0)
    settle(qapp)
    if change == 'content':
        table.item(0, 0).setText('a' * 200)
    elif change == 'column':
        table.setColumnWidth(0, 70)
    elif change == 'font':
        font = QFont(table.font())
        font.setPointSize(18)
        table.item(0, 0).setFont(font)
    else:
        table.setAutoRowHeightEnabled(True)
    settle(qapp)
    if route == 'row':
        table.showRow(0)
    elif route == 'hidden':
        table.setRowHidden(0, False)
    else:
        table.verticalHeader().showSection(0)
    settle(qapp)
    assert table.rowHeight(0) == content_height(table)


def test_auto_height_coalesces_changes_without_self_resize_feedback(qtbot, qapp):
    class CountingDelegate(RichTextTableItemDelegate):
        calls = 0

        def sizeHint(self, option, index):
            self.calls += 1
            return super().sizeHint(option, index)

    table = visible_table(qtbot, qapp, CountingDelegate)
    table.setAutoRowHeightEnabled(True)
    settle(qapp)
    delegate = table.itemDelegate()
    delegate.calls = 0
    for text in ('a' * 90, 'a' * 70, 'a' * 50):
        table.item(0, 0).setText(text)
    settle(qapp)
    assert delegate.calls == 2  # One pass measures the two visible rows.
    settle(qapp)
    assert delegate.calls == 2
    assert table.rowHeight(0) == content_height(table)
