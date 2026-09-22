from __future__ import annotations

from PySide6.QtWidgets import QPlainTextEdit, QTextEdit, QWidget


class TextEdit(QTextEdit):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setMinimumHeight(90)


class PlainTextEdit(QPlainTextEdit):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setMinimumHeight(90)
