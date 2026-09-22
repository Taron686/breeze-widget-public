from __future__ import annotations

from PySide6.QtWidgets import QProgressBar, QWidget


class ProgressBar(QProgressBar):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setMinimumHeight(14)


class IndeterminateProgressBar(ProgressBar):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setRange(0, 0)
