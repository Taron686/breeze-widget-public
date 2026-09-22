from __future__ import annotations

from PySide6.QtWidgets import QLabel, QWidget

from ..constants import (
    LABEL_BODY_STRONG,
    LABEL_CAPTION,
    LABEL_SUBTITLE,
    LABEL_TITLE,
    PROP_LABEL,
)


class BodyLabel(QLabel):
    def __init__(self, text: str = "", parent: QWidget | None = None):
        super().__init__(text, parent)
        self.setWordWrap(True)


class CaptionLabel(BodyLabel):
    def __init__(self, text: str = "", parent: QWidget | None = None):
        super().__init__(text, parent)
        self.setProperty(PROP_LABEL, LABEL_CAPTION)


class StrongBodyLabel(BodyLabel):
    def __init__(self, text: str = "", parent: QWidget | None = None):
        super().__init__(text, parent)
        self.setProperty(PROP_LABEL, LABEL_BODY_STRONG)


class SubtitleLabel(BodyLabel):
    def __init__(self, text: str = "", parent: QWidget | None = None):
        super().__init__(text, parent)
        self.setProperty(PROP_LABEL, LABEL_SUBTITLE)


class TitleLabel(BodyLabel):
    def __init__(self, text: str = "", parent: QWidget | None = None):
        super().__init__(text, parent)
        self.setProperty(PROP_LABEL, LABEL_TITLE)
