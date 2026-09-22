from collections import Counter
import pytest
from PySide6.QtWidgets import QWidget
from breezewidget import BreezeWindow, SettingCard, Theme, applyTheme, setTheme, BreezeIcon


@pytest.mark.parametrize("global_change", [False, True])
def test_theme_refresh_visits_each_widget_once(qapp, qtbot, monkeypatch, global_change):
    setTheme(Theme.LIGHT, qapp)
    window = BreezeWindow()
    qtbot.addWidget(window)
    page = QWidget()
    window.addSubInterface(page, BreezeIcon.HOME, "Home")
    card = SettingCard(BreezeIcon.HOME, parent=page)
    counts = Counter()
    widgets = [window, window.titleBar, window.navigationInterface, card,
               *window.navigationInterface._buttons.values()]
    for index, widget in enumerate(widgets):
        original = widget.refreshTheme
        def counted(i=index, callback=original):
            counts[i] += 1
            callback()
        monkeypatch.setattr(widget, "refreshTheme", counted)
    if global_change:
        setTheme(Theme.DARK, qapp)
    else:
        applyTheme(window)
    assert [counts[i] for i in range(len(widgets))] == [1] * len(widgets)
