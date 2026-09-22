"""TeachingTip — flyout preset with title, content, optional buttons."""
from __future__ import annotations

from typing import Any, Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ..constants import PROP_TEACHING_TIP
from ..icons._themed import ThemedIcon
from ..widgets.button import PushButton, TransparentToolButton
from ..widgets.label import BodyLabel, StrongBodyLabel
from .animation import FlyoutAnimationType
from .flyout import Flyout, FlyoutPlacement


class TeachingTip(Flyout):
    """Flyout preset for short on-screen guidance.

    Layout:
        [icon]  Title (StrongBodyLabel)        [close]
                Content (BodyLabel, word-wrapped)
                [primary action] [secondary action] ...
    """

    def __init__(
        self,
        title: str,
        content: str,
        target: QWidget | None = None,
        parent: QWidget | None = None,
        icon: Any = None,
        placement: FlyoutPlacement = FlyoutPlacement.BOTTOM,
        animation_type: FlyoutAnimationType = FlyoutAnimationType.SLIDE_DOWN,
        closable: bool = True,
    ):
        super().__init__(
            target=target,
            parent=parent,
            placement=placement,
            animation_type=animation_type,
        )
        self.setProperty(PROP_TEACHING_TIP, True)

        body = self._buildBody(title, content, icon, closable)
        self.setContent(body)

    def _buildBody(self, title: str, content: str, icon: Any, closable: bool) -> QWidget:
        body = QWidget(self._body)
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(8)

        body_layout.addLayout(self._buildHeader(body, title, content, icon, closable))
        self._button_row = self._buildActionRow()
        body_layout.addLayout(self._button_row)
        return body

    def _buildHeader(
        self,
        body: QWidget,
        title: str,
        content: str,
        icon: Any,
        closable: bool,
    ) -> QHBoxLayout:
        head_row = QHBoxLayout()
        head_row.setContentsMargins(0, 0, 0, 0)
        head_row.setSpacing(10)

        if icon is not None:
            self._icon_label = QLabel(body)
            self._icon_label.setFixedSize(20, 20)
            self._icon = ThemedIcon(
                lambda rendered: self._icon_label.setPixmap(rendered.pixmap(20, 20)),
                size=20,
            )
            self._icon.set(icon)
            head_row.addWidget(self._icon_label, 0, Qt.AlignmentFlag.AlignTop)
        else:
            self._icon_label = None
            self._icon = None

        text_column = QVBoxLayout()
        text_column.setContentsMargins(0, 0, 0, 0)
        text_column.setSpacing(2)
        self._title_label = StrongBodyLabel(title, body)
        text_column.addWidget(self._title_label)
        self._content_label = BodyLabel(content, body)
        self._content_label.setWordWrap(True)
        text_column.addWidget(self._content_label)
        head_row.addLayout(text_column, 1)

        if closable:
            from ..icons import BreezeIcon
            self._close_button = TransparentToolButton(BreezeIcon.CLOSE, body)
            self._close_button.setFixedSize(24, 24)
            self._close_button.clicked.connect(self.close)
            head_row.addWidget(self._close_button, 0, Qt.AlignmentFlag.AlignTop)
        else:
            self._close_button = None

        return head_row

    def _buildActionRow(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setContentsMargins(0, 6, 0, 0)
        row.setSpacing(8)
        row.addStretch(1)
        self._has_buttons = False
        return row

    # --- public API -----------------------------------------------------

    def setTitle(self, title: str) -> None:
        self._title_label.setText(title)

    def setText(self, content: str) -> None:
        self._content_label.setText(content)

    def addButton(self, text: str, callback: Callable[[], None] | None = None) -> PushButton:
        button = PushButton(text, self._body)
        if callback is not None:
            button.clicked.connect(lambda checked=False, cb=callback: cb())
        button.clicked.connect(self.close)
        # Insert before the trailing stretch
        self._button_row.insertWidget(self._button_row.count() - 1, button)
        self._has_buttons = True
        return button

    def refreshTheme(self) -> None:
        if self._icon is not None:
            self._icon.refresh()

    @classmethod
    def make(
        cls,
        title: str,
        content: str,
        target: QWidget,
        parent: QWidget | None = None,
        icon: Any = None,
        placement: FlyoutPlacement = FlyoutPlacement.BOTTOM,
        animation_type: FlyoutAnimationType = FlyoutAnimationType.SLIDE_DOWN,
    ) -> "TeachingTip":
        """Create + show a TeachingTip in one call."""
        tip = cls(
            title=title,
            content=content,
            target=target,
            parent=parent,
            icon=icon,
            placement=placement,
            animation_type=animation_type,
        )
        tip.exec()
        return tip
