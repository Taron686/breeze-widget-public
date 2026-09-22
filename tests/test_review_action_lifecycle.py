from PySide6.QtCore import QCoreApplication, QEvent, SIGNAL
from PySide6.QtGui import QAction, QIcon
from shiboken6 import delete, isValid

from breezewidget import BreezeIcon, CommandBar, RoundMenu
from breezewidget.icons._themed import ThemedActionIcons


def test_menu_clear_allows_theme_refresh(qapp, qtbot):
    menu = RoundMenu()
    qtbot.addWidget(menu)
    menu.addBreezeAction(BreezeIcon.HOME, "Home")
    menu.clear()
    menu.refreshTheme()
    survivor = menu.addBreezeAction(BreezeIcon.SAVE, "Save")
    menu.refreshTheme()
    assert not survivor.icon().isNull()


def test_deleted_action_does_not_block_survivor_refresh(qapp):
    icons = ThemedActionIcons()
    dead, survivor = QAction(), QAction()
    icons.set(dead, BreezeIcon.HOME)
    icons.set(survivor, BreezeIcon.SAVE)
    dead.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    icons.refresh()
    assert not survivor.icon().isNull()


def test_repeated_sources_keep_one_cleanup_connection(qapp):
    icons = ThemedActionIcons()
    action, survivor = QAction(), QAction()
    icons.set(survivor, BreezeIcon.SAVE)
    signal = SIGNAL("destroyed(QObject*)")
    baseline = action.receivers(signal)
    icons.set(action, BreezeIcon.HOME)
    connected = action.receivers(signal)
    assert connected > baseline
    for source in (BreezeIcon.HOME, BreezeIcon.SAVE, QIcon(), None, BreezeIcon.HOME):
        icons.set(action, source)
        icons.refresh()
        assert not survivor.icon().isNull()
        if source is None or isinstance(source, QIcon):
            assert action.icon().isNull()
    assert action.receivers(signal) == connected
    delete(action)
    icons.refresh()
    assert not survivor.icon().isNull()


def test_refresh_handles_deletion_during_action_changed(qapp):
    icons = ThemedActionIcons()
    first, second = QAction(), QAction()
    icons.set(first, BreezeIcon.HOME)
    icons.set(second, BreezeIcon.SAVE)
    first.changed.connect(lambda: delete(second) if isValid(second) else None)
    icons.refresh()
    assert not isValid(second)
    assert not first.icon().isNull()


def test_overflow_clear_preserves_shared_action(qapp, qtbot):
    bar = CommandBar()
    qtbot.addWidget(bar)
    action = bar.addAction(icon=BreezeIcon.HOME, text="A long action title")
    bar.setFixedWidth(60)
    bar.show()
    qapp.processEvents()
    assert action in bar.overflowMenu().actions()
    bar.setFixedWidth(1000)
    qapp.processEvents()
    assert not bar.overflowMenu().actions()
    assert isValid(action)
    bar.refreshTheme()
    assert not action.icon().isNull()
