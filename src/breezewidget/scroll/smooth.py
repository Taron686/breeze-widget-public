from __future__ import annotations

from PySide6.QtCore import QAbstractAnimation, QEasingCurve, QPropertyAnimation
from PySide6.QtWidgets import QScrollArea, QWidget


class SmoothScrollArea(QScrollArea):
    """QScrollArea with animated mouse-wheel scrolling.

    Wheel events are intercepted and the scroll position is animated
    instead of jumping instantly.  Multiple consecutive wheel notches
    stack onto the running animation's end value for a fluid feel.

    Call ``setSmoothing(False)`` to fall back to the standard Qt behaviour.

    Usage::

        area = SmoothScrollArea()
        area.setWidget(my_content_widget)
        area.setWidgetResizable(True)
    """

    _DURATION_MS = 250

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._smooth = True

        self._v_anim = QPropertyAnimation(self.verticalScrollBar(), b"value", self)
        self._v_anim.setDuration(self._DURATION_MS)
        self._v_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._h_anim = QPropertyAnimation(self.horizontalScrollBar(), b"value", self)
        self._h_anim.setDuration(self._DURATION_MS)
        self._h_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def setSmoothing(self, enabled: bool) -> None:
        """Enable or disable animated scrolling."""
        self._smooth = enabled

    def smoothing(self) -> bool:
        """Return ``True`` when animated scrolling is active."""
        return self._smooth

    # ------------------------------------------------------------------
    # Event override
    # ------------------------------------------------------------------

    def wheelEvent(self, event) -> None:
        if not self._smooth:
            super().wheelEvent(event)
            return

        dy = -event.angleDelta().y()
        dx = -event.angleDelta().x()

        if dy != 0:
            self._animateAxis(self.verticalScrollBar(), self._v_anim, dy)
        if dx != 0:
            self._animateAxis(self.horizontalScrollBar(), self._h_anim, dx)

        event.accept()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _animateAxis(self, scrollbar, anim, angle_delta: int) -> None:
        """Animate *scrollbar* by the equivalent of *angle_delta* wheel units."""
        # 3 lines per notch × singleStep; minimum 20 px per line so tiny
        # steps still feel responsive even with very small singleStep values.
        step = max(scrollbar.singleStep(), 20) * 3
        delta = int(angle_delta / 120 * step)

        # Stack on the running animation's end value so rapid scrolling
        # accelerates instead of restarting from the current position.
        if anim.state() == QAbstractAnimation.State.Running:
            base = int(anim.endValue())
        else:
            base = scrollbar.value()

        target = max(scrollbar.minimum(), min(scrollbar.maximum(), base + delta))

        # Nothing to animate.
        if target == scrollbar.value() and anim.state() != QAbstractAnimation.State.Running:
            return

        anim.stop()
        anim.setStartValue(scrollbar.value())
        anim.setEndValue(target)
        anim.start()
