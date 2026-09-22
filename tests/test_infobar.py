from __future__ import annotations

from PySide6.QtWidgets import QWidget

from breezewidget import BreezeIcon, InfoBar, InfoBarPosition


def test_infobar_position_enum_has_six_values():
    assert {p.value for p in InfoBarPosition} == {
        "top", "topRight", "topLeft", "bottom", "bottomRight", "bottomLeft",
    }


def test_infobar_constructs(qapp):
    parent = QWidget()
    parent.resize(400, 300)
    bar = InfoBar(BreezeIcon.INFO, "Title", "Content", parent, duration=0)
    assert bar.property("breezeInfoBar") is True


def test_infobar_class_methods_construct(qapp):
    parent = QWidget()
    parent.resize(400, 300)
    for factory in (InfoBar.info, InfoBar.success, InfoBar.warning, InfoBar.error):
        bar = factory("Title", "Content", parent, duration=0)
        assert bar.property("breezeInfoBar") is True


def test_infobar_auto_closes_after_duration(qapp, qtbot):
    parent = QWidget()
    parent.resize(400, 300)
    qtbot.addWidget(parent)
    parent.show()
    bar = InfoBar.info("T", "C", parent, duration=50)
    assert bar.isVisible()
    # The timeout deletes the bar; only its parent belongs to qtbot cleanup.
    with qtbot.waitSignal(bar.destroyed, timeout=1500):
        pass


def test_infobar_does_not_autoclose_when_duration_zero(qapp, qtbot):
    parent = QWidget()
    parent.resize(400, 300)
    qtbot.addWidget(parent)
    parent.show()
    bar = InfoBar.info("T", "C", parent, duration=0)
    qtbot.wait(150)
    assert bar.isVisible()
