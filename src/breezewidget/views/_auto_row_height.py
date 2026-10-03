"""Lazily installed coalesced content sizing for TableWidget."""
from PySide6.QtCore import QEvent, QObject, QRect, QTimer, Slot
from PySide6.QtWidgets import QStyleOptionViewItem

from ..theme import ThemeManager


class _AutoRowHeightController(QObject):
    def __init__(self, table):
        super().__init__(table)
        self.table = table
        self.enabled = False
        self.minimums = {}
        self._resizing = False
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self._resize)
        table.installEventFilter(self)
        table.viewport().installEventFilter(self)
        table.horizontalHeader().sectionResized.connect(self.schedule)
        table.horizontalHeader().geometriesChanged.connect(self.schedule)
        # Hiding/showing rows also emits this signal. Our own height changes
        # are ignored by schedule() while _resizing is true.
        table.verticalHeader().sectionResized.connect(self.schedule)
        model = table.model()
        model.dataChanged.connect(self.schedule)
        model.rowsInserted.connect(self._inserted)
        model.rowsRemoved.connect(self._removed)
        model.columnsInserted.connect(self.schedule)
        model.columnsRemoved.connect(self.schedule)
        model.modelReset.connect(self._reset)
        model.layoutChanged.connect(self.schedule)
        ThemeManager.instance().themeChanged.connect(self.schedule)
        ThemeManager.instance().themeColorChanged.connect(self.schedule)
        self._delegates = set()
        self.watchDelegate(table.itemDelegate())
        for row in range(table.rowCount()):
            self.watchDelegate(table.itemDelegateForRow(row))
        for column in range(table.columnCount()):
            self.watchDelegate(table.itemDelegateForColumn(column))

    def watchDelegate(self, delegate):
        if delegate is not None and delegate not in self._delegates:
            self._delegates.add(delegate)
            delegate.sizeHintChanged.connect(self.schedule)
        self.schedule()

    def setEnabled(self, enabled):
        self.enabled = bool(enabled)
        if self.enabled:
            self.schedule()
        else:
            self.timer.stop()

    def setMinimum(self, row, height):
        self.minimums[row] = height
        self.schedule()

    @Slot()
    def schedule(self, *args):
        if self.enabled and not self._resizing and not self.timer.isActive():
            self.timer.start(0)

    def _inserted(self, parent, first, last):
        count = last - first + 1
        self.minimums = {row + count if row >= first else row: height for row, height in self.minimums.items()}
        self.schedule()

    def _removed(self, parent, first, last):
        count = last - first + 1
        self.minimums = {row - count if row > last else row: height
                         for row, height in self.minimums.items() if not first <= row <= last}
        self.schedule()

    def _reset(self):
        self.minimums.clear()
        self.schedule()

    def eventFilter(self, watched, event):
        if event.type() in (QEvent.Type.Resize, QEvent.Type.FontChange, QEvent.Type.StyleChange,
                            QEvent.Type.PaletteChange, QEvent.Type.Show,
                            QEvent.Type.ScreenChangeInternal, QEvent.Type.DevicePixelRatioChange):
            self.schedule()
        return False

    def _resize(self):
        if not self.enabled:
            return
        table = self.table
        self._resizing = True
        try:
            for row in range(table.rowCount()):
                if table.isRowHidden(row):
                    continue  # No visual geometry; remeasure when shown.
                height = self.minimums.get(row, table.verticalHeader().minimumSectionSize())
                column = 0
                while column < table.columnCount():
                    index = table.model().index(row, column)
                    # Only the span's anchor is painted. Qt's visual geometry
                    # includes every visible spanned section and the grid inset.
                    column += table.columnSpan(row, column)
                    width = table.visualRect(index).width()
                    if width <= 0:
                        continue
                    option = QStyleOptionViewItem()
                    table.initViewItemOption(option)
                    option.rect = QRect(0, 0, width, table.rowHeight(row))
                    delegate = table.itemDelegateForIndex(index)
                    height = max(height, delegate.sizeHint(option, index).height() + int(table.showGrid()))
                if table.rowHeight(row) != height:
                    table.setRowHeight(row, height)
        finally:
            self._resizing = False
