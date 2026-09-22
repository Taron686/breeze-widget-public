from __future__ import annotations

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLineEdit, QWidget

from ..icons import BreezeIcon
from ..icons._themed import ThemedActionIcons


class LineEdit(QLineEdit):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setClearButtonEnabled(True)
        self.setMinimumHeight(34)


class SearchLineEdit(LineEdit):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setPlaceholderText("Search")
        self._icons = ThemedActionIcons()
        self._searchAction = self.addAction(QIcon(), QLineEdit.ActionPosition.LeadingPosition)
        self._icons.set(self._searchAction, BreezeIcon.SEARCH)

    def refreshTheme(self) -> None:
        self._icons.refresh()


class PasswordLineEdit(LineEdit):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setEchoMode(QLineEdit.EchoMode.Password)
