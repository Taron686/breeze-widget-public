"""Overlay-style dialog that dims its parent instead of opening a new window.

``MaskedMessageBoxBase`` mirrors :class:`MessageBoxBase` in terms of layout
and styling (BreezeTitleBar, body, button-group footer, rounded card,
drop shadow), but it lives **inside** its parent window: the dialog
itself is a frameless, translucent ``QDialog`` whose geometry tracks the
parent, a semi-transparent mask layer dims the underlying UI, and a
centred card holds the actual content.  It mirrors the
``MessageBox`` pattern from PyQt-Fluent-Widgets.

Use this when a modal interruption should stay visually anchored to a
specific window rather than spawning a new top-level OS window.
"""
from __future__ import annotations

from PySide6.QtCore import (
    QEasingCurve,
    QEvent,
    QObject,
    QPropertyAnimation,
    Qt,
)
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)

from ..constants import PROP_DIALOG
from ._content import _DialogContentMixin, _TextDialogMixin


class MaskedMessageBoxBase(_DialogContentMixin, QDialog):
    """In-parent modal dialog with a dim mask and a centred Breeze card.

    Subclasses populate :attr:`viewLayout` with their content widgets;
    :attr:`yesButton` / :attr:`cancelButton` are pre-wired to
    :meth:`QDialog.accept` / :meth:`QDialog.reject`.
    """

    def __init__(self, title: str = "", parent: QWidget | None = None) -> None:
        if parent is None:
            raise ValueError(
                "MaskedMessageBoxBase requires a parent widget — the mask "
                "covers the parent's geometry."
            )
        super().__init__(parent)
        self.setProperty(PROP_DIALOG, True)
        self.setModal(True)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowTitle(title)

        self._isClosableOnMaskClicked = False
        self._fade_anim: QPropertyAnimation | None = None
        self._suppress_done_anim = False

        # Mask layer covers the entire dialog (= parent).
        self._mask = QWidget(self)
        self._mask.setProperty("breezeDialogMask", "true")
        self._mask.lower()

        self._initDialogContent(title, shadow_blur=60, shadow_offset=10, shadow_alpha=140)

        # Centre the card via stretch-padded layout.
        host = QVBoxLayout(self)
        host.setContentsMargins(0, 0, 0, 0)
        host.setSpacing(0)
        host.addStretch(1)
        center_row = QHBoxLayout()
        center_row.setContentsMargins(0, 0, 0, 0)
        center_row.setSpacing(0)
        center_row.addStretch(1)
        center_row.addWidget(self._card)
        center_row.addStretch(1)
        host.addLayout(center_row)
        host.addStretch(1)

        self._card.setMinimumWidth(360)

        parent.installEventFilter(self)
        self._mask.installEventFilter(self)
        self.resize(parent.size())

    # --- public helpers ------------------------------------------------

    def setClosableOnMaskClicked(self, closable: bool) -> None:
        """When True, a left-click on the dimmed mask rejects the dialog."""
        self._isClosableOnMaskClicked = bool(closable)

    def isClosableOnMaskClicked(self) -> bool:
        return self._isClosableOnMaskClicked

    # --- internals -----------------------------------------------------

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._mask.setGeometry(self.rect())

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if obj is self.parentWidget() and event.type() == QEvent.Type.Resize:
            self.resize(self.parentWidget().size())
            return False
        if obj is self._mask and event.type() == QEvent.Type.MouseButtonRelease:
            if (
                event.button() == Qt.MouseButton.LeftButton
                and self._isClosableOnMaskClicked
            ):
                self.reject()
                return True
        return super().eventFilter(obj, event)

    def showEvent(self, event) -> None:
        # Make sure the mask sits at the right size before the fade.
        self._mask.setGeometry(self.rect())
        # Animate ``windowOpacity`` directly rather than stacking a
        # QGraphicsOpacityEffect on top of the card's own drop-shadow
        # effect — Qt cannot composite two graphics effects from a
        # parent and child widget at the same time and would log
        # "QPainter::begin: A paint device can only be painted by one
        # painter at a time" warnings on every animation tick.
        self.setWindowOpacity(0.0)
        anim = QPropertyAnimation(self, b"windowOpacity", self)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setDuration(200)
        anim.setEasingCurve(QEasingCurve.Type.InSine)
        self._fade_anim = anim
        anim.start()
        super().showEvent(event)

    def done(self, code: int) -> None:
        if self._suppress_done_anim or not self.isVisible():
            super().done(code)
            return
        self.setWindowOpacity(1.0)
        anim = QPropertyAnimation(self, b"windowOpacity", self)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setDuration(100)
        anim.finished.connect(lambda c=code: self._finishDone(c))
        self._fade_anim = anim
        anim.start()

    def _finishDone(self, code: int) -> None:
        self._suppress_done_anim = True
        try:
            QDialog.done(self, code)
        finally:
            self._suppress_done_anim = False
            self.setWindowOpacity(1.0)


class MaskedDialog(_TextDialogMixin, MaskedMessageBoxBase):
    """Title + plain text body + Yes/Cancel buttons, rendered as an overlay."""

    def __init__(
        self,
        title: str = "",
        content: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(title, parent)
        self._initTextContent(content)
