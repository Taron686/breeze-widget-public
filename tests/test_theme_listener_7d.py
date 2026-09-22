"""Phase 7d — OSThemeListener."""
from __future__ import annotations

from PySide6.QtCore import QCoreApplication

from breezewidget import OSThemeListener
from breezewidget.theme import listener as listener_mod


def test_initial_state(qapp):
    lst = OSThemeListener(interval_ms=500)
    assert not lst.isRunning()
    assert lst.interval() == 500


def test_set_interval_clamps_minimum(qapp):
    lst = OSThemeListener()
    lst.setInterval(10)
    assert lst.interval() == 100
    lst.setInterval(5000)
    assert lst.interval() == 5000


def test_start_emits_initial_signal(qapp, monkeypatch):
    monkeypatch.setattr(OSThemeListener, "_detect", lambda self: True)
    lst = OSThemeListener(interval_ms=10000)
    seen = []
    lst.osThemeChanged.connect(seen.append)
    lst.start()
    try:
        assert lst.isRunning()
        assert seen == [True]
    finally:
        lst.stop()


def test_stop_halts_polling(qapp, monkeypatch):
    monkeypatch.setattr(OSThemeListener, "_detect", lambda self: False)
    lst = OSThemeListener(interval_ms=10000)
    lst.start()
    lst.stop()
    assert not lst.isRunning()


def test_signal_only_on_change(qapp, monkeypatch):
    state = {"dark": False}
    monkeypatch.setattr(OSThemeListener, "_detect", lambda self: state["dark"])
    lst = OSThemeListener(interval_ms=10000)
    seen = []
    lst.osThemeChanged.connect(seen.append)
    lst.start()
    try:
        # Initial start emitted once.
        assert seen == [False]
        # No flip — manual poll: still no new emit.
        lst._poll()
        assert seen == [False]
        # Flip — manual poll triggers emit.
        state["dark"] = True
        lst._poll()
        assert seen == [False, True]
        # No second emit until next change.
        lst._poll()
        assert seen == [False, True]
    finally:
        lst.stop()


def test_is_os_dark_returns_detected_value(qapp, monkeypatch):
    monkeypatch.setattr(OSThemeListener, "_detect", lambda self: True)
    lst = OSThemeListener()
    assert lst.isOSDark() is True


def test_idempotent_start_stop(qapp, monkeypatch):
    monkeypatch.setattr(OSThemeListener, "_detect", lambda self: False)
    lst = OSThemeListener(interval_ms=10000)
    lst.start()
    lst.start()
    assert lst.isRunning()
    lst.stop()
    lst.stop()
    assert not lst.isRunning()


def test_linux_detector_reads_gtk_theme(monkeypatch):
    monkeypatch.setenv("GTK_THEME", "Adwaita-dark")
    assert listener_mod._detect_linux() is True
    monkeypatch.setenv("GTK_THEME", "Adwaita")
    assert listener_mod._detect_linux() is False
    monkeypatch.delenv("GTK_THEME", raising=False)
    assert listener_mod._detect_linux() is False
