from __future__ import annotations

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPalette, QPen
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QLineEdit,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTableWidget,
    QWidget,
)

from ..constants import PROP_ITEM_VIEW
from ..theme import getPalette


class TableItemDelegate(QStyledItemDelegate):
    """Breeze-styled item delegate for QTableWidget-based tables."""

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index) -> None:
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)

        palette = getPalette()
        selected = bool(opt.state & QStyle.StateFlag.State_Selected)
        current = _is_current_index(opt.widget, index)
        hovered = bool(opt.state & QStyle.StateFlag.State_MouseOver)
        editing = bool(opt.state & QStyle.StateFlag.State_Editing)

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(Qt.PenStyle.NoPen)
        background = QBrush(QColor(_cell_background(palette, index.row(), selected, current, hovered)))
        if not (selected or current or hovered) and opt.backgroundBrush.style() != Qt.BrushStyle.NoBrush:
            background = opt.backgroundBrush
        painter.setBrush(background)
        painter.drawRoundedRect(_cell_rect(opt.rect), 4, 4)

        if selected or current:
            _draw_accent(painter, _cell_rect(opt.rect), QColor(palette.primary4), current)

        if not editing:
            # Qt owns text layout, decoration and check indicators. Only the
            # selection background is custom; keep the original item geometry
            # so the inherited editorEvent still hits the drawn checkbox.
            opt.state &= ~(QStyle.StateFlag.State_Selected | QStyle.StateFlag.State_MouseOver
                           | QStyle.StateFlag.State_HasFocus)
            opt.features &= ~QStyleOptionViewItem.ViewItemFeature.Alternate
            opt.backgroundBrush = QBrush(Qt.BrushStyle.NoBrush)
            if index.data(Qt.ItemDataRole.ForegroundRole) is None:
                opt.palette.setColor(QPalette.ColorRole.Text, QColor(palette.text1))
                opt.palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(palette.text2))
            painter.setFont(opt.font)
            self._draw_content(painter, opt, index)
        painter.restore()

    def _draw_content(self, painter, option, index):
        style = option.widget.style() if option.widget is not None else QApplication.style()
        style.drawControl(QStyle.ControlElement.CE_ItemViewItem, option, painter, option.widget)

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index):
        editor = super().createEditor(parent, option, index)
        if isinstance(editor, QLineEdit):
            palette = getPalette()
            editor.setFrame(False)
            editor.setStyleSheet(
                "QLineEdit { "
                f"background: {palette.surface5}; "
                f"color: {palette.text1}; "
                f"selection-background-color: {palette.primary4}; "
                f"selection-color: {palette.primary_text}; "
                "border: none; "
                "padding: 2px 8px; "
                "}"
            )
        return editor

    def updateEditorGeometry(self, editor: QWidget, option: QStyleOptionViewItem, index) -> None:
        del index
        editor.setGeometry(_cell_rect(option.rect))


class TableWidget(QTableWidget):
    """Breeze-styled :class:`QTableWidget` with qfluent-compatible border helpers."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty(PROP_ITEM_VIEW, "tableWidget")
        self.setAlternatingRowColors(True)
        self.setShowGrid(False)
        self.setMouseTracking(True)
        self.setItemDelegate(TableItemDelegate(self))
        self._borderRadius = 8
        self._apply_empty_area_palette()

    def setBorderVisible(self, visible: bool) -> None:
        self.setFrameShape(QFrame.Shape.StyledPanel if visible else QFrame.Shape.NoFrame)

    def _row_height_controller(self):
        from ._auto_row_height import _AutoRowHeightController
        if not hasattr(self, "_auto_row_height"):
            self._auto_row_height = _AutoRowHeightController(self)
        return self._auto_row_height

    def setAutoRowHeightEnabled(self, enabled: bool) -> None:
        """Opt into coalesced content sizing; disabling leaves current heights."""
        self._row_height_controller().setEnabled(enabled)

    def isAutoRowHeightEnabled(self) -> bool:
        return hasattr(self, "_auto_row_height") and self._auto_row_height.enabled

    def setMinimumRowHeight(self, row: int, height: int) -> None:
        """Set a logical row's floor; it follows insertion/deletion of other rows."""
        if not 0 <= row < self.rowCount():
            raise IndexError("row out of range")
        self._row_height_controller().setMinimum(row, max(0, int(height)))

    def setItemDelegate(self, delegate) -> None:
        super().setItemDelegate(delegate)
        if hasattr(self, "_auto_row_height"):
            self._auto_row_height.watchDelegate(delegate)

    def setItemDelegateForRow(self, row, delegate) -> None:
        super().setItemDelegateForRow(row, delegate)
        if hasattr(self, "_auto_row_height"):
            self._auto_row_height.watchDelegate(delegate)

    def setItemDelegateForColumn(self, column, delegate) -> None:
        super().setItemDelegateForColumn(column, delegate)
        if hasattr(self, "_auto_row_height"):
            self._auto_row_height.watchDelegate(delegate)

    def setSpan(self, row, column, rowSpan, columnSpan) -> None:
        super().setSpan(row, column, rowSpan, columnSpan)
        if hasattr(self, "_auto_row_height"):
            self._auto_row_height.schedule()

    def clearSpans(self) -> None:
        super().clearSpans()
        if hasattr(self, "_auto_row_height"):
            self._auto_row_height.schedule()

    def setBorderRadius(self, radius: int) -> None:
        self._borderRadius = max(0, int(radius))
        self.setProperty("_breezeTableRadius", self._borderRadius)
        self.style().unpolish(self)
        self.style().polish(self)

    def borderRadius(self) -> int:
        return self._borderRadius

    def refreshTheme(self) -> None:
        self._apply_empty_area_palette()

    def _apply_empty_area_palette(self) -> None:
        palette = getPalette()
        qt_palette = self.palette()
        background = QColor(palette.surface2)
        qt_palette.setColor(QPalette.ColorRole.Base, background)
        qt_palette.setColor(QPalette.ColorRole.Window, background)
        self.setPalette(qt_palette)
        self.viewport().setPalette(qt_palette)
        self.viewport().setStyleSheet(f"background: {palette.surface2};")
        header_qss = (
            "QHeaderView { "
            f"background: {palette.surface2}; "
            "border: none; "
            "} "
            "QHeaderView::section { "
            f"background: {palette.surface3}; "
            f"color: {palette.text1}; "
            "border: none; "
            "padding: 4px 8px; "
            "}"
        )
        for header in (self.horizontalHeader(), self.verticalHeader()):
            header.setPalette(qt_palette)
            header.viewport().setPalette(qt_palette)
            header.viewport().setStyleSheet(f"background: {palette.surface2};")
            header.setStyleSheet(header_qss)


def _is_current_index(widget: QWidget | None, index) -> bool:
    return hasattr(widget, "currentIndex") and widget.currentIndex() == index


def _cell_rect(rect: QRect):
    return rect.adjusted(4, 2, -4, -2)


def _cell_background(palette, row: int, selected: bool, current: bool, hovered: bool) -> str:
    if current:
        return palette.surface5
    if selected:
        return palette.surface4
    if hovered:
        return palette.surface4
    return palette.surface3 if row % 2 else palette.surface2


def _draw_accent(painter: QPainter, rect, color: QColor, focused: bool) -> None:
    painter.setPen(QPen(color, 2))
    painter.drawLine(rect.left() + 1, rect.bottom(), rect.right() - 1, rect.bottom())
    if focused:
        painter.drawLine(rect.left(), rect.top() + 6, rect.left(), rect.bottom() - 6)
