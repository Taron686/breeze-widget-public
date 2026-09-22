from __future__ import annotations

from PySide6.QtWidgets import QWidget

from .base import Dialog


class MessageBox(Dialog):
    """Compact message dialog without a body title header.

    Same layout as :class:`Dialog` (title bar with close button, body
    text, button-group footer), but the big body title is hidden so
    short notifications read as a single content block.  The constructor
    still accepts a ``title`` argument for backward compatibility — it
    is forwarded to ``setWindowTitle`` so it shows up in the title bar,
    but the in-body ``titleLabel`` stays hidden.
    """

    def __init__(
        self,
        title: str = "",
        content: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(title, content, parent)
        # Drop the entire top chrome — MessageBox is a compact alert,
        # not a window that needs caption/close/drag affordances.
        self.titleBar.hide()
        self.titleLabel.hide()
