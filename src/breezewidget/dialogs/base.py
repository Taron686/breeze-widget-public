"""MessageBoxBase — common frame for all Breeze dialogs."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)

from ..constants import PROP_DIALOG
from ._content import _DialogContentMixin, _TextDialogMixin


class MessageBoxBase(_DialogContentMixin, QDialog):
    """Common Breeze dialog frame: title + scrollable view + button row.

    Subclasses populate :attr:`viewLayout` with their content widgets.
    Two pre-wired buttons are exposed on the instance:

      * :attr:`yesButton`   — primary action; ``clicked`` connects to
        :meth:`QDialog.accept`.
      * :attr:`cancelButton` — secondary action; ``clicked`` connects to
        :meth:`QDialog.reject`.

    Override :meth:`yesButtonText` / :meth:`cancelButtonText` (or call
    :meth:`setYesText` / :meth:`setCancelText`) to change the labels.
    Hide ``cancelButton`` for single-action dialogs.
    """

    def __init__(self, title: str | QWidget | None = "", parent: QWidget | None = None) -> None:
        if isinstance(title, QWidget):
            parent = title
            title = ""
        title = "" if title is None else str(title)
        super().__init__(parent)
        self.setProperty(PROP_DIALOG, True)
        self.setModal(True)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowTitle(title)

        self._initDialogContent(title, shadow_blur=40, shadow_offset=8, shadow_alpha=120)

        self._outer = QVBoxLayout(self)
        self._outer.setContentsMargins(24, 24, 24, 24)
        self._outer.setSpacing(0)
        self._outer.addWidget(self._card)

        self.resize(420, self.sizeHint().height())

    @property
    def widget(self) -> QWidget:
        return self

    @property
    def buttonLayout(self) -> QHBoxLayout:
        return self._buttonRow


class Dialog(_TextDialogMixin, MessageBoxBase):
    """Title + plain text body + Yes/Cancel buttons."""

    def __init__(
        self,
        title: str = "",
        content: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(title, parent)
        self._initTextContent(content)
