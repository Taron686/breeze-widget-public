"""Shared helper to convert any Qt popup container into a Breeze-styled
frameless, translucent popup that lets QSS draw rounded corners cleanly.

Used by :class:`RoundMenu`, :class:`ComboBox` (popup container), and any
other Breeze widget that opens a top-level popup.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget


def apply_breeze_popup_window(widget: QWidget) -> None:
    """Make *widget* a frameless, translucent top-level popup window.

    Idempotent: safe to call repeatedly.
    """
    if widget is None:
        return
    widget.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
    widget.setWindowFlag(Qt.WindowType.NoDropShadowWindowHint, True)
    widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)


__all__ = ["apply_breeze_popup_window"]
