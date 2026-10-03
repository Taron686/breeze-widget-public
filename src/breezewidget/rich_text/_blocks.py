"""Paragraph transport and native QTextList checklist state."""
from __future__ import annotations

from dataclasses import dataclass, field

from PySide6.QtGui import QTextBlockFormat, QTextCharFormat, QTextCursor, QTextListFormat

from ._model import RichTextSegment, _set_segments


RICH_TEXT_BLOCKS_ROLE = 258


@dataclass(frozen=True)
class RichTextBlock:
    """One paragraph; separatorColor colors its following LF, if any.

    checked=None is ordinary text, False/True is an open/completed task.
    U+2028 soft breaks are allowed within segments; paragraph separators are not.
    """

    segments: tuple[RichTextSegment, ...]
    checked: bool | None = None
    separatorColor: str | None = field(default=None, kw_only=True)

    def __post_init__(self):
        if not isinstance(self.segments, tuple) or not all(
                isinstance(segment, RichTextSegment) for segment in self.segments):
            raise TypeError("segments must be a tuple of RichTextSegment")
        if self.checked is not None and type(self.checked) is not bool:
            raise TypeError("checked must be bool or None")
        if any(any(char in segment.text for char in "\n\r\u2029") for segment in self.segments):
            raise ValueError("block segments cannot contain paragraph separators")
        color = RichTextSegment("", self.separatorColor).color
        object.__setattr__(self, "separatorColor", color)


def _append_segment(result, text, color):
    if not text:
        return
    if result and result[-1].color == color:
        result[-1] = RichTextSegment(result[-1].text + text, color)
    else:
        result.append(RichTextSegment(text, color))


def _block_segments(blocks):
    result = []
    for number, block in enumerate(blocks):
        for segment in block.segments:
            _append_segment(result, segment.text, segment.color)
        if number + 1 < len(blocks):
            _append_segment(result, "\n", block.separatorColor)
    return tuple(result)


def _validated_blocks(text, data):
    if not isinstance(data, (tuple, list)) or not data:
        return None
    if not all(isinstance(block, RichTextBlock) for block in data):
        return None
    if "".join(segment.text for segment in _block_segments(data)) != text:
        return None
    return tuple(data)


def _checked(block):
    if block.textList() is None:
        return None
    marker = block.blockFormat().marker()
    if marker == QTextBlockFormat.MarkerType.Checked:
        return True
    if marker == QTextBlockFormat.MarkerType.Unchecked:
        return False
    return None


def _set_checked(block, checked):
    cursor = QTextCursor(block)
    fmt = block.blockFormat()
    if checked is None:
        if block.textList() is not None:
            block.textList().remove(block)
        fmt.setObjectIndex(-1)
        fmt.setIndent(0)
        fmt.setMarker(QTextBlockFormat.MarkerType.NoMarker)
    else:
        if block.textList() is None:
            list_format = QTextListFormat()
            list_format.setStyle(QTextListFormat.Style.ListDisc)
            list_format.setIndent(1)
            cursor.createList(list_format)
            fmt = block.blockFormat()
        fmt.setMarker(QTextBlockFormat.MarkerType.Checked if checked else
                      QTextBlockFormat.MarkerType.Unchecked)
    cursor.setBlockFormat(fmt)


def _set_blocks(document, blocks):
    blocks = tuple(blocks)
    if not all(isinstance(block, RichTextBlock) for block in blocks):
        raise TypeError("blocks must contain RichTextBlock")
    _set_segments(document, _block_segments(blocks))
    block = document.begin()
    for data in blocks:
        _set_checked(block, data.checked)
        block = block.next()
    document.clearUndoRedoStacks()


def _format_color(fmt):
    return (fmt.foreground().color().name()
            if fmt.hasProperty(QTextCharFormat.Property.ForegroundBrush) else None)


def _blocks(document):
    result = []
    block = document.begin()
    while block.isValid():
        segments = []
        fragments = block.begin()
        while not fragments.atEnd():
            fragment = fragments.fragment()
            _append_segment(segments, fragment.text(), _format_color(fragment.charFormat()))
            fragments += 1
        separator = _format_color(block.next().charFormat()) if block.next().isValid() else None
        result.append(RichTextBlock(tuple(segments), _checked(block), separatorColor=separator))
        block = block.next()
    return tuple(result)
