"""CommandBar — horizontal action bar with auto-overflow into a RoundMenu."""
from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QFrame, QHBoxLayout, QSizePolicy, QToolButton, QWidget

from ..constants import PROP_COMMAND_BAR, PROP_COMMAND_ITEM
from ..icons import BreezeIcon
from ..icons._themed import ThemedActionIcons, ThemedIcon
from .round_menu import RoundMenu


def _visible_cutoff(
    widths: list[int],
    kinds: list[str],
    available: int,
    more_width: int,
    spacing: int,
) -> int:
    total = sum(widths) + max(0, len(widths) - 1) * spacing
    if total <= available:
        return len(widths)

    budget = available - more_width
    used = 0
    cutoff = 0
    for i, width in enumerate(widths):
        extra = width + (spacing if i > 0 else 0)
        if used + extra > budget:
            break
        used += extra
        cutoff = i + 1

    while cutoff > 0 and kinds[cutoff - 1] == "separator":
        cutoff -= 1
    return cutoff


class CommandBar(QWidget):
    """Horizontal toolbar of :class:`QAction` entries.

    Add commands with :meth:`addAction` (overloaded to also accept
    ``(icon, text, triggered)``) or :meth:`addSeparator`.  When the bar is
    too narrow to show every command, trailing entries collapse into an
    overflow :class:`RoundMenu` accessible through a ``…`` button.
    """

    _SPACING = 2

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty(PROP_COMMAND_BAR, True)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        self._entries: list[tuple[str, QAction | None, QWidget]] = []  # (kind, action, widget)
        self._icons = ThemedActionIcons()
        self._overflow_menu = RoundMenu(parent=self)
        self._more_button = QToolButton(self)
        self._more_button.setProperty(PROP_COMMAND_ITEM, True)
        self._more_icon = ThemedIcon(self._more_button.setIcon)
        self._more_icon.set(BreezeIcon.MORE)
        self._more_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self._more_button.setMenu(self._overflow_menu)
        self._more_button.setAutoRaise(True)
        self._more_button.hide()

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(4, 4, 4, 4)
        self._layout.setSpacing(self._SPACING)
        self._layout.addStretch(1)
        self._layout.addWidget(self._more_button)

    def refreshTheme(self) -> None:
        self._more_icon.refresh()
        self._icons.refresh()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def addAction(self, *args, **kwargs) -> QAction:  # type: ignore[override]
        """Add an action to the bar.

        Accepts either an existing :class:`QAction` or the convenience
        signature ``addAction(icon, text, triggered=None)``.
        """
        if len(args) == 1 and isinstance(args[0], QAction) and not kwargs:
            action = args[0]
        else:
            icon = kwargs.pop("icon", None)
            text = kwargs.pop("text", None)
            triggered = kwargs.pop("triggered", None)
            pos_args = list(args)
            if icon is None and pos_args and not isinstance(pos_args[0], str):
                icon = pos_args.pop(0)
            if text is None and pos_args:
                text = pos_args.pop(0)
            if triggered is None and pos_args:
                triggered = pos_args.pop(0)
            action = QAction(QIcon(), text or "", self)
            self._icons.set(action, icon)
            if triggered is not None:
                action.triggered.connect(lambda checked=False, cb=triggered: cb())
        button = self._makeButton(action)
        self._entries.append(("action", action, button))
        self._insertWidget(button)
        self._relayout()
        return action

    def addSeparator(self) -> QFrame:
        sep = QFrame(self)
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFrameShadow(QFrame.Shadow.Plain)
        sep.setFixedWidth(1)
        sep.setObjectName("breezeCommandSeparator")
        self._entries.append(("separator", None, sep))
        self._insertWidget(sep)
        self._relayout()
        return sep

    def actions(self) -> list[QAction]:  # type: ignore[override]
        return [a for kind, a, _ in self._entries if kind == "action" and a is not None]

    def overflowMenu(self) -> RoundMenu:
        return self._overflow_menu

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _makeButton(self, action: QAction) -> QToolButton:
        button = QToolButton(self)
        button.setProperty(PROP_COMMAND_ITEM, True)
        button.setDefaultAction(action)
        button.setAutoRaise(True)
        button.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon
            if action.text()
            else Qt.ToolButtonStyle.ToolButtonIconOnly
        )
        return button

    def _insertWidget(self, widget: QWidget) -> None:
        # Insert before the trailing stretch (-2) and the more-button (-1).
        index = self._layout.count() - 2
        self._layout.insertWidget(index, widget)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._relayout()

    def _relayout(self) -> None:
        margins = self._layout.contentsMargins()
        available = self.width() - margins.left() - margins.right()
        if available <= 0:
            return

        more_w = self._more_button.sizeHint().width() + self._SPACING

        widths = [w.sizeHint().width() for _, _, w in self._entries]
        kinds = [kind for kind, _, _ in self._entries]
        cutoff = _visible_cutoff(widths, kinds, available, more_w, self._SPACING)

        if cutoff == len(self._entries):
            for _, _, w in self._entries:
                w.setVisible(True)
            self._overflow_menu.clear()
            self._more_button.hide()
            return

        for i, (_, _, w) in enumerate(self._entries):
            w.setVisible(i < cutoff)

        self._overflow_menu.clear()
        for kind, action, _ in self._entries[cutoff:]:
            if kind == "action" and action is not None:
                self._overflow_menu.addAction(action)
            elif kind == "separator":
                self._overflow_menu.addSeparator()
        self._more_button.show()
