from __future__ import annotations

from breezewidget import BreezeIcon, NavigationInterface, NavigationItemPosition


def test_navigation_interface_constructs(qapp):
    nav = NavigationInterface()
    assert nav.property("breezeNavigation") is True


def test_navigation_add_item_returns_button(qapp):
    nav = NavigationInterface()
    button = nav.addItem("home", BreezeIcon.HOME, "Home")
    assert button is not None
    assert button.property("breezeNavigationItem") is True
    assert nav.item("home") is button


def test_navigation_set_current_item_emits(qapp, qtbot):
    nav = NavigationInterface()
    nav.addItem("home", BreezeIcon.HOME, "Home")
    nav.addItem("settings", BreezeIcon.SETTINGS, "Settings")

    with qtbot.waitSignal(nav.currentItemChanged, timeout=1000) as blocker:
        nav.setCurrentItem("settings")
    assert blocker.args == ["settings"]
    assert nav.currentItem() == "settings"


def test_navigation_compact_toggle_changes_width(qapp):
    nav = NavigationInterface()
    nav.addItem("home", BreezeIcon.HOME, "Home")

    nav.setCompact(False)
    expanded = nav.width()
    nav.setCompact(True)
    compact = nav.width()
    assert compact < expanded
    assert nav.isCompact() is True

    nav.setCompact(False)
    assert nav.isCompact() is False


def test_navigation_item_positions(qapp):
    nav = NavigationInterface()
    top = nav.addItem("a", BreezeIcon.HOME, "A", position=NavigationItemPosition.TOP)
    bottom = nav.addItem(
        "b", BreezeIcon.SETTINGS, "B", position=NavigationItemPosition.BOTTOM
    )
    assert top is not None and bottom is not None


def test_navigation_callback_runs(qapp):
    nav = NavigationInterface()
    called: list[str] = []
    nav.addItem("ping", BreezeIcon.HOME, "Ping", onClick=lambda: called.append("yes"))
    nav.setCurrentItem("ping")
    assert called == ["yes"]


def test_navigation_separator(qapp):
    nav = NavigationInterface()
    nav.addItem("a", BreezeIcon.HOME, "A")
    nav.addSeparator()
    nav.addItem("b", BreezeIcon.SETTINGS, "B")
