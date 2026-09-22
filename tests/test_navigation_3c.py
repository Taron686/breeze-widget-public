"""Smoke tests for Phase 3c navigation components."""
from __future__ import annotations

from breezewidget import (
    BreadcrumbBar,
    Pivot,
    SegmentedWidget,
    TabBar,
)
from breezewidget.constants import (
    PROP_BREADCRUMB,
    PROP_BREADCRUMB_ITEM,
    PROP_PIVOT,
    PROP_PIVOT_ITEM,
    PROP_SEGMENTED,
    PROP_SEGMENTED_ITEM,
    PROP_TAB_BAR,
    PROP_TAB_ITEM,
)


# --- Pivot ---------------------------------------------------------------

def test_pivot_first_item_is_current(qapp, qtbot):
    pivot = Pivot()
    qtbot.addWidget(pivot)
    pivot.addItem("Home", "home")
    pivot.addItem("Search", "search")
    assert pivot.property(PROP_PIVOT) == "true"
    assert pivot.currentRoute() == "home"
    assert pivot.items()[0].property(PROP_PIVOT_ITEM) == "true"


def test_pivot_set_current_emits_signal(qapp, qtbot):
    pivot = Pivot()
    qtbot.addWidget(pivot)
    pivot.addItem("Home", "home")
    pivot.addItem("Search", "search")
    with qtbot.waitSignal(pivot.currentChanged, timeout=500) as signal:
        pivot.setCurrentRoute("search")
    assert signal.args == ["search"]
    assert pivot.currentRoute() == "search"


def test_pivot_indicator_follows_active_item(qapp, qtbot):
    pivot = Pivot()
    qtbot.addWidget(pivot)
    pivot.resize(400, 40)
    pivot.addItem("Home", "home")
    pivot.addItem("Mitte", "mid")
    pivot.addItem("Settings", "settings")
    pivot.show()
    qtbot.waitExposed(pivot)
    initial_x = pivot._indicator_x
    pivot.setCurrentRoute("settings")
    qtbot.waitUntil(lambda: pivot._indicator_x != initial_x, timeout=1000)
    assert pivot._indicator_x > initial_x


# --- SegmentedWidget ----------------------------------------------------

def test_segmented_first_item_is_current(qapp, qtbot):
    seg = SegmentedWidget()
    qtbot.addWidget(seg)
    seg.addItem("Day", "day")
    seg.addItem("Week", "week")
    assert seg.property(PROP_SEGMENTED) == "true"
    assert seg.currentRoute() == "day"
    assert seg.items()[0].property(PROP_SEGMENTED_ITEM) == "true"


def test_segmented_switch_route(qapp, qtbot):
    seg = SegmentedWidget()
    qtbot.addWidget(seg)
    seg.addItem("Day", "day")
    seg.addItem("Week", "week")
    with qtbot.waitSignal(seg.currentChanged, timeout=500):
        seg.setCurrentRoute("week")
    assert seg.currentRoute() == "week"
    assert seg.items()[0].isChecked() is False
    assert seg.items()[1].isChecked() is True


# --- BreadcrumbBar ------------------------------------------------------

def test_breadcrumb_marks_last_as_active(qapp, qtbot):
    bar = BreadcrumbBar()
    qtbot.addWidget(bar)
    bar.addItem("Root", "root")
    bar.addItem("Folder", "folder")
    bar.addItem("File", "file")
    assert bar.property(PROP_BREADCRUMB) == "true"
    items = bar.items()
    assert items[-1].property("breezeBreadcrumbActive") == "true"
    for ancestor in items[:-1]:
        assert ancestor.property("breezeBreadcrumbActive") == "false"
    assert items[0].property(PROP_BREADCRUMB_ITEM) == "true"


def test_breadcrumb_emits_current_changed_on_click(qapp, qtbot):
    bar = BreadcrumbBar()
    qtbot.addWidget(bar)
    root = bar.addItem("Root", "root")
    bar.addItem("Folder", "folder")
    with qtbot.waitSignal(bar.currentChanged, timeout=500) as signal:
        root.click()
    assert signal.args == ["root"]


def test_breadcrumb_clear_removes_all_items(qapp, qtbot):
    bar = BreadcrumbBar()
    qtbot.addWidget(bar)
    bar.addItem("A")
    bar.addItem("B")
    bar.clear()
    assert bar.items() == []


def test_breadcrumb_clicking_ancestor_truncates_trail(qapp, qtbot):
    bar = BreadcrumbBar()
    qtbot.addWidget(bar)
    root = bar.addItem("Root", "root")
    bar.addItem("Folder", "folder")
    bar.addItem("File", "file")
    assert [item.routeKey() for item in bar.items()] == ["root", "folder", "file"]
    with qtbot.waitSignal(bar.currentChanged, timeout=500) as signal:
        root.click()
    assert signal.args == ["root"]
    assert [item.routeKey() for item in bar.items()] == ["root"]
    assert bar.currentRoute() == "root"


def test_breadcrumb_truncate_to_leaf_is_noop(qapp, qtbot):
    bar = BreadcrumbBar()
    qtbot.addWidget(bar)
    bar.addItem("A", "a")
    bar.addItem("B", "b")
    bar.truncateTo("b")
    assert [item.routeKey() for item in bar.items()] == ["a", "b"]


# --- TabBar -------------------------------------------------------------

def test_tab_bar_first_tab_is_current(qapp, qtbot):
    bar = TabBar()
    qtbot.addWidget(bar)
    bar.addTab("Home", "home")
    bar.addTab("Edit", "edit")
    assert bar.property(PROP_TAB_BAR) == "true"
    assert bar.currentRoute() == "home"
    assert bar.tabs()[0].property(PROP_TAB_ITEM) == "true"


def test_tab_bar_switch_route(qapp, qtbot):
    bar = TabBar()
    qtbot.addWidget(bar)
    bar.addTab("Home", "home")
    bar.addTab("Edit", "edit")
    with qtbot.waitSignal(bar.currentChanged, timeout=500):
        bar.setCurrentRoute("edit")
    assert bar.currentRoute() == "edit"


def test_tab_bar_remove_tab_falls_back(qapp, qtbot):
    bar = TabBar()
    qtbot.addWidget(bar)
    bar.addTab("Home", "home")
    bar.addTab("Edit", "edit")
    bar.removeTab("home")
    assert bar.currentRoute() == "edit"
    assert len(bar.tabs()) == 1


def test_tab_bar_close_request_signal(qapp, qtbot):
    bar = TabBar()
    qtbot.addWidget(bar)
    tab = bar.addTab("Home", "home")
    with qtbot.waitSignal(bar.tabCloseRequested, timeout=500) as signal:
        tab._close_button.click()
    assert signal.args == ["home"]
