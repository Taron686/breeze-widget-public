""":class:`PropertyAnimation` — thin :class:`QPropertyAnimation` wrapper with
sensible Breeze defaults (180 ms, ``OutCubic``).
"""
from __future__ import annotations

from typing import Any

from PySide6.QtCore import QEasingCurve, QObject, QPropertyAnimation


DEFAULT_DURATION_MS = 180
DEFAULT_EASING = QEasingCurve.Type.OutCubic


class PropertyAnimation(QPropertyAnimation):
    """:class:`QPropertyAnimation` with Breeze defaults and chainable setters."""

    def __init__(
        self,
        target: QObject,
        property_name: bytes | str,
        duration_ms: int = DEFAULT_DURATION_MS,
        easing: QEasingCurve.Type = DEFAULT_EASING,
        parent: QObject | None = None,
    ) -> None:
        prop = property_name.encode() if isinstance(property_name, str) else property_name
        super().__init__(target, prop, parent)
        self.setDuration(duration_ms)
        self.setEasingCurve(easing)

    def from_(self, value: Any) -> "PropertyAnimation":
        self.setStartValue(value)
        return self

    def to(self, value: Any) -> "PropertyAnimation":
        self.setEndValue(value)
        return self

    def withDuration(self, ms: int) -> "PropertyAnimation":
        self.setDuration(int(ms))
        return self

    def withEasing(self, easing: QEasingCurve.Type) -> "PropertyAnimation":
        self.setEasingCurve(easing)
        return self


__all__ = ["PropertyAnimation", "DEFAULT_DURATION_MS", "DEFAULT_EASING"]
