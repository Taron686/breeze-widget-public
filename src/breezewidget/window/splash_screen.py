"""BreezeSplashScreen — pre-window splash with logo and indeterminate progress."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ..constants import PROP_SPLASH_SCREEN
from ..status.progress_ring import IndeterminateProgressRing
from ..theme import applyTheme
from ..widgets.label import SubtitleLabel


class BreezeSplashScreen(QWidget):
    """Frameless top-level widget shown before the main window.

    Displays an icon (large), a title, and an
    :class:`IndeterminateProgressRing`.  Call :meth:`finish` to close
    the splash and raise the supplied window.

    Lifecycle:
      1. ``splash = BreezeSplashScreen(icon, "App")``
      2. ``splash.show()`` — frameless overlay appears, ring spins.
      3. After heavy startup, ``splash.finish(main_window)`` closes the
         splash and shows ``main_window``.
    """

    closed = Signal()

    def __init__(
        self,
        icon: QIcon | QPixmap | None = None,
        title: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setProperty(PROP_SPLASH_SCREEN, True)
        flags = Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)

        self._iconLabel = QLabel(self)
        self._iconLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setIcon(icon)

        self._titleLabel = SubtitleLabel(title, self)
        self._titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._ring = IndeterminateProgressRing(self)
        self._ring.setFixedSize(36, 36)
        ring_row = QHBoxLayout()
        ring_row.addStretch(1)
        ring_row.addWidget(self._ring)
        ring_row.addStretch(1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 36, 36, 36)
        layout.setSpacing(18)
        layout.addStretch(1)
        layout.addWidget(self._iconLabel)
        layout.addWidget(self._titleLabel)
        layout.addLayout(ring_row)
        layout.addStretch(1)

        self.resize(360, 280)
        applyTheme(self)

    # --- public API -----------------------------------------------------

    def setIcon(self, icon: QIcon | QPixmap | None) -> None:
        if icon is None:
            self._iconLabel.clear()
            return
        if isinstance(icon, QIcon):
            pixmap = icon.pixmap(96, 96)
        else:
            pixmap = icon
        self._iconLabel.setPixmap(pixmap)

    def setTitle(self, title: str) -> None:
        self._titleLabel.setText(title)

    def finish(self, window: QWidget | None = None) -> None:
        """Close the splash; if *window* is given, also show + raise it."""
        self.close()
        self.closed.emit()
        if window is not None:
            window.show()
            window.raise_()
            window.activateWindow()
