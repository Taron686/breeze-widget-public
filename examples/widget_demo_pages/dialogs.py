"""Dialogs (4d) — Dialog, MessageBox, ColorDialog, FolderListDialog."""
from __future__ import annotations

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QHBoxLayout, QWidget

from breezewidget import (
    MessageBox,
    PrimaryPushButton,
    PushButton,
)
from breezewidget.dialogs import ColorDialog, Dialog, FolderListDialog, MaskedDialog

from ._gallery import GalleryPage


class DialogsDemoPage(GalleryPage):
    """Phase 4d — Dialog, MessageBox, ColorDialog, FolderListDialog."""

    def __init__(self):
        super().__init__("Dialogs", "breezewidget.dialogs", "dialogs")
        self._color = QColor("#1f6feb")
        self._folders: list[str] = []

        # Plain text Dialog.
        dlg_button = PrimaryPushButton("Open Dialog")
        dlg_button.clicked.connect(self._openDialog)
        self.addExample("Dialog — title + text body + Yes/Cancel", dlg_button)

        # MessageBox alias.
        msg_button = PushButton("Open MessageBox")
        msg_button.clicked.connect(self._openMessageBox)
        self.addExample("MessageBox — alias for Dialog (backward-compatible)", msg_button)

        # MaskedDialog (in-parent overlay with dim mask).
        masked_button = PushButton("Open MaskedDialog")
        masked_button.clicked.connect(self._openMaskedDialog)
        self.addExample(
            "MaskedDialog — overlay inside parent window with dim mask + fade",
            masked_button,
        )

        # ColorDialog with live preview.
        color_row = QWidget()
        color_layout = QHBoxLayout(color_row)
        color_layout.setContentsMargins(0, 0, 0, 0)
        self._colorSwatch = QFrame()
        self._colorSwatch.setFixedSize(40, 28)
        self._refreshSwatch()
        color_button = PushButton("Pick color")
        color_button.clicked.connect(self._openColorDialog)
        color_layout.addWidget(self._colorSwatch)
        color_layout.addWidget(color_button)
        color_layout.addStretch(1)
        self.addExample("ColorDialog — RGB sliders + spin boxes + hex input", color_row)

        # FolderListDialog.
        folder_button = PushButton("Edit folder list")
        folder_button.clicked.connect(self._openFolderDialog)
        self.addExample("FolderListDialog — manage a list of paths", folder_button)

        self.finish()

    def _openDialog(self):
        dlg = Dialog("Confirm action", "This is a Breeze-styled Dialog. Proceed?")
        dlg.setYesText("Yes, do it")
        dlg.setCancelText("Abort")
        dlg.exec()
        self.setStatus("Dialog accepted" if dlg.result() == 1 else "Dialog cancelled")

    def _openMessageBox(self):
        box = MessageBox("", "MessageBox is now a Dialog subclass.")
        box.exec()

    def _openMaskedDialog(self):
        dlg = MaskedDialog(
            "Masked dialog",
            "Dieser Dialog liegt als Overlay direkt im Eltern-Fenster und "
            "dimmt den Hintergrund. Klick auf den dunklen Bereich schliesst "
            "ihn (setClosableOnMaskClicked).",
            parent=self.window(),
        )
        dlg.setYesText("Verstanden")
        dlg.setCancelText("Abbrechen")
        dlg.setClosableOnMaskClicked(True)
        dlg.exec()
        self.setStatus(
            "MaskedDialog accepted" if dlg.result() == 1 else "MaskedDialog cancelled"
        )

    def _openColorDialog(self):
        dlg = ColorDialog(self._color, "Pick accent")
        dlg.colorChanged.connect(self._onColorPicked)
        if dlg.exec() == 1:
            self._color = dlg.color()
        self._refreshSwatch()

    def _onColorPicked(self, color: QColor):
        self._color = color
        self._refreshSwatch()

    def _refreshSwatch(self):
        self._colorSwatch.setStyleSheet(
            f"background: {self._color.name()}; border-radius: 6px;"
        )

    def _openFolderDialog(self):
        dlg = FolderListDialog(self._folders, "Watched folders")
        if dlg.exec() == 1:
            self._folders = dlg.folders()
            self.setStatus(f"{len(self._folders)} folders configured")
