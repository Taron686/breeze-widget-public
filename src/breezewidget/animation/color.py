""":class:`BackgroundColorAnimation` — animate a widget's background color
between two :class:`QColor` values via a dynamic ``backgroundColor`` Q_PROPERTY.

Useful for hover/pressed transitions on custom-painted widgets where a
plain QSS ``transition`` is unavailable.
"""
from __future__ import annotations

from PySide6.QtCore import Property, QEasingCurve, QObject, QPropertyAnimation
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget


DEFAULT_DURATION_MS = 180
DEFAULT_EASING = QEasingCurve.Type.OutCubic


class BackgroundColorAnimation(QObject):
    """Animate the background color of a target widget.

    The animation owns a ``backgroundColor`` Q_PROPERTY on this object
    that interpolates between the start and end :class:`QColor`. On every
    tick the widget's stylesheet is refreshed with the current color.

    Example::

        anim = BackgroundColorAnimation(button)
        anim.animateTo(QColor("#11d9f3"))
    """

    def __init__(
        self,
        target: QWidget,
        initial: QColor | str | None = None,
        duration_ms: int = DEFAULT_DURATION_MS,
        easing: QEasingCurve.Type = DEFAULT_EASING,
    ) -> None:
        super().__init__(target)
        self._target = target
        self._color: QColor = QColor(initial) if initial is not None else QColor("#000000")
        self._animation = QPropertyAnimation(self, b"backgroundColor", self)
        self._animation.setDuration(duration_ms)
        self._animation.setEasingCurve(easing)
        self._apply()

    # -- Qt property -------------------------------------------------------

    def _get_color(self) -> QColor:
        return QColor(self._color)

    def _set_color(self, color: QColor) -> None:
        self._color = QColor(color)
        self._apply()

    backgroundColor = Property(QColor, _get_color, _set_color)

    # -- public API --------------------------------------------------------

    def color(self) -> QColor:
        return QColor(self._color)

    def setDuration(self, ms: int) -> None:
        self._animation.setDuration(int(ms))

    def duration(self) -> int:
        return self._animation.duration()

    def animateTo(self, color: QColor | str) -> None:
        """Animate from the current color to *color*."""
        end = QColor(color)
        self._animation.stop()
        self._animation.setStartValue(QColor(self._color))
        self._animation.setEndValue(end)
        self._animation.start()

    def stop(self) -> None:
        self._animation.stop()

    # -- internal ----------------------------------------------------------

    def _apply(self) -> None:
        if self._target is None:
            return
        self._target.setStyleSheet(
            f"{type(self._target).__name__} {{ background-color: {self._color.name()}; }}"
        )


__all__ = ["BackgroundColorAnimation"]
