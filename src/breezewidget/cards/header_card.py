from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLayout, QVBoxLayout, QWidget

from ..layout._utils import clear_layout
from ..theme import getPalette
from ..widgets import StrongBodyLabel
from .card import CardWidget


class HeaderCardWidget(CardWidget):
    """Card with a fixed header row and a content area below it."""

    def __init__(self, title: str = "", parent: QWidget | None = None):
        super().__init__(parent)
        self.setMinimumHeight(88)

        self.titleLabel = StrongBodyLabel(title, self)
        self.headerLayout = QHBoxLayout()
        self.headerLayout.setContentsMargins(0, 0, 0, 0)
        self.headerLayout.setSpacing(8)
        self.headerLayout.addWidget(self.titleLabel)
        self.headerLayout.addStretch(1)

        self._separator = QFrame(self)
        self._separator.setFixedHeight(1)
        self._separator.setFrameShape(QFrame.Shape.NoFrame)

        self.viewLayout = QVBoxLayout()
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.setSpacing(10)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 16)
        root.setSpacing(12)
        root.addLayout(self.headerLayout)
        root.addWidget(self._separator)
        root.addLayout(self.viewLayout)

        self.refreshTheme()

    def title(self) -> str:
        return self.titleLabel.text()

    def setTitle(self, title: str) -> None:
        self.titleLabel.setText(title)

    def addWidget(
        self,
        widget: QWidget,
        stretch: int = 0,
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag(0),
    ) -> None:
        self.viewLayout.addWidget(widget, stretch, alignment)

    def addLayout(self, layout: QLayout, stretch: int = 0) -> None:
        self.viewLayout.addLayout(layout, stretch)

    def setContentWidget(self, widget: QWidget) -> None:
        clear_layout(self.viewLayout)
        self.viewLayout.addWidget(widget)

    def refreshTheme(self) -> None:
        palette = getPalette()
        self._separator.setStyleSheet(f"background: {palette.border1}; border: none;")
