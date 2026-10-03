from __future__ import annotations

from math import ceil

from PySide6.QtCore import QEvent, QModelIndex, QPersistentModelIndex, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QAbstractTextDocumentLayout, QPalette, QRegion, QTextOption
from PySide6.QtWidgets import QApplication, QFrame, QStyle, QStyleOptionViewItem
from shiboken6 import isValid

from ..views.table_widget import TableItemDelegate
from ._edit import RichTextEdit
from ._model import RICH_TEXT_ROLE, _configure_document, _document, _validated_segments
from ._blocks import (RICH_TEXT_BLOCKS_ROLE, RichTextBlock, _block_segments,
                      _set_blocks, _validated_blocks)
from ._checklist_geometry import _document_origin, _marker_at


class RichTextTableItemDelegate(TableItemDelegate):
    """Opt-in color-only, multiline cells. ``modelUpdated`` is the save boundary.

    The model must support setItemData for DisplayRole, EditRole and richTextRole.
    Models may emit intermediate dataChanged signals; persist from modelUpdated.
    """

    modelUpdated = Signal(QModelIndex)
    checklistItemToggled = Signal(QModelIndex, int, bool)

    def __init__(self, parent=None, *, richTextRole=RICH_TEXT_ROLE,
                 wrapMode=QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere,
                 richTextBlocksRole=None):
        super().__init__(parent)
        if int(richTextRole) < int(Qt.ItemDataRole.UserRole):
            raise ValueError("richTextRole must be a user role")
        self._rich_text_role = int(richTextRole)
        self._wrap_mode = QTextOption.WrapMode(wrapMode)
        if richTextBlocksRole is None:
            richTextBlocksRole = (RICH_TEXT_BLOCKS_ROLE + 1 if self._rich_text_role == RICH_TEXT_BLOCKS_ROLE
                                  else RICH_TEXT_BLOCKS_ROLE)
        if int(richTextBlocksRole) < int(Qt.ItemDataRole.UserRole) or int(richTextBlocksRole) == self._rich_text_role:
            raise ValueError("richTextBlocksRole must be a distinct user role")
        self._rich_text_blocks_role = int(richTextBlocksRole)
        self._checklists_enabled = False
        self._checklist_labels = None
        self._checklist_pressed = None

    def richTextBlocksRole(self):
        return self._rich_text_blocks_role

    def setChecklistsEnabled(self, enabled):
        self._checklists_enabled = bool(enabled)
        self._checklist_pressed = None
        self.sizeHintChanged.emit(QModelIndex())
        parent = self.parent()
        if hasattr(parent, "viewport"):
            parent.viewport().update()

    def isChecklistsEnabled(self):
        return self._checklists_enabled

    def setChecklistMenuLabels(self, insert, remove, toggle):
        """Override translated labels in subsequently created cell editors."""
        self._checklist_labels = (str(insert), str(remove), str(toggle))

    def richTextRole(self):
        return self._rich_text_role

    def wrapMode(self):
        return self._wrap_mode

    def _option(self, option, index):
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        opt.textElideMode = Qt.TextElideMode.ElideNone
        opt.features |= QStyleOptionViewItem.ViewItemFeature.WrapText
        return opt

    def _text_rect(self, option):
        style = option.widget.style() if option.widget is not None else QApplication.style()
        rect = style.subElementRect(QStyle.SubElement.SE_ItemViewItemText, option, option.widget)
        return rect.adjusted(4, 2, -4, -2)

    def _layout(self, option, index):
        rect = self._text_rect(option)
        text = index.data(Qt.ItemDataRole.DisplayRole)
        text = "" if text is None else str(text)
        segments = _validated_segments(text, index.data(self._rich_text_role))
        document = _document(segments, option.font, rect.width(), self._wrap_mode,
                             option.displayAlignment, option.widget)
        if self._checklists_enabled:
            blocks = _validated_blocks(text, index.data(self._rich_text_blocks_role))
            if blocks is not None:
                _set_blocks(document, blocks)
        return document, rect

    def _draw_content(self, painter, option, index):
        opt = self._option(option, index)
        document, rect = self._layout(opt, index)
        # Keep Qt's full option/geometry, but only draw its decoration regions.
        # Qt text can overflow SE_ItemViewItemText (unbroken words under QSS).
        painter.save()
        style = opt.widget.style() if opt.widget is not None else QApplication.style()
        decorations = QRegion()
        if opt.features & QStyleOptionViewItem.ViewItemFeature.HasCheckIndicator:
            decorations |= QRegion(style.subElementRect(QStyle.SubElement.SE_ItemViewItemCheckIndicator, opt, opt.widget))
        if opt.features & QStyleOptionViewItem.ViewItemFeature.HasDecoration:
            decorations |= QRegion(style.subElementRect(QStyle.SubElement.SE_ItemViewItemDecoration, opt, opt.widget))
        if not decorations.isEmpty():
            painter.setClipRegion(decorations, Qt.ClipOperation.IntersectClip)
            super()._draw_content(painter, opt, index)
        painter.restore()
        painter.save()
        painter.setClipRect(rect, Qt.ClipOperation.IntersectClip)
        painter.translate(_document_origin(document, rect, opt.displayAlignment))
        context = QAbstractTextDocumentLayout.PaintContext()
        context.palette = opt.palette
        if not opt.state & QStyle.StateFlag.State_Enabled:
            context.palette.setCurrentColorGroup(QPalette.ColorGroup.Disabled)
        # Qt draws the checked mark before its outer rectangle; the inherited
        # cell-background brush would fill that rectangle over the mark.
        painter.setBrush(Qt.BrushStyle.NoBrush)
        document.documentLayout().draw(painter, context)
        painter.restore()

    def sizeHint(self, option, index):
        opt = self._option(option, index)
        if opt.rect.width() <= 0 and hasattr(opt.widget, "columnWidth"):
            opt.rect.setWidth(opt.widget.columnWidth(index.column()))
        document, rect = self._layout(opt, index)
        base = super().sizeHint(opt, index)
        vertical_insets = opt.rect.height() - rect.height()
        return QSize(base.width(), max(base.height(), ceil(document.size().height()) + vertical_insets))

    def createEditor(self, parent, option, index):
        editor = RichTextEdit(parent, cellMode=True)
        editor.setFrameShape(QFrame.Shape.NoFrame)
        editor.setStyleSheet("QTextEdit { border: none; padding: 0px; margin: 0px; }")
        editor.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        editor.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        editor.setWordWrapMode(self._wrap_mode)
        editor.setChecklistsEnabled(self._checklists_enabled)
        if self._checklist_labels is not None:
            editor.setChecklistMenuLabels(*self._checklist_labels)
        editor._breeze_finished = False
        editor._breeze_committing = False
        editor._breeze_focus_timer = QTimer(editor)
        editor._breeze_focus_timer.setSingleShot(True)
        editor._breeze_focus_timer.timeout.connect(lambda: self._finish_if_unfocused(editor))
        # Apply the app's QSS before item FontRole/ForegroundRole are installed;
        # a first-show polish would otherwise overwrite those document defaults.
        editor.ensurePolished()
        return editor

    def setEditorData(self, editor, index):
        if editor._breeze_committing:
            return
        text = index.data(Qt.ItemDataRole.EditRole)
        text = "" if text is None else str(text)
        if self._checklists_enabled:
            blocks = _validated_blocks(text, index.data(self._rich_text_blocks_role))
            if blocks is not None:
                editor.setBlocks(blocks)
                return
        editor.setSegments(_validated_segments(text, index.data(self._rich_text_role)))

    def updateEditorGeometry(self, editor, option, index):
        opt = self._option(option, index)
        rect = self._text_rect(opt)
        editor.setFont(opt.font)
        editor.setPalette(opt.palette)
        editor.setGeometry(rect)
        _configure_document(editor.document(), opt.font, rect.width(), self._wrap_mode, opt.displayAlignment)

    def setModelData(self, editor, model, index):
        segments = editor.segments()
        blocks = editor.blocks() if self._checklists_enabled else None
        if blocks is not None:
            segments = _block_segments(blocks)
        text = "".join(segment.text for segment in segments)
        # setItemData can synchronously sort, remove or reset the edited item.
        edited_index = QPersistentModelIndex(index)
        editor._breeze_committing = True
        try:
            roles = {
                int(Qt.ItemDataRole.DisplayRole): text,
                int(Qt.ItemDataRole.EditRole): text,
                self._rich_text_role: segments,
            }
            if blocks is not None:
                roles[self._rich_text_blocks_role] = blocks
            accepted = model.setItemData(index, roles)
            if accepted and edited_index.isValid():
                self.modelUpdated.emit(QModelIndex(edited_index))
        finally:
            editor._breeze_committing = False

    def editorEvent(self, event, model, option, index):
        mouse_types = (QEvent.Type.MouseButtonPress, QEvent.Type.MouseButtonRelease,
                       QEvent.Type.MouseButtonDblClick)
        if (not self._checklists_enabled or event.type() not in mouse_types
                or event.button() != Qt.MouseButton.LeftButton):
            return super().editorEvent(event, model, option, index)
        opt = self._option(option, index)
        document, rect = self._layout(opt, index)
        point = event.position()
        block = (_marker_at(document, point - _document_origin(document, rect, opt.displayAlignment))
                 if rect.contains(point.toPoint()) else None)
        flags = index.flags()
        editable = (bool(flags & Qt.ItemFlag.ItemIsEditable)
                    and bool(flags & Qt.ItemFlag.ItemIsEnabled)
                    and bool(opt.state & QStyle.StateFlag.State_Enabled))
        if event.type() == QEvent.Type.MouseButtonPress:
            self._checklist_pressed = ((QPersistentModelIndex(index), block.blockNumber())
                                       if block is not None and editable else None)
        elif event.type() == QEvent.Type.MouseButtonDblClick:
            self._checklist_pressed = None
        else:
            pressed = self._checklist_pressed
            self._checklist_pressed = None
            if pressed is not None:
                if (block is not None and editable and pressed[0] == index
                        and pressed[1] == block.blockNumber()):
                    self._toggle_model_block(model, index, block.blockNumber())
                return True
        if block is not None:
            return True
        return super().editorEvent(event, model, option, index)

    def _toggle_model_block(self, model, index, number):
        text = index.data(Qt.ItemDataRole.DisplayRole)
        text = "" if text is None else str(text)
        blocks = _validated_blocks(text, index.data(self._rich_text_blocks_role))
        if blocks is None or not 0 <= number < len(blocks) or blocks[number].checked is None:
            return
        changed = blocks[number]
        checked = not changed.checked
        blocks = list(blocks)
        blocks[number] = RichTextBlock(changed.segments, checked, separatorColor=changed.separatorColor)
        blocks = tuple(blocks)
        segments = _block_segments(blocks)
        edited_index = QPersistentModelIndex(index)
        accepted = model.setItemData(index, {
            int(Qt.ItemDataRole.DisplayRole): text,
            int(Qt.ItemDataRole.EditRole): text,
            self._rich_text_role: segments,
            self._rich_text_blocks_role: blocks,
        })
        if accepted and edited_index.isValid():
            self.modelUpdated.emit(QModelIndex(edited_index))
            if edited_index.isValid():
                self.checklistItemToggled.emit(QModelIndex(edited_index), number, checked)

    def _finish(self, editor, hint=TableItemDelegate.EndEditHint.NoHint, cancel=False):
        if not isValid(editor) or editor._breeze_finished:
            return
        editor._breeze_finished = True
        if not cancel:
            self.commitData.emit(editor)
        self.closeEditor.emit(editor, hint)

    def _finish_if_unfocused(self, editor):
        if not isValid(editor) or editor.isFormattingPopupOpen():
            return
        focus = QApplication.focusWidget()
        if focus is editor or (focus is not None and editor.isAncestorOf(focus)):
            return
        self._finish(editor)

    def eventFilter(self, editor, event):
        if not isinstance(editor, RichTextEdit):
            return super().eventFilter(editor, event)
        if event.type() == QEvent.Type.FocusOut:
            if not editor.isFormattingPopupOpen():
                editor._breeze_focus_timer.start(0)
            return False
        if event.type() == QEvent.Type.KeyPress:
            if event.key() in (Qt.Key.Key_Tab, Qt.Key.Key_Backtab):
                backwards = event.key() == Qt.Key.Key_Backtab or bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier)
                hint = self.EndEditHint.EditPreviousItem if backwards else self.EndEditHint.EditNextItem
                self._finish(editor, hint)
                return True
            if event.key() == Qt.Key.Key_Escape:
                self._finish(editor, self.EndEditHint.RevertModelCache, cancel=True)
                return True
            # QTextEdit owns Return/Enter (new paragraph), including shortcuts.
            return False
        return False
