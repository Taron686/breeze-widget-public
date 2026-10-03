"""Color-only document transport shared by editors and item delegates."""
from __future__ import annotations

from dataclasses import dataclass
import re

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QImage, QTextCharFormat, QTextCursor, QTextDocument


RICH_TEXT_ROLE = int(Qt.ItemDataRole.UserRole) + 1


@dataclass(frozen=True)
class RichTextSegment:
    """Text with an optional explicit RGB foreground (otherwise theme/item color).

    Paragraph boundaries are ``\n``; U+2028 is a soft break in one paragraph.
    Segment boundaries carry no paragraph semantics.
    """

    text: str
    color: str | None = None

    def __post_init__(self):
        if not isinstance(self.text, str):
            raise TypeError("text must be a string")
        if self.color is not None:
            if not isinstance(self.color, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", self.color):
                raise ValueError("color must be #rrggbb or None")
            object.__setattr__(self, "color", self.color.lower())


def _validated_segments(text, data):
    if (isinstance(data, (tuple, list))
            and all(isinstance(segment, RichTextSegment) for segment in data)
            and "".join(segment.text for segment in data) == text):
        return tuple(data)
    return (RichTextSegment(text),)


def _set_segments(document, segments):
    document.clear()
    cursor = QTextCursor(document)
    for segment in segments:
        fmt = QTextCharFormat()
        if segment.color is not None:
            fmt.setForeground(QColor(segment.color))
        cursor.insertText(segment.text, fmt)
    document.clearUndoRedoStacks()


def _segments(document):
    result = []

    def append(text, fmt):
        color = fmt.foreground().color().name() if fmt.hasProperty(QTextCharFormat.Property.ForegroundBrush) else None
        if result and result[-1].color == color:
            result[-1] = RichTextSegment(result[-1].text + text, color)
        elif text:
            result.append(RichTextSegment(text, color))

    # Fragments preserve format boundaries even inside a grapheme, as well as
    # complete Unicode text, NBSP and soft breaks (unlike toPlainText()).
    block = document.begin()
    while block.isValid():
        fragments = block.begin()
        while not fragments.atEnd():
            fragment = fragments.fragment()
            append(fragment.text(), fragment.charFormat())
            fragments += 1
        if block.next().isValid():
            # Qt stores the preceding paragraph separator's format on the
            # following block, separately from that block's first text run.
            append("\n", block.next().charFormat())
        block = block.next()
    return tuple(result)


def _configure_document(document, font, width, wrap_mode, alignment=Qt.AlignmentFlag.AlignLeft):
    document.setDocumentMargin(0)
    document.setDefaultFont(font)
    text_option = document.defaultTextOption()
    text_option.setWrapMode(wrap_mode)
    text_option.setAlignment(alignment & Qt.AlignmentFlag.AlignHorizontal_Mask)
    document.setDefaultTextOption(text_option)
    document.setTextWidth(max(1, width))


def _document(segments, font, width, wrap_mode, alignment, paint_device=None):
    document = QTextDocument()
    if paint_device is not None:
        # PySide ties a QWidget paint-device wrapper to the temporary document
        # and invalidates its child wrappers when that document dies. Retain an
        # independent metrics device with the same logical DPI instead.
        metrics = QImage(1, 1, QImage.Format.Format_ARGB32_Premultiplied)
        metrics.setDotsPerMeterX(round(paint_device.logicalDpiX() / 0.0254))
        metrics.setDotsPerMeterY(round(paint_device.logicalDpiY() / 0.0254))
        document._breeze_metrics_device = metrics
        document.documentLayout().setPaintDevice(metrics)
    _configure_document(document, font, width, wrap_mode, alignment)
    _set_segments(document, segments)
    return document
