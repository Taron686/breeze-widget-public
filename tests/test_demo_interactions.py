"""Exercise the gallery's actual controls and callbacks."""
import pytest

from PySide6.QtCore import QTimer, Qt

from breezewidget import BodyLabel, PushButton, Theme, ThemeManager, setTheme
from breezewidget.dialogs import Dialog, MaskedDialog
from examples.widget_demo_pages.animations import AnimationsDemoPage
from examples.widget_demo_pages.dialogs import DialogsDemoPage


def test_demo_pulse_visibly_fades_child_panel_and_restores_it(qapp, qtbot):
    page = AnimationsDemoPage()
    qtbot.addWidget(page)
    page.resize(1000, 700)
    page.show()
    qapp.processEvents()
    label = next(w for w in page.findChildren(BodyLabel) if "animate opacity" in w.text())
    panel = label.parentWidget()
    row = panel.parentWidget()
    before = row.grab(panel.geometry()).toImage()
    button = next(w for w in page.findChildren(PushButton) if w.text() == "Pulse")
    button.click()
    animation = page._prop_anim
    animation.pause()
    animation.setCurrentTime(animation.duration() // 2)
    qapp.processEvents()
    assert row.grab(panel.geometry()).toImage() != before
    animation.setCurrentTime(animation.duration())
    qapp.processEvents()
    assert row.grab(panel.geometry()).toImage() == before


@pytest.mark.parametrize("method,dialog_type", [
    ("_openDialog", Dialog), ("_openMessageBox", Dialog),
    ("_openMaskedDialog", MaskedDialog),
])
@pytest.mark.parametrize("accept", [False, True])
def test_demo_dialog_actions_and_open_theme_switch(qapp, qtbot, method, dialog_type, accept):
    old_theme = ThemeManager.instance().currentTheme
    old_stylesheet = qapp.styleSheet()
    page = DialogsDemoPage()
    qtbot.addWidget(page)
    page.resize(1000, 700)
    page.show()
    visited = []

    def finish_dialog():
        dialogs = [w for w in qapp.allWidgets() if isinstance(w, dialog_type) and w.isVisible()]
        for dialog in dialogs:
            try:
                setTheme(Theme.LIGHT)
                setTheme(Theme.DARK)
                assert not dialog.grab().isNull()
                dialog.finished.connect(visited.append)
                (dialog.yesButton if accept else dialog.cancelButton).click()
            except Exception:
                dialog.close()
                raise

    timer = QTimer(page)
    timer.setSingleShot(True)
    timer.timeout.connect(finish_dialog)
    try:
        timer.start(100)
        getattr(page, method)()
        assert visited == [int(accept)]
        if method != "_openMessageBox":
            assert ("accepted" if accept else "cancelled") in page._statusLabel.text()
    finally:
        setTheme(old_theme)
        qapp.setStyleSheet(old_stylesheet)


def test_demo_navigation_callbacks(qapp, qtbot):
    from breezewidget import BreadcrumbBar, Pivot, SegmentedWidget, TabBar
    from examples.widget_demo_pages.navigation import NavigationDemoPage

    page = NavigationDemoPage()
    qtbot.addWidget(page)
    page.show()
    for widget_type, key in ((Pivot, "stats"), (SegmentedWidget, "week")):
        widget = page.findChild(widget_type)
        widget.items()[1].click()
        assert widget.currentRoute() == key
        assert page._statusLabel.text().endswith(key)
    breadcrumb = page.findChild(BreadcrumbBar)
    breadcrumb.items()[0].click()
    assert breadcrumb.currentRoute() == "home"
    assert len(breadcrumb.items()) == 1
    tabs = page.findChild(TabBar)
    tabs.setCurrentRoute("b")
    assert page._statusLabel.text() == "TabBar: b"
    tabs.tabs()[1]._close_button.click()
    assert [tab.routeKey() for tab in tabs.tabs()] == ["a", "c"]
    assert tabs.currentRoute() in ("a", "c")


def test_demo_split_actions_and_menu_theme_refresh(qapp, qtbot):
    from breezewidget import SplitPushButton
    from examples.widget_demo_pages.basic_input import WidgetDemoPage

    old_theme = ThemeManager.instance().currentTheme
    page = WidgetDemoPage()
    qtbot.addWidget(page)
    page.show()
    button = page.findChild(SplitPushButton)
    try:
        button._button.click()
        assert page._statusLabel.text() == "Split-Hauptaktion ausgefuehrt"
        for theme in (Theme.DARK, Theme.LIGHT):
            button.showMenu()
            setTheme(theme)
            assert not button.menu().grab().isNull()
            action = button.menu().actions()[1]
            button.menu().setActiveAction(action)
            qtbot.keyClick(button.menu(), Qt.Key_Return)
            assert page._statusLabel.text() == "Split-Menue: Mit Protokoll"
            assert not button.menu().isVisible()
    finally:
        button.menu().hide()
        setTheme(old_theme)


def test_demo_flyouts_open_and_dismiss(qapp, qtbot):
    from breezewidget import Flyout
    from examples.widget_demo_pages.flyouts import DialogsFlyoutsDemoPage

    page = DialogsFlyoutsDemoPage()
    qtbot.addWidget(page)
    page.show()
    for text in ("TeachingTip zeigen", "Flyout zeigen"):
        button = next(w for w in page.findChildren(PushButton) if w.text() == text)
        button.click()
        popup = next(w for w in page.findChildren(Flyout) if w.isVisible())
        qtbot.wait(250)
        assert not popup.grab().isNull()
        qtbot.keyClick(popup, Qt.Key_Escape)
        assert not popup.isVisible()




@pytest.mark.parametrize("accept", [False, True])
def test_demo_color_dialog_respects_cancel(qapp, qtbot, accept):
    from breezewidget.dialogs import ColorDialog

    page = DialogsDemoPage()
    qtbot.addWidget(page)
    original = page._color.name()
    visited = []

    def choose_color():
        dialog = next(w for w in qapp.topLevelWidgets() if isinstance(w, ColorDialog) and w.isVisible())
        dialog._spins["R"].setValue(200)
        visited.append(dialog.color().name())
        (dialog.yesButton if accept else dialog.cancelButton).click()

    QTimer.singleShot(100, choose_color)
    page._openColorDialog()
    assert visited
    assert page._color.name() == (visited[0] if accept else original)


def test_demo_infrastructure_save_reload_reset_and_tools(qapp, qtbot, tmp_path, monkeypatch):
    import tempfile
    from breezewidget import ComboBox, SpinBox
    from examples.widget_demo_pages.infrastructure import InfrastructureDemoPage

    monkeypatch.setattr(tempfile, "gettempdir", lambda: str(tmp_path))
    page = InfrastructureDemoPage()
    qtbot.addWidget(page)
    buttons = {w.text(): w for w in page.findChildren(PushButton)}
    volume = page.findChild(SpinBox)
    quality = page.findChild(ComboBox)
    volume.setValue(23)
    quality.setCurrentText("high")
    buttons["Save"].click()
    assert (tmp_path / "breeze_demo_settings.json").exists()
    buttons["Reset"].click()
    assert volume.value() == 50 and quality.currentText() == "medium"
    buttons["Reload"].click()
    assert volume.value() == 23 and quality.currentText() == "high"
    buttons["Trigger ValueError"].click()
    assert "Caught: ValueError" in page._exc_log.text()
    buttons["Use system locale"].click()
    buttons["Clear"].click()
    buttons["Start polling"].click()
    assert page._listener.isRunning()
    buttons["Stop"].click()
    assert not page._listener.isRunning()


@pytest.mark.parametrize("accept", [False, True])
def test_demo_folder_dialog_commits_only_on_accept(qapp, qtbot, tmp_path, accept):
    from breezewidget.dialogs import FolderListDialog

    page = DialogsDemoPage()
    qtbot.addWidget(page)
    page._folders = [str(tmp_path)]

    def remove_folder():
        dialog = next(w for w in qapp.topLevelWidgets()
                      if isinstance(w, FolderListDialog) and w.isVisible())
        dialog.listWidget().setCurrentRow(0)
        dialog.removeButton.click()
        (dialog.yesButton if accept else dialog.cancelButton).click()

    QTimer.singleShot(100, remove_folder)
    page._openFolderDialog()
    assert page._folders == ([] if accept else [str(tmp_path)])
