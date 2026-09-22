"""Cross-platform window material adapter.

Provides :class:`MaterialEffect` and :func:`apply_material` so client
code can request native backdrops (Windows 11 Mica, Acrylic) without
caring about the OS.  On unsupported platforms or older Windows
versions the call is a safe no-op and returns ``False``.

The Windows path uses ``DwmSetWindowAttribute`` with
``DWMWA_SYSTEMBACKDROP_TYPE`` (attribute 38).  Values follow Microsoft's
``DWM_SYSTEMBACKDROP_TYPE`` enum: 1 = AUTO/None, 2 = Mica, 3 =
Acrylic, 4 = Mica Alt (Tabbed).
"""
from __future__ import annotations

import ctypes
import sys
from enum import IntEnum

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget


class MaterialEffect(IntEnum):
    """Backdrop effect applied to a top-level window."""

    NONE = 1  # DWMSBT_AUTO — fall back to default (no effect).
    MICA = 2  # DWMSBT_MAINWINDOW
    ACRYLIC = 3  # DWMSBT_TRANSIENTWINDOW
    MICA_ALT = 4  # DWMSBT_TABBEDWINDOW


_DWMWA_SYSTEMBACKDROP_TYPE = 38


def apply_material(window: QWidget, effect: MaterialEffect) -> bool:
    """Apply a native backdrop *effect* to *window*.

    Returns ``True`` if the platform call succeeded.  On non-Windows
    platforms, on Windows < 11, or when ``window.winId()`` is not yet
    available, returns ``False`` without raising.

    Translucency is also enabled on the widget so the backdrop can
    show through.
    """
    if window is None:
        return False
    # Force translucency so DWM can paint the backdrop behind us.
    window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    if sys.platform != "win32":
        return False

    try:
        hwnd = int(window.winId())
        if hwnd == 0:
            return False
        dwmapi = ctypes.windll.dwmapi  # type: ignore[attr-defined]
        value = ctypes.c_int(int(effect))
        result = dwmapi.DwmSetWindowAttribute(
            ctypes.c_void_p(hwnd),
            ctypes.c_uint(_DWMWA_SYSTEMBACKDROP_TYPE),
            ctypes.byref(value),
            ctypes.sizeof(value),
        )
        return result == 0  # S_OK
    except (OSError, AttributeError):
        return False
