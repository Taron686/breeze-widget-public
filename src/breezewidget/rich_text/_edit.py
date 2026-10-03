from __future__ import annotations

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QIcon, QPixmap, QTextCharFormat, QTextCursor, QTextDocumentFragment, QTextOption
from PySide6.QtWidgets import QDialog

from ..dialogs.color_dialog import ColorDialog
from ..menu import RoundMenu
from ..widgets.text_edit import TextEdit
from ._model import _segments, _set_segments
from ._blocks import _blocks, _checked, _set_blocks, _set_checked
from ._checklist_geometry import _marker_at


class RichTextEdit(TextEdit):
    """TextEdit with selectable text colors and a popup-safe cell editor mode."""

    def __init__(self, parent=None, *, cellMode=False):
        super().__init__(parent)
        self._cell_mode = bool(cellMode)
        self._popup_depth = 0
        self._popup_cursor = None
        self._color_presets = None
        self._color_menu_title = None
        self._custom_color_label = None
        self._checklists_enabled = False
        self._checklist_labels = None
        self._checklist_pressed = None
        self.setWordWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
        if cellMode:
            self.setMinimumHeight(0)
            self.setAcceptRichText(False)

    def setSegments(self, segments):
        """Replace text/colors and reset undo history, as when loading model data."""
        _set_segments(self.document(), tuple(segments))

    def segments(self):
        """Return normalized immutable segments (adjacent equal colors merge)."""
        return _segments(self.document())

    def plainText(self):
        """Lossless plain text, including soft breaks and nonbreaking spaces."""
        return "".join(segment.text for segment in self.segments())

    def setChecklistsEnabled(self, enabled):
        """Enable checklist actions, mouse toggling and task-aware Enter."""
        self._checklists_enabled = bool(enabled)
        self._checklist_pressed = None

    def isChecklistsEnabled(self):
        return self._checklists_enabled

    def setBlocks(self, blocks):
        """Replace paragraphs, colors and states, clearing undo history."""
        _set_blocks(self.document(), blocks)

    def blocks(self):
        """Extract immutable paragraphs with their current native task states."""
        return _blocks(self.document())

    def setChecklistMenuLabels(self, insert, remove, toggle):
        self._checklist_labels = (str(insert), str(remove), str(toggle))

    def _can_change_checklists(self):
        return self._checklists_enabled and self.isEnabled() and not self.isReadOnly()

    def _selected_blocks(self, cursor):
        start, end = cursor.selectionStart(), cursor.selectionEnd()
        block = self.document().findBlock(start)
        result = [block]
        block = block.next()
        while block.isValid() and block.position() < end:
            result.append(block)
            block = block.next()
        return result

    def _change_checklists(self, operation):
        if not self._can_change_checklists():
            return
        cursor = QTextCursor(self._popup_cursor or self.textCursor())
        blocks = [cursor.block()] if operation == "toggle" else self._selected_blocks(cursor)
        cursor.beginEditBlock()
        for block in blocks:
            checked = _checked(block)
            if operation == "insert" and checked is None:
                _set_checked(block, False)
            elif operation == "remove" and checked is not None:
                _set_checked(block, None)
            elif operation == "toggle" and checked is not None:
                _set_checked(block, not checked)
        cursor.endEditBlock()
        self.setTextCursor(cursor)

    def insertChecklist(self):
        """Convert selected paragraphs to tasks; existing task states survive."""
        self._change_checklists("insert")

    def removeChecklist(self):
        """Remove selected task markers, preserving text and foreground colors."""
        self._change_checklists("remove")

    def toggleChecklistItem(self):
        """Toggle the current task in one undo step."""
        self._change_checklists("toggle")

    def keyPressEvent(self, event):
        cursor = self.textCursor()
        if (self._can_change_checklists() and event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
                and not event.modifiers() and not cursor.hasSelection()
                and _checked(cursor.block()) is not None):
            cursor.beginEditBlock()
            if not cursor.block().text():
                _set_checked(cursor.block(), None)
            else:
                # At the start the existing text moves into the new block;
                # its state must follow it, leaving the preceding task open.
                state = _checked(cursor.block()) if cursor.atBlockStart() else False
                if cursor.atBlockStart():
                    _set_checked(cursor.block(), False)
                cursor.insertBlock()
                _set_checked(cursor.block(), state)
            cursor.endEditBlock()
            self.setTextCursor(cursor)
            event.accept()
            return
        super().keyPressEvent(event)

    def _event_marker(self, event):
        point = event.position() + QPointF(self.horizontalScrollBar().value(),
                                          self.verticalScrollBar().value())
        return _marker_at(self.document(), point)

    def mousePressEvent(self, event):
        self._checklist_pressed = None
        if self._can_change_checklists() and event.button() == Qt.MouseButton.LeftButton:
            block = self._event_marker(event)
            if block is not None:
                self._checklist_pressed = block
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        pressed = self._checklist_pressed
        self._checklist_pressed = None
        if pressed is not None and event.button() == Qt.MouseButton.LeftButton:
            if self._can_change_checklists() and pressed == self._event_marker(event):
                cursor = QTextCursor(pressed)
                cursor.beginEditBlock()
                _set_checked(pressed, not _checked(pressed))
                cursor.endEditBlock()
            event.accept()
            return
        # QTextEdit itself handles native marker releases. Consume these when
        # checklist interaction is disabled, read-only, or a double click.
        if event.button() == Qt.MouseButton.LeftButton and self._event_marker(event) is not None:
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._event_marker(event) is not None:
            self._checklist_pressed = None
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def setColorPresets(self, presets):
        """Override swatches with ``[(translated_label, QColor-compatible), ...]``."""
        colors = [(str(label), QColor(color)) for label, color in presets]
        if any(not color.isValid() for _, color in colors):
            raise ValueError("invalid preset color")
        self._color_presets = colors

    def setColorMenuLabels(self, title, customColor):
        self._color_menu_title = str(title)
        self._custom_color_label = str(customColor)

    def applyTextColor(self, color):
        """Color the selection in one undo step. No selection means no change."""
        cursor = QTextCursor(self._popup_cursor or self.textCursor())
        color = QColor(color)
        if not cursor.hasSelection() or not color.isValid():
            return
        fmt = QTextCharFormat()
        fmt.setForeground(color)
        cursor.beginEditBlock()
        cursor.mergeCharFormat(fmt)
        cursor.endEditBlock()
        self.setTextCursor(cursor)

    def isFormattingPopupOpen(self):
        return self._popup_depth > 0

    def _presets(self):
        if self._color_presets is not None:
            return self._color_presets
        return [(self.tr(name), QColor(color)) for name, color in (
            ("Green", "#008000"), ("Yellow", "#ffff00"), ("Red", "#ff0000"),
            ("Blue", "#0000ff"), ("Purple", "#800080"), ("Orange", "#ffa500"),
            ("White", "#ffffff"), ("Black", "#000000"))]

    def _choose_color(self):
        dialog = ColorDialog(self.textColor(), self._custom_color_label or self.tr("Custom color…"), self)
        try:
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.applyTextColor(dialog.color())
        finally:
            dialog.deleteLater()

    def contextMenuEvent(self, event):
        # One continuous guard spans menu.hide -> action -> modal dialog.exec.
        # aboutToHide is too early to release the cell delegate's focus lock.
        self._popup_depth += 1
        self._popup_cursor = QTextCursor(self.textCursor())
        standard = self.createStandardContextMenu()
        menu = RoundMenu(parent=self)
        for action in standard.actions():
            action.setParent(menu)
            menu.addAction(action)
        standard.deleteLater()
        menu.addSeparator()
        colors = RoundMenu(self._color_menu_title or self.tr("Text color"), menu)
        colors.setEnabled(self._popup_cursor.hasSelection() and not self.isReadOnly())
        for label, color in self._presets():
            swatch = QPixmap(16, 16)
            swatch.fill(color)
            action = colors.addAction(QIcon(swatch), label)
            action.triggered.connect(lambda checked=False, value=color: self.applyTextColor(value))
        colors.addSeparator()
        colors.addAction(self._custom_color_label or self.tr("Custom color…"), self._choose_color)
        menu.addMenu(colors)
        if self._checklists_enabled:
            menu.addSeparator()
            labels = self._checklist_labels or (self.tr("Insert checkbox"),
                                                self.tr("Remove checkbox"),
                                                self.tr("Toggle completed"))
            current = _checked(self._popup_cursor.block())
            for label, callback, applicable in (
                    (labels[0], self.insertChecklist, True),
                    (labels[1], self.removeChecklist, any(
                        _checked(block) is not None for block in self._selected_blocks(self._popup_cursor))),
                    (labels[2], self.toggleChecklistItem, current is not None)):
                action = menu.addAction(label, callback)
                action.setEnabled(self._can_change_checklists() and applicable)
        try:
            menu.exec(event.globalPos())
        finally:
            self.window().activateWindow()
            self.setFocus(Qt.FocusReason.PopupFocusReason)
            self._popup_cursor = None
            self._popup_depth -= 1
            menu.deleteLater()

    def insertPlainText(self, text):
        if (not self._can_change_checklists()
                or not any(separator in text for separator in ("\n", "\r", "\u2029"))):
            return super().insertPlainText(text)
        insert = super().insertPlainText
        self._insert_checklist_content(lambda: insert(text))

    def _insert_checklist_content(self, insert):
        cursor = self.textCursor()
        start = cursor.selectionStart()
        first = self.document().findBlock(start)
        checked = _checked(first)
        end = cursor.selectionEnd()
        end_block = self.document().findBlock(end)
        end_checked = _checked(end_block)
        same_paragraph = first == end_block
        prefix_survives = start > first.position()
        suffix_survives = (end < end_block.position() + end_block.length() - 1
                           or end == end_block.position())
        cursor.beginEditBlock()
        # Native insertion owns selection replacement and its character format.
        # An accepted but empty HTML clipboard can leave the selection intact.
        insert()
        inserted = self.textCursor()
        last = inserted.block()
        if (not inserted.hasSelection() and inserted.position() != start
                and (checked is not None or end_checked is not None)):
            first = self.document().findBlock(start)
            block = first
            while block.isValid():
                state = False if checked is not None else None
                if block == first and prefix_survives:
                    state = checked
                elif block == last and suffix_survives and (not prefix_survives or not same_paragraph):
                    # Separate surviving paragraphs keep their own states.
                    # Splitting one task keeps its state on only one part.
                    state = end_checked
                _set_checked(block, state)
                if block == last:
                    break
                block = block.next()
        cursor.endEditBlock()

    def insertFromMimeData(self, source):
        if self._cell_mode:
            text = source.text() if source.hasText() else QTextDocumentFragment.fromHtml(source.html()).toPlainText()
            self.insertPlainText(text)
        elif (self._can_change_checklists() and source.hasText()
              and not source.hasHtml() and source.text()):
            self.insertPlainText(source.text())
        elif self._can_change_checklists():
            insert = super().insertFromMimeData
            self._insert_checklist_content(lambda: insert(source))
        else:
            super().insertFromMimeData(source)

    def canInsertFromMimeData(self, source):
        if self._cell_mode:
            return source.hasText() or source.hasHtml()
        return super().canInsertFromMimeData(source)
