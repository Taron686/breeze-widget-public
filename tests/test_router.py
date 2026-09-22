"""Smoke tests for Phase 3e: BreezeRouter + BreezeWindow integration."""
from __future__ import annotations

from PySide6.QtWidgets import QLabel, QWidget

from breezewidget import BreezeIcon, BreezeRouter, BreezeWindow


# ---------------------------------------------------------------------------
# BreezeRouter — standalone (no window needed)
# ---------------------------------------------------------------------------

def _make_router(qapp) -> tuple[BreezeRouter, QWidget, QWidget]:
    router = BreezeRouter()
    a = QLabel("A")
    b = QLabel("B")
    router.addRoute("a", a)
    router.addRoute("b", b)
    return router, a, b


def test_router_initial_state(qapp):
    router = BreezeRouter()
    assert router.current() is None
    assert router.canGoBack() is False


def test_router_replace_sets_current_without_history(qapp):
    router, a, b = _make_router(qapp)
    router.replace("a")
    assert router.current() == "a"
    assert router.canGoBack() is False


def test_router_push_sets_current_and_builds_history(qapp):
    router, a, b = _make_router(qapp)
    router.replace("a")
    router.push("b")
    assert router.current() == "b"
    assert router.canGoBack() is True


def test_router_back_returns_to_previous(qapp):
    router, a, b = _make_router(qapp)
    router.replace("a")
    router.push("b")
    router.back()
    assert router.current() == "a"
    assert router.canGoBack() is False


def test_router_push_same_key_is_noop(qapp, qtbot):
    router, a, b = _make_router(qapp)
    router.replace("a")
    signals: list[str] = []
    router.routeChanged.connect(signals.append)
    router.push("a")
    assert signals == []
    assert router.current() == "a"


def test_router_push_unknown_key_is_noop(qapp):
    router, a, b = _make_router(qapp)
    router.replace("a")
    router.push("nonexistent")
    assert router.current() == "a"


def test_router_back_when_empty_is_noop(qapp):
    router, a, b = _make_router(qapp)
    router.replace("a")
    router.back()  # history empty — must not raise
    assert router.current() == "a"


def test_router_route_changed_signal_fires_on_push(qapp, qtbot):
    router, a, b = _make_router(qapp)
    router.replace("a")
    with qtbot.waitSignal(router.routeChanged, timeout=500) as signal:
        router.push("b")
    assert signal.args == ["b"]


def test_router_replace_does_not_add_history(qapp):
    router, a, b = _make_router(qapp)
    router.replace("a")
    router.replace("b")
    assert router.canGoBack() is False
    assert router.current() == "b"


def test_router_widget_lookup(qapp):
    router, a, b = _make_router(qapp)
    assert router.widget("a") is a
    assert router.widget("b") is b
    assert router.widget("x") is None


def test_router_key_for_widget(qapp):
    router, a, b = _make_router(qapp)
    assert router.keyForWidget(a) == "a"
    assert router.keyForWidget(b) == "b"
    assert router.keyForWidget(QLabel("orphan")) is None


def test_router_routes_returns_copy(qapp):
    router, a, b = _make_router(qapp)
    copy = router.routes()
    copy["x"] = QLabel("X")
    assert "x" not in router.routes()


# ---------------------------------------------------------------------------
# BreezeWindow integration
# ---------------------------------------------------------------------------

def test_breeze_window_has_router(qapp):
    window = BreezeWindow()
    assert isinstance(window.router, BreezeRouter)


def test_breeze_window_add_sub_interface_sets_router_current(qapp):
    window = BreezeWindow()
    page = QLabel("Home")
    page.setObjectName("home")
    window.addSubInterface(page, BreezeIcon.HOME, "Home")
    assert window.router.current() == "home"
    assert window.router.widget("home") is page


def test_breeze_window_switch_to_string_uses_router(qapp):
    window = BreezeWindow()
    a = QLabel("A"); a.setObjectName("a")
    b = QLabel("B"); b.setObjectName("b")
    window.addSubInterface(a, BreezeIcon.HOME, "A")
    window.addSubInterface(b, BreezeIcon.SETTINGS, "B")
    window.switchTo("b")
    assert window.router.current() == "b"
    assert window.stackedWidget.currentWidget() is b
    assert window.navigationInterface.currentItem() == "b"


def test_breeze_window_switch_to_widget_uses_router(qapp):
    window = BreezeWindow()
    a = QLabel("A"); a.setObjectName("a")
    b = QLabel("B"); b.setObjectName("b")
    window.addSubInterface(a, BreezeIcon.HOME, "A")
    window.addSubInterface(b, BreezeIcon.SETTINGS, "B")
    window.switchTo(b)
    assert window.router.current() == "b"
    assert window.stackedWidget.currentWidget() is b


def test_breeze_window_router_back_navigates(qapp):
    window = BreezeWindow()
    a = QLabel("A"); a.setObjectName("a")
    b = QLabel("B"); b.setObjectName("b")
    window.addSubInterface(a, BreezeIcon.HOME, "A")
    window.addSubInterface(b, BreezeIcon.SETTINGS, "B")
    window.switchTo("b")
    window.router.back()
    assert window.router.current() == "a"
    assert window.stackedWidget.currentWidget() is a
