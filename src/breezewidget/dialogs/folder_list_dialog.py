"""FolderListDialog — manage a list of folder paths via add/remove buttons."""
from __future__ import annotations

from typing import Iterable

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QListWidget,
    QWidget,
)

from ..widgets.button import PushButton
from .base import MessageBoxBase


class FolderListDialog(MessageBoxBase):
    """Edit a list of folders.

    The dialog shows the current paths in a :class:`QListWidget`.  Use
    "Add" to spawn a folder picker, or "Remove" to drop the selected
    row.  ``foldersChanged`` fires whenever the list contents mutate.
    Final list available via :meth:`folders`.
    """

    foldersChanged = Signal(list)

    def __init__(
        self,
        folders: Iterable[str] = (),
        title: str = "Folders",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(title, parent)
        self._listWidget = QListWidget(self)
        self.addContentWidget(self._listWidget)
        for path in folders:
            self._listWidget.addItem(path)

        controls = QHBoxLayout()
        self.addButton = PushButton("Add", self)
        self.removeButton = PushButton("Remove", self)
        controls.addWidget(self.addButton)
        controls.addWidget(self.removeButton)
        controls.addStretch(1)
        self.addContentLayout(controls)

        self.addButton.clicked.connect(self._onAdd)
        self.removeButton.clicked.connect(self._onRemove)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def folders(self) -> list[str]:
        return [self._listWidget.item(i).text() for i in range(self._listWidget.count())]

    def setFolders(self, folders: Iterable[str]) -> None:
        self._listWidget.clear()
        for path in folders:
            self._listWidget.addItem(path)
        self.foldersChanged.emit(self.folders())

    def addFolder(self, path: str) -> None:
        if not path:
            return
        if path in self.folders():
            return
        self._listWidget.addItem(path)
        self.foldersChanged.emit(self.folders())

    def listWidget(self) -> QListWidget:
        return self._listWidget

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _onAdd(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select folder")
        if path:
            self.addFolder(path)

    def _onRemove(self) -> None:
        row = self._listWidget.currentRow()
        if row < 0:
            return
        item = self._listWidget.takeItem(row)
        del item
        self.foldersChanged.emit(self.folders())
