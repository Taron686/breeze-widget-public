import pytest
from PySide6.QtWidgets import QWidget
from breezewidget import BreezeWindow, Theme, applyTheme, setCustomStyleSheet, setTheme


@pytest.mark.parametrize("direct", [False, True])
def test_custom_stylesheet_survives_repeated_theme_application(qapp, qtbot, direct):
    setTheme(Theme.LIGHT, qapp)
    widget = QWidget()
    qtbot.addWidget(widget)
    light = "QWidget { color: #112233; }"
    dark = "QWidget { color: #ddeeff; }"
    setCustomStyleSheet(widget, light, dark)
    target = widget if direct else qapp
    applyTheme(target)
    assert widget.styleSheet() == light
    setTheme(Theme.LIGHT, target)
    assert widget.styleSheet() == light
    setTheme(Theme.DARK, target)
    assert widget.styleSheet() == dark


def test_global_theme_preserves_unmanaged_window_stylesheet(qapp, qtbot):
    widget = QWidget()
    qtbot.addWidget(widget)
    widget.setStyleSheet("QWidget { color: #123456; }")
    applyTheme(qapp)
    assert widget.styleSheet() == "QWidget { color: #123456; }"


def test_breeze_window_managed_stylesheet_follows_global_theme(qapp, qtbot):
    setTheme(Theme.LIGHT, qapp)
    window = BreezeWindow()
    qtbot.addWidget(window)
    before = window.styleSheet()
    setTheme(Theme.DARK, qapp)
    assert window.styleSheet() != before
