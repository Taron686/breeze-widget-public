"""Long-lived progress tooltip — shows a state until the work is done."""
from __future__ import annotations

from PySide6.QtCore import QPoint, QTimer, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from shiboken6 import isValid

from ..constants import PROP_STATE_TOOLTIP
from ..icons import BreezeIcon
from ..theme import getPalette
from ..widgets.button import TransparentToolButton
from ..widgets.label import BodyLabel, StrongBodyLabel
from .badge import IconInfoBadge
from .progress_ring import IndeterminateProgressRing


class StateToolTip(QWidget):
    """Floating tooltip that announces a long-running task and its result.

    Lifecycle:
        ``StateToolTip(title, content, parent)`` shows a spinning ring while the
        work runs. Call :meth:`setState(True)` when the task completes — the
        ring is replaced by a check-mark icon and the tooltip auto-closes after
        a short delay (configurable via :meth:`setAutoCloseDelay`).
    """

    closed = Signal()

    def __init__(
        self,
        title: str,
        content: str,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.setProperty(PROP_STATE_TOOLTIP, True)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        flags = Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint
        if parent is None:
            flags |= Qt.WindowType.Window
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self._title = StrongBodyLabel(title, self)
        self._content = BodyLabel(content, self)
        self._spinner = IndeterminateProgressRing(self)
        self._spinner.setFixedSize(22, 22)
        self._done_icon = IconInfoBadge(BreezeIcon.CHECK, self, variant="success", size=18)
        self._done_icon.hide()
        self._close_button = TransparentToolButton(BreezeIcon.CLOSE, self)
        self._close_button.setFixedSize(24, 24)
        self._close_button.clicked.connect(self.close)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 12, 10, 12)
        layout.setSpacing(10)
        layout.addWidget(self._spinner, 0, Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self._done_icon, 0, Qt.AlignmentFlag.AlignVCenter)

        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)
        text_layout.addWidget(self._title)
        text_layout.addWidget(self._content)
        layout.addLayout(text_layout, 1)
        layout.addWidget(self._close_button, 0, Qt.AlignmentFlag.AlignTop)

        self._is_done = False
        self._auto_close_delay = 1500
        self.adjustSize()
        if parent is not None:
            self._placeNextTo(parent)

    # --- public API ----------------------------------------------------------

    def setTitle(self, title: str) -> None:
        self._title.setText(title)

    def setContent(self, content: str) -> None:
        self._content.setText(content)

    def setState(self, done: bool) -> None:
        done = bool(done)
        if not isValid(self):
            return
        if done == self._is_done:
            return
        self._is_done = done
        if done:
            self._spinner.stop()
            self._spinner.hide()
            self._done_icon.show()
            if self._auto_close_delay > 0:
                QTimer.singleShot(self._auto_close_delay, self._safeClose)
        else:
            self._done_icon.hide()
            self._spinner.show()
            self._spinner.start()

    def _safeClose(self) -> None:
        if isValid(self):
            self.close()

    def isDone(self) -> bool:
        return self._is_done

    def setAutoCloseDelay(self, msec: int) -> None:
        self._auto_close_delay = max(0, int(msec))

    # --- painting ------------------------------------------------------------

    def paintEvent(self, event) -> None:
        del event
        palette = getPalette()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = self.rect().adjusted(0, 0, -1, -1)
        painter.setPen(QPen(QColor(palette.border1), 1))
        painter.setBrush(QColor(palette.surface2))
        painter.drawRoundedRect(rect, 8, 8)
        painter.end()

    # --- helpers -------------------------------------------------------------

    def _placeNextTo(self, parent: QWidget) -> None:
        margin = 18
        size = self.sizeHint()
        global_pos = parent.mapToGlobal(QPoint(parent.width() - size.width() - margin, margin))
        self.move(global_pos)

    def closeEvent(self, event) -> None:
        self.closed.emit()
        super().closeEvent(event)
