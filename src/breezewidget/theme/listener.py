"""OS theme listener — polls the operating system's light/dark setting and
emits :class:`OSThemeListener.osThemeChanged` whenever it flips.

On Windows the listener reads
``HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize\\AppsUseLightTheme``
via :mod:`winreg`. On macOS it shells out to ``defaults read -g AppleInterfaceStyle``
(``"Dark"`` ⇒ dark). On Linux there is no portable signal — it reads
the ``GTK_THEME`` env-var as a hint and otherwise reports light.

Wire ``osThemeChanged`` to :meth:`ThemeManager.applyTheme` if you want the
app's ``Theme.AUTO`` mode to follow the OS in real time::

    listener = OSThemeListener()
    listener.osThemeChanged.connect(lambda is_dark: ThemeManager.instance().applyTheme(...))
    listener.start()
"""
from __future__ import annotations

import sys
from typing import Optional

from PySide6.QtCore import QObject, QTimer, Signal


class OSThemeListener(QObject):
    """Polls the OS for light/dark mode at a configurable interval."""

    osThemeChanged = Signal(bool)  # True = dark, False = light

    DEFAULT_INTERVAL_MS = 2000

    def __init__(self, interval_ms: int = DEFAULT_INTERVAL_MS, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.setInterval(interval_ms)
        self._timer.timeout.connect(self._poll)
        self._last_dark: Optional[bool] = None
        self._running = False

    # -- control -----------------------------------------------------------

    def start(self) -> None:
        """Begin polling. Emits an initial ``osThemeChanged`` if state changed."""
        if self._running:
            return
        self._running = True
        # Capture initial state and emit if different from last seen.
        self._poll(force_emit=True)
        self._timer.start()

    def stop(self) -> None:
        if not self._running:
            return
        self._timer.stop()
        self._running = False

    def isRunning(self) -> bool:
        return self._running

    def setInterval(self, ms: int) -> None:
        self._timer.setInterval(max(100, int(ms)))

    def interval(self) -> int:
        return self._timer.interval()

    # -- query -------------------------------------------------------------

    def isOSDark(self) -> bool:
        """Return ``True`` when the OS reports dark mode. Polls once."""
        return self._detect()

    # -- internals ---------------------------------------------------------

    def _poll(self, force_emit: bool = False) -> None:
        is_dark = self._detect()
        if force_emit or is_dark != self._last_dark:
            self._last_dark = is_dark
            self.osThemeChanged.emit(is_dark)

    def _detect(self) -> bool:
        platform = sys.platform
        if platform == "win32":
            return _detect_windows()
        if platform == "darwin":
            return _detect_macos()
        return _detect_linux()


# ---------------------------------------------------------------------------
# Per-platform detectors (module-level so they can be monkeypatched in tests)
# ---------------------------------------------------------------------------

def _detect_windows() -> bool:
    try:
        import winreg  # type: ignore[import-not-found]
    except ImportError:
        return False
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        ) as key:
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return int(value) == 0
    except OSError:
        return False


def _detect_macos() -> bool:
    import subprocess

    try:
        result = subprocess.run(
            ["defaults", "read", "-g", "AppleInterfaceStyle"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return result.returncode == 0 and "Dark" in result.stdout


def _detect_linux() -> bool:
    import os

    hint = os.environ.get("GTK_THEME", "").lower()
    return "dark" in hint


__all__ = ["OSThemeListener"]
