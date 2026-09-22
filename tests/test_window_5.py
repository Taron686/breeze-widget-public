"""Smoke tests for Phase 5: Plattform & Material."""
from __future__ import annotations

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel, QStackedWidget

from breezewidget import (
    BreezeIcon,
    MSBreezeWindow,
    SplitBreezeWindow,
)
from breezewidget.window import BreezeSplashScreen, MaterialEffect, apply_material


# ---------------------------------------------------------------------------
# MSBreezeWindow (top pivot)
# ---------------------------------------------------------------------------

def test_ms_window_has_pivot_and_stack(qapp):
    win = MSBreezeWindow()
    assert isinstance(win.stackedWidget, QStackedWidget)
    assert win.pivot is not None
    assert win.router is not None


def test_ms_window_add_sub_interface_registers_route(qapp):
    win = MSBreezeWindow()
    page = QLabel("home")
    key = win.addSubInterface(page, "Home", routeKey="home")
    assert key == "home"
    assert win.router.widget("home") is page
    assert win.stackedWidget.count() == 1


def test_ms_window_first_interface_is_active(qapp):
    win = MSBreezeWindow()
    page = QLabel("home")
    win.addSubInterface(page, "Home", routeKey="home")
    assert win.router.current() == "home"
    assert win.stackedWidget.currentWidget() is page


def test_ms_window_pivot_navigation(qapp):
    win = MSBreezeWindow()
    a, b = QLabel("a"), QLabel("b")
    win.addSubInterface(a, "A", routeKey="a")
    win.addSubInterface(b, "B", routeKey="b")
    win.pivot.setCurrentRoute("b")
    assert win.router.current() == "b"
    assert win.stackedWidget.currentWidget() is b


# ---------------------------------------------------------------------------
# SplitBreezeWindow
# ---------------------------------------------------------------------------

def test_split_window_has_splitter(qapp):
    win = SplitBreezeWindow()
    assert win.splitter is not None
    assert win.splitter.count() == 2


def test_split_window_add_sub_interface(qapp):
    win = SplitBreezeWindow()
    page = QLabel("settings")
    key = win.addSubInterface(page, BreezeIcon.SETTINGS, "Settings", routeKey="settings")
    assert key == "settings"
    assert win.router.widget("settings") is page


def test_split_window_set_navigation_width(qapp, qtbot):
    win = SplitBreezeWindow()
    qtbot.addWidget(win)
    win.resize(1000, 600)
    win.show()
    qtbot.waitExposed(win)
    win.setNavigationWidth(300)
    # Splitter rounds sizes; allow small tolerance.
    assert abs(win.navigationWidth() - 300) <= 2


def test_split_window_navigation_and_content_have_no_extra_gap(qapp, qtbot):
    win = SplitBreezeWindow()
    qtbot.addWidget(win)
    win.resize(900, 540)
    win.show()
    qtbot.waitExposed(win)

    nav_right = win.navigationInterface.geometry().x() + win.navigationInterface.geometry().width()
    host_left = win.contentHost.geometry().left()
    content_left = win.stackedWidget.mapTo(win.splitter, win.stackedWidget.rect().topLeft()).x()

    assert host_left - nav_right <= win.splitter.handleWidth()
    assert content_left - host_left == 6


def test_split_window_route_change_updates_stack(qapp):
    win = SplitBreezeWindow()
    a, b = QLabel("a"), QLabel("b")
    win.addSubInterface(a, BreezeIcon.HOME, "A", routeKey="a")
    win.addSubInterface(b, BreezeIcon.SETTINGS, "B", routeKey="b")
    win.router.push("b")
    assert win.stackedWidget.currentWidget() is b


# ---------------------------------------------------------------------------
# BreezeSplashScreen
# ---------------------------------------------------------------------------

def test_splash_screen_constructs(qapp):
    splash = BreezeSplashScreen(QIcon(), "MyApp")
    assert splash.property("breezeSplashScreen") is True


def test_splash_screen_set_title(qapp):
    splash = BreezeSplashScreen(QIcon(), "Old")
    splash.setTitle("New Title")
    assert splash._titleLabel.text() == "New Title"


def test_splash_screen_finish_emits_closed(qapp, qtbot):
    splash = BreezeSplashScreen(QIcon(), "App")
    with qtbot.waitSignal(splash.closed, timeout=500):
        splash.finish()


def test_splash_screen_finish_shows_window(qapp):
    splash = BreezeSplashScreen(QIcon(), "App")
    win = QLabel("main")
    splash.finish(win)
    # Window was raised; closed signal fired.
    assert not splash.isVisible()


# ---------------------------------------------------------------------------
# Material adapter
# ---------------------------------------------------------------------------

def test_material_effect_enum_values():
    assert int(MaterialEffect.NONE) == 1
    assert int(MaterialEffect.MICA) == 2
    assert int(MaterialEffect.ACRYLIC) == 3
    assert int(MaterialEffect.MICA_ALT) == 4


def test_apply_material_does_not_crash(qapp):
    splash = BreezeSplashScreen(QIcon(), "App")
    # Returns bool; offscreen platform may return False.  Must not raise.
    result = apply_material(splash, MaterialEffect.MICA)
    assert isinstance(result, bool)


def test_apply_material_handles_none_window():
    assert apply_material(None, MaterialEffect.MICA) is False
