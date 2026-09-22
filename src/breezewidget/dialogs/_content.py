"""Shared content construction for window and overlay dialogs."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QVBoxLayout, QWidget

from ..widgets.button import PrimaryPushButton, PushButton
from ..widgets.label import BodyLabel, TitleLabel
from ..window.title_bar import BreezeTitleBar


class _DialogContentMixin:
    def _initDialogContent(self, title: str, *, shadow_blur: int, shadow_offset: int, shadow_alpha: int) -> None:
        self._card = QFrame(self)
        self._card.setProperty("breezeDialogCard", "true")
        self._cardLayout = QVBoxLayout(self._card)
        self._cardLayout.setContentsMargins(0, 0, 0, 0)
        self._cardLayout.setSpacing(0)

        self.titleBar = BreezeTitleBar(self)
        self.titleBar.setProperty("breezeDialogTitleBar", "true")
        self.titleBar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.titleBar.minButton.hide()
        self.titleBar.maxButton.hide()
        self.windowTitleChanged.connect(self.titleBar.setTitle)
        self._cardLayout.addWidget(self.titleBar)

        self._body = QFrame(self._card)
        self._body.setFrameShape(QFrame.Shape.NoFrame)
        # Body must stay transparent so the card's surface2 background
        # (with its 12px rounded corners) shows through.  Without this,
        # the global ``QWidget { background: surface1 }`` rule paints a
        # square opaque rectangle that hides the card's top-corner
        # rounding whenever the title bar isn't covering the top edge
        # (e.g. MessageBox hides its title bar).
        # Scope transparency to the container, not its controls or their popups.
        self._body.setObjectName("_breezeDialogBody")
        self._body.setStyleSheet("QFrame#_breezeDialogBody { background: transparent; }")
        self._bodyLayout = QVBoxLayout(self._body)
        self._bodyLayout.setContentsMargins(24, 18, 24, 18)
        self._bodyLayout.setSpacing(14)
        self._cardLayout.addWidget(self._body, 1)

        self._buttonGroup = QFrame(self._card)
        self._buttonGroup.setProperty("breezeDialogButtonGroup", "true")
        self._buttonGroup.setFrameShape(QFrame.Shape.NoFrame)
        self._buttonRow = QHBoxLayout(self._buttonGroup)
        self._buttonRow.setContentsMargins(24, 18, 24, 18)
        self._buttonRow.setSpacing(12)
        self._cardLayout.addWidget(self._buttonGroup, 0)

        # Drop shadow around the card; outer margin reserves the blur area.
        self._shadow = QGraphicsDropShadowEffect(self._card)
        self._shadow.setBlurRadius(shadow_blur)
        self._shadow.setOffset(0, shadow_offset)
        self._shadow.setColor(QColor(0, 0, 0, shadow_alpha))
        self._card.setGraphicsEffect(self._shadow)

        self.titleLabel = TitleLabel(title, self._body)
        self._bodyLayout.addWidget(self.titleLabel)

        self._viewFrame = QFrame(self._body)
        self._viewFrame.setFrameShape(QFrame.Shape.NoFrame)
        self._viewFrame.setObjectName("_breezeDialogView")
        self._viewFrame.setStyleSheet("QFrame#_breezeDialogView { background: transparent; }")
        self.viewLayout = QVBoxLayout(self._viewFrame)
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.setSpacing(8)
        self._bodyLayout.addWidget(self._viewFrame, 1)

        self.cancelButton = PushButton("Cancel", self._buttonGroup)
        self.yesButton = PrimaryPushButton("OK", self._buttonGroup)
        self.cancelButton.clicked.connect(self.reject)
        self.yesButton.clicked.connect(self.accept)
        self._buttonRow.addWidget(self.yesButton, 1)
        self._buttonRow.addWidget(self.cancelButton, 1)

    def setTitle(self, text: str) -> None:
        self.titleLabel.setText(text)
        self.setWindowTitle(text)

    def setYesText(self, text: str) -> None:
        self.yesButton.setText(text)

    def setCancelText(self, text: str) -> None:
        self.cancelButton.setText(text)

    def addContentWidget(self, widget: QWidget) -> None:
        self.viewLayout.addWidget(widget)

    def addContentLayout(self, layout) -> None:
        self.viewLayout.addLayout(layout)


class _TextDialogMixin:
    def _initTextContent(self, content: str) -> None:
        self.contentLabel = BodyLabel(content, self)
        self.contentLabel.setWordWrap(True)
        self.contentLabel.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.addContentWidget(self.contentLabel)

    def setContentText(self, text: str) -> None:
        self.contentLabel.setText(text)
