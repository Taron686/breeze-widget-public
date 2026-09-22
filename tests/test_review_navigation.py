import pytest
from PySide6.QtTest import QSignalSpy
from breezewidget import Pivot, SegmentedWidget, TabBar


@pytest.mark.parametrize("cls", [Pivot, SegmentedWidget, TabBar])
def test_current_route_cannot_be_unchecked(qapp, qtbot, cls):
    nav = cls()
    qtbot.addWidget(nav)
    add = nav.addTab if cls is TabBar else nav.addItem
    first = add("First", "first")
    second = add("Second", "second")
    button = lambda item: item._button if cls is TabBar else item
    changes = QSignalSpy(nav.currentChanged)
    button(first).click()
    assert button(first).isChecked()
    assert changes.count() == 0
    button(second).click()
    assert nav.currentRoute() == "second"
    assert button(second).isChecked()
    assert not button(first).isChecked()
    assert changes.count() == 1
    nav.setCurrentRoute("first")
    assert button(first).isChecked()
    assert not button(second).isChecked()
