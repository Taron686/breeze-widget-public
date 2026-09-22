""":class:`DropShadowAnimation` — animate a widget's drop-shadow blur radius
on hover/pressed transitions.

Wraps a :class:`QGraphicsDropShadowEffect` attached to the target widget
and exposes a single ``blurRadius`` Q_PROPERTY for animation. The effect
is created and attached automatically; the original effect (if any) is
restored when :meth:`detach` is called.
"""
from __future__ import annotations

from PySide6.QtCore import Property, QEasingCurve, QObject, QPropertyAnimation
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QWidget


DEFAULT_DURATION_MS = 180
DEFAULT_EASING = QEasingCurve.Type.OutCubic


class DropShadowAnimation(QObject):
    """Animate the blur radius of a drop-shadow effect on a widget."""

    def __init__(
        self,
        target: QWidget,
        color: QColor | str = QColor(0, 0, 0, 96),
        offset: tuple[float, float] = (0.0, 2.0),
        initial_blur: float = 0.0,
        duration_ms: int = DEFAULT_DURATION_MS,
        easing: QEasingCurve.Type = DEFAULT_EASING,
    ) -> None:
        super().__init__(target)
        self._target = target
        self._previous_effect = target.graphicsEffect()
        self._effect = QGraphicsDropShadowEffect(target)
        self._effect.setColor(QColor(color))
        self._effect.setOffset(*offset)
        self._effect.setBlurRadius(initial_blur)
        target.setGraphicsEffect(self._effect)
        self._blur = float(initial_blur)
        self._animation = QPropertyAnimation(self, b"blurRadius", self)
        self._animation.setDuration(duration_ms)
        self._animation.setEasingCurve(easing)

    # -- Qt property -------------------------------------------------------

    def _get_blur(self) -> float:
        return self._blur

    def _set_blur(self, value: float) -> None:
        self._blur = float(value)
        self._effect.setBlurRadius(self._blur)

    blurRadius = Property(float, _get_blur, _set_blur)

    # -- public API --------------------------------------------------------

    def animateBlur(self, target_blur: float) -> None:
        """Animate from the current blur radius to *target_blur*."""
        self._animation.stop()
        self._animation.setStartValue(self._blur)
        self._animation.setEndValue(float(target_blur))
        self._animation.start()

    def setDuration(self, ms: int) -> None:
        self._animation.setDuration(int(ms))

    def duration(self) -> int:
        return self._animation.duration()

    def setColor(self, color: QColor | str) -> None:
        self._effect.setColor(QColor(color))

    def setOffset(self, dx: float, dy: float) -> None:
        self._effect.setOffset(dx, dy)

    def effect(self) -> QGraphicsDropShadowEffect:
        return self._effect

    def stop(self) -> None:
        self._animation.stop()

    def detach(self) -> None:
        """Restore the previous graphics effect (if any) and stop animation."""
        self._animation.stop()
        if self._target is not None:
            self._target.setGraphicsEffect(self._previous_effect)


__all__ = ["DropShadowAnimation"]
