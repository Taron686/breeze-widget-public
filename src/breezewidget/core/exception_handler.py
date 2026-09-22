"""Global exception handler — installs ``sys.excepthook`` and forwards
unhandled exceptions to optional file/dialog/callback sinks.

Typical usage at app startup::

    from pathlib import Path
    from breezewidget import ExceptionHandler

    handler = ExceptionHandler(
        log_file=Path("crash.log"),
        show_dialog=True,
        chain_previous=True,
    )
    handler.install()

The handler intentionally does **not** raise from inside its sinks — a sink
that itself fails is logged to ``stderr`` but never crashes the host app.
``KeyboardInterrupt`` always falls through to the previous excepthook so
``Ctrl+C`` keeps working.
"""
from __future__ import annotations

import sys
import traceback
from datetime import datetime
from pathlib import Path
from types import TracebackType
from typing import Callable

from PySide6.QtCore import QObject, Signal

ExcInfo = tuple[type[BaseException], BaseException, TracebackType | None]
ExceptionCallback = Callable[[type[BaseException], BaseException, TracebackType | None], None]


class ExceptionHandler(QObject):
    """Catches unhandled exceptions and dispatches to logfile/dialog/callback.

    Sinks (any combination):
    - ``log_file``: append ``[timestamp] traceback`` to a file.
    - ``show_dialog``: pop a Breeze ``Dialog`` with the exception summary.
    - ``callback``: arbitrary callable invoked with ``(exc_type, exc, tb)``.

    The Qt ``exceptionRaised(type, exc, tb)`` signal fires for every caught
    exception regardless of sink configuration.
    """

    exceptionRaised = Signal(object, object, object)

    def __init__(
        self,
        log_file: Path | str | None = None,
        show_dialog: bool = False,
        callback: ExceptionCallback | None = None,
        chain_previous: bool = False,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._log_file: Path | None = Path(log_file) if log_file else None
        self._show_dialog = show_dialog
        self._callback = callback
        self._chain_previous = chain_previous
        self._previous_hook: Callable | None = None
        self._installed = False

    # -- configuration -----------------------------------------------------

    def setLogFile(self, path: Path | str | None) -> None:
        self._log_file = Path(path) if path else None

    def logFile(self) -> Path | None:
        return self._log_file

    def setShowDialog(self, enabled: bool) -> None:
        self._show_dialog = bool(enabled)

    def setCallback(self, callback: ExceptionCallback | None) -> None:
        self._callback = callback

    # -- install / uninstall ------------------------------------------------

    def install(self) -> None:
        """Install as ``sys.excepthook``. Safe to call repeatedly."""
        if self._installed:
            return
        self._previous_hook = sys.excepthook
        sys.excepthook = self._hook
        self._installed = True

    def uninstall(self) -> None:
        """Restore the previous ``sys.excepthook``."""
        if not self._installed:
            return
        sys.excepthook = self._previous_hook or sys.__excepthook__
        self._previous_hook = None
        self._installed = False

    def isInstalled(self) -> bool:
        return self._installed

    # -- core dispatch ------------------------------------------------------

    def handle(self, exc_type: type[BaseException], exc: BaseException, tb: TracebackType | None) -> None:
        """Run all sinks for the given exception. Public entry-point for
        callers that catch their own exceptions and want to forward them."""
        if issubclass(exc_type, KeyboardInterrupt):
            if self._previous_hook:
                self._previous_hook(exc_type, exc, tb)
            else:
                sys.__excepthook__(exc_type, exc, tb)
            return

        try:
            self.exceptionRaised.emit(exc_type, exc, tb)
        except Exception as sink_err:  # pragma: no cover - defensive
            print(f"[ExceptionHandler] signal failed: {sink_err}", file=sys.stderr)

        if self._log_file is not None:
            self._safe_write_log(exc_type, exc, tb)

        if self._callback is not None:
            try:
                self._callback(exc_type, exc, tb)
            except Exception as sink_err:
                print(f"[ExceptionHandler] callback failed: {sink_err}", file=sys.stderr)

        if self._show_dialog:
            self._safe_show_dialog(exc_type, exc, tb)

        if self._chain_previous and self._previous_hook is not None:
            try:
                self._previous_hook(exc_type, exc, tb)
            except Exception as sink_err:  # pragma: no cover
                print(f"[ExceptionHandler] previous hook failed: {sink_err}", file=sys.stderr)

    # -- internal -----------------------------------------------------------

    def _hook(self, exc_type: type[BaseException], exc: BaseException, tb: TracebackType | None) -> None:
        self.handle(exc_type, exc, tb)

    def _safe_write_log(self, exc_type: type[BaseException], exc: BaseException, tb: TracebackType | None) -> None:
        assert self._log_file is not None
        try:
            self._log_file.parent.mkdir(parents=True, exist_ok=True)
            with self._log_file.open("a", encoding="utf-8") as fh:
                fh.write(f"[{datetime.now().isoformat(timespec='seconds')}] ")
                fh.write("".join(traceback.format_exception(exc_type, exc, tb)))
                fh.write("\n")
        except OSError as sink_err:
            print(f"[ExceptionHandler] log write failed: {sink_err}", file=sys.stderr)

    def _safe_show_dialog(self, exc_type: type[BaseException], exc: BaseException, tb: TracebackType | None) -> None:
        try:
            from PySide6.QtWidgets import QApplication

            if QApplication.instance() is None:
                return
            from ..dialogs import Dialog

            summary = "".join(traceback.format_exception_only(exc_type, exc)).strip()
            dlg = Dialog(parent=None)
            dlg.setTitle("Unhandled exception")
            dlg.setContentText(summary or repr(exc))
            dlg.setYesText("OK")
            dlg.cancelButton.setVisible(False)
            dlg.exec()
        except Exception as sink_err:  # pragma: no cover - dialog is best-effort
            print(f"[ExceptionHandler] dialog failed: {sink_err}", file=sys.stderr)

    @staticmethod
    def format(exc_type: type[BaseException], exc: BaseException, tb: TracebackType | None) -> str:
        """Return a multi-line ``traceback`` string. Public helper for sinks."""
        return "".join(traceback.format_exception(exc_type, exc, tb))


__all__ = ["ExceptionHandler"]
