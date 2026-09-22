from __future__ import annotations

from enum import Enum

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ..constants import PROP_INFO_BAR
from ..icons import BreezeIcon
from ..icons._themed import ThemedIcon
from ..widgets.button import TransparentToolButton
from ..widgets.label import BodyLabel, StrongBodyLabel


class InfoBarPosition(str, Enum):
    TOP = "top"
    TOP_RIGHT = "topRight"
    TOP_LEFT = "topLeft"
    BOTTOM = "bottom"
    BOTTOM_RIGHT = "bottomRight"
    BOTTOM_LEFT = "bottomLeft"


class InfoBar(QWidget):
    def __init__(
        self,
        icon,
        title: str,
        content: str,
        parent: QWidget | None = None,
        duration: int = 3000,
        closable: bool = True,
    ):
        super().__init__(parent)
        self.setProperty(PROP_INFO_BAR, True)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 10, 10)
        layout.setSpacing(10)

        self._icon_label = QLabel(self)
        self._icon = ThemedIcon(lambda rendered: self._icon_label.setPixmap(rendered.pixmap(20, 20)), size=20)
        self._icon.set(icon)
        layout.addWidget(self._icon_label, 0, Qt.AlignmentFlag.AlignTop)

        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)
        if title:
            text_layout.addWidget(StrongBodyLabel(title, self))
        if content:
            text_layout.addWidget(BodyLabel(content, self))
        layout.addLayout(text_layout, 1)

        if closable:
            close_button = TransparentToolButton(BreezeIcon.CLOSE, self)
            close_button.clicked.connect(self.close)
            layout.addWidget(close_button, 0, Qt.AlignmentFlag.AlignTop)

        if duration > 0:
            QTimer.singleShot(duration, self.close)

    def refreshTheme(self) -> None:
        self._icon.refresh()

    @classmethod
    def new(
        cls,
        icon,
        title: str,
        content: str,
        parent: QWidget | None = None,
        duration: int = 3000,
        position: InfoBarPosition = InfoBarPosition.TOP_RIGHT,
        closable: bool = True,
    ) -> "InfoBar":
        bar = cls(icon, title, content, parent, duration, closable)
        bar.adjustSize()
        if parent is not None:
            _place_infobar(bar, parent, position)
        bar.show()
        return bar

    @classmethod
    def info(cls, title: str, content: str, parent: QWidget | None = None, duration: int = 3000, **kwargs) -> "InfoBar":
        return cls.new(BreezeIcon.INFO, title, content, parent, duration, **kwargs)

    @classmethod
    def success(cls, title: str, content: str, parent: QWidget | None = None, duration: int = 3000, **kwargs) -> "InfoBar":
        return cls.new(BreezeIcon.CHECK, title, content, parent, duration, **kwargs)

    @classmethod
    def warning(cls, title: str, content: str, parent: QWidget | None = None, duration: int = 3000, **kwargs) -> "InfoBar":
        return cls.new(BreezeIcon.WARNING, title, content, parent, duration, **kwargs)

    @classmethod
    def error(cls, title: str, content: str, parent: QWidget | None = None, duration: int = 3000, **kwargs) -> "InfoBar":
        return cls.new(BreezeIcon.ERROR, title, content, parent, duration, **kwargs)


def _place_infobar(bar: QWidget, parent: QWidget, position: InfoBarPosition) -> None:
    margin = 18
    width = min(max(bar.sizeHint().width(), 320), max(parent.width() - margin * 2, 320))
    height = bar.sizeHint().height()
    bar.resize(width, height)

    if position in {InfoBarPosition.TOP, InfoBarPosition.BOTTOM}:
        x = (parent.width() - width) // 2
    elif position in {InfoBarPosition.TOP_LEFT, InfoBarPosition.BOTTOM_LEFT}:
        x = margin
    else:
        x = parent.width() - width - margin

    if position in {InfoBarPosition.BOTTOM, InfoBarPosition.BOTTOM_LEFT, InfoBarPosition.BOTTOM_RIGHT}:
        y = parent.height() - height - margin
    else:
        y = margin

    bar.move(max(margin, x), max(margin, y))
