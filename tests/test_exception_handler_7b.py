"""Phase 7b — ExceptionHandler."""
from __future__ import annotations

import sys

import pytest

from breezewidget import ExceptionHandler


def _trigger() -> tuple[type[BaseException], BaseException, object]:
    try:
        raise ValueError("boom")
    except ValueError as e:
        return type(e), e, e.__traceback__


def test_handle_emits_signal(qapp):
    h = ExceptionHandler()
    seen = []
    h.exceptionRaised.connect(lambda t, e, tb: seen.append((t, e)))
    et, e, tb = _trigger()
    h.handle(et, e, tb)
    assert len(seen) == 1
    assert seen[0][1] is e


def test_handle_writes_logfile(qapp, tmp_path):
    log = tmp_path / "crash.log"
    h = ExceptionHandler(log_file=log)
    et, e, tb = _trigger()
    h.handle(et, e, tb)
    text = log.read_text(encoding="utf-8")
    assert "ValueError" in text
    assert "boom" in text


def test_handle_appends_to_logfile(qapp, tmp_path):
    log = tmp_path / "crash.log"
    h = ExceptionHandler(log_file=log)
    et, e, tb = _trigger()
    h.handle(et, e, tb)
    h.handle(et, e, tb)
    text = log.read_text(encoding="utf-8")
    assert text.count("ValueError") >= 2


def test_handle_creates_parent_dirs(qapp, tmp_path):
    log = tmp_path / "deep" / "nest" / "crash.log"
    h = ExceptionHandler(log_file=log)
    et, e, tb = _trigger()
    h.handle(et, e, tb)
    assert log.is_file()


def test_handle_invokes_callback(qapp):
    h = ExceptionHandler()
    captured = []
    h.setCallback(lambda t, e, tb: captured.append(e))
    et, e, tb = _trigger()
    h.handle(et, e, tb)
    assert captured == [e]


def test_callback_failure_does_not_propagate(qapp, capsys):
    def bad(t, e, tb):
        raise RuntimeError("sink crashed")

    h = ExceptionHandler(callback=bad)
    et, e, tb = _trigger()
    h.handle(et, e, tb)
    err = capsys.readouterr().err
    assert "sink crashed" in err


def test_keyboard_interrupt_falls_through(qapp):
    h = ExceptionHandler()
    seen = []
    h.exceptionRaised.connect(lambda t, e, tb: seen.append(e))
    try:
        raise KeyboardInterrupt()
    except KeyboardInterrupt as e:
        h.handle(type(e), e, e.__traceback__)
    assert seen == []


def test_install_replaces_excepthook_and_uninstall_restores(qapp):
    original = sys.excepthook
    h = ExceptionHandler()
    h.install()
    try:
        assert sys.excepthook is not original
        assert h.isInstalled()
    finally:
        h.uninstall()
    assert sys.excepthook is original
    assert not h.isInstalled()


def test_install_idempotent(qapp):
    h = ExceptionHandler()
    h.install()
    hook = sys.excepthook
    h.install()
    assert sys.excepthook is hook
    h.uninstall()


def test_chain_previous_calls_prior_hook(qapp):
    calls = []

    def prior(t, e, tb):
        calls.append("prior")

    original = sys.excepthook
    sys.excepthook = prior
    try:
        h = ExceptionHandler(chain_previous=True)
        h.install()
        et, e, tb = _trigger()
        h.handle(et, e, tb)
        assert calls == ["prior"]
        h.uninstall()
    finally:
        sys.excepthook = original


def test_format_returns_traceback_string():
    et, e, tb = _trigger()
    text = ExceptionHandler.format(et, e, tb)
    assert "ValueError" in text and "boom" in text


def test_setters(qapp, tmp_path):
    h = ExceptionHandler()
    h.setLogFile(tmp_path / "x.log")
    assert h.logFile() == tmp_path / "x.log"
    h.setLogFile(None)
    assert h.logFile() is None
    h.setShowDialog(True)
    cb = lambda t, e, tb: None
    h.setCallback(cb)
