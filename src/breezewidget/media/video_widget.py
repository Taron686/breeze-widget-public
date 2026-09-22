"""VideoWidget — Breeze-styled :class:`QVideoWidget`."""
from __future__ import annotations

from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import QWidget

from ..constants import PROP_VIDEO_WIDGET


class VideoWidget(QVideoWidget):
    """Thin :class:`QVideoWidget` subclass with a Breeze property hook."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty(PROP_VIDEO_WIDGET, True)
