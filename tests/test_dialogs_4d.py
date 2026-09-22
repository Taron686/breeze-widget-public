"""Smoke tests for Phase 4d: MessageBoxBase, Dialog, ColorDialog, FolderListDialog."""
from __future__ import annotations

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QColor
from PySide6.QtGui import QImage

from breezewidget import (
    MessageBox,
    Theme,
    ThemeManager,
    getPalette,
    setTheme,
    setThemeColor,
)
from breezewidget.dialogs import ColorDialog, Dialog, FolderListDialog, MessageBoxBase


# ---------------------------------------------------------------------------
# MessageBoxBase / Dialog / MessageBox
# ---------------------------------------------------------------------------

def test_message_box_base_has_buttons(qapp):
    dlg = MessageBoxBase("Title")
    assert dlg.yesButton is not None
    assert dlg.cancelButton is not None
    assert dlg.property("breezeDialog") is True


def test_message_box_base_set_title(qapp):
    dlg = MessageBoxBase("Original")
    dlg.setTitle("Updated")
    assert dlg.titleLabel.text() == "Updated"
    assert dlg.windowTitle() == "Updated"


def test_message_box_base_set_button_text(qapp):
    dlg = MessageBoxBase()
    dlg.setYesText("Apply")
    dlg.setCancelText("Discard")
    assert dlg.yesButton.text() == "Apply"
    assert dlg.cancelButton.text() == "Discard"


def test_message_box_base_accepts_parent_first_constructor(qapp):
    parent = Dialog("Host", "Body")
    dlg = MessageBoxBase(parent)
    assert dlg.parent() is parent
    assert dlg.windowTitle() == ""


def test_message_box_base_compat_properties(qapp):
    dlg = MessageBoxBase("Title")
    assert dlg.widget is dlg
    assert dlg.buttonLayout is dlg._buttonRow


def test_dialog_constructs_with_content(qapp):
    dlg = Dialog("Hi", "body content")
    assert dlg.contentLabel.text() == "body content"
    dlg.setContentText("changed")
    assert dlg.contentLabel.text() == "changed"


def test_dialog_title_bar_uses_footer_background(qapp):
    manager = ThemeManager.instance()
    old_theme = manager.currentTheme
    old_accent = manager.accentColor
    old_stylesheet = qapp.styleSheet()
    try:
        setTheme(Theme.DARK, qapp)
        palette = getPalette()
        dlg = Dialog("Hi", "body content")
        dlg.show()
        qapp.processEvents()

        image = QImage(dlg.size(), QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(Qt.GlobalColor.transparent)
        dlg.render(image)

        title_pos = dlg.titleBar.mapTo(dlg, QPoint(dlg.titleBar.width() // 2, dlg.titleBar.height() // 2))
        body_pos = dlg._body.mapTo(dlg, QPoint(dlg._body.width() // 2, dlg._body.height() // 2))
        footer_pos = dlg._buttonGroup.mapTo(
            dlg,
            QPoint(dlg._buttonGroup.width() // 2, dlg._buttonGroup.height() // 2),
        )

        assert image.pixelColor(title_pos).name() == palette.surface1
        assert image.pixelColor(footer_pos).name() == palette.surface1
        assert image.pixelColor(body_pos).name() == palette.surface2
    finally:
        setTheme(old_theme, qapp)
        setThemeColor(old_accent, qapp)
        qapp.setStyleSheet(old_stylesheet)


def test_message_box_is_dialog_subclass(qapp):
    box = MessageBox("T", "C")
    assert isinstance(box, Dialog)
    assert isinstance(box, MessageBoxBase)


def test_message_box_base_yes_emits_accepted(qapp, qtbot):
    dlg = MessageBoxBase()
    with qtbot.waitSignal(dlg.accepted, timeout=500):
        dlg.yesButton.click()


def test_message_box_base_cancel_emits_rejected(qapp, qtbot):
    dlg = MessageBoxBase()
    with qtbot.waitSignal(dlg.rejected, timeout=500):
        dlg.cancelButton.click()


# ---------------------------------------------------------------------------
# ColorDialog
# ---------------------------------------------------------------------------

def test_color_dialog_initial_color(qapp):
    dlg = ColorDialog("#ff8800")
    color = dlg.color()
    assert color.red() == 0xFF
    assert color.green() == 0x88
    assert color.blue() == 0x00


def test_color_dialog_set_color(qapp, qtbot):
    dlg = ColorDialog("#000000")
    with qtbot.waitSignal(dlg.colorChanged, timeout=500):
        dlg.setColor("#11dd44")
    assert dlg.color().name() == "#11dd44"


def test_color_dialog_invalid_color_ignored(qapp):
    dlg = ColorDialog("#11dd44")
    dlg.setColor("not-a-color")
    assert dlg.color().name() == "#11dd44"


def test_color_dialog_slider_updates_color(qapp):
    dlg = ColorDialog("#000000")
    dlg._sliders["R"].setValue(200)
    assert dlg.color().red() == 200
    # Spin is kept in sync.
    assert dlg._spins["R"].value() == 200


def test_color_dialog_spin_updates_color(qapp):
    dlg = ColorDialog("#000000")
    dlg._spins["G"].setValue(123)
    assert dlg.color().green() == 123
    assert dlg._sliders["G"].value() == 123


# ---------------------------------------------------------------------------
# FolderListDialog
# ---------------------------------------------------------------------------

def test_folder_list_dialog_initial_folders(qapp):
    dlg = FolderListDialog(["C:/a", "C:/b"])
    assert dlg.folders() == ["C:/a", "C:/b"]


def test_folder_list_dialog_add_folder_emits(qapp, qtbot):
    dlg = FolderListDialog()
    with qtbot.waitSignal(dlg.foldersChanged, timeout=500) as sig:
        dlg.addFolder("C:/x")
    assert sig.args == [["C:/x"]]


def test_folder_list_dialog_dedup(qapp):
    dlg = FolderListDialog(["C:/x"])
    dlg.addFolder("C:/x")
    assert dlg.folders() == ["C:/x"]


def test_folder_list_dialog_set_folders_replaces(qapp):
    dlg = FolderListDialog(["a", "b"])
    dlg.setFolders(["c"])
    assert dlg.folders() == ["c"]


def test_folder_list_dialog_remove_selected(qapp):
    dlg = FolderListDialog(["a", "b", "c"])
    dlg.listWidget().setCurrentRow(1)
    dlg._onRemove()
    assert dlg.folders() == ["a", "c"]
