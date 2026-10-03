"""Rendering regressions for combo popups inside dialog content."""
import pytest

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QImage, QPalette
from PySide6.QtWidgets import QVBoxLayout, QWidget

from breezewidget import ComboBox, EditableComboBox, LineEdit, Theme, ThemeManager, getPalette, setTheme
from breezewidget.dialogs import MaskedMessageBoxBase, MessageBoxBase


@pytest.mark.parametrize("combo_type", [ComboBox, EditableComboBox])
@pytest.mark.parametrize("in_dialog", [False, True])
@pytest.mark.parametrize("change_while_open", [False, True])
def test_combo_popup_container_tracks_theme(qapp, qtbot, combo_type, in_dialog, change_while_open):
    """Native popup margins must match the list, even after reuse/theme changes."""
    old_theme = ThemeManager.instance().currentTheme
    old_stylesheet = qapp.styleSheet()
    old_style = qapp.style().objectName()
    old_palette = qapp.palette()
    host = MessageBoxBase("Popup regression") if in_dialog else QWidget()
    qtbot.addWidget(host)
    layout = host.viewLayout if in_dialog else QVBoxLayout(host)
    combo = combo_type()
    combo.addItems(["First", "Second", "Third"])
    layout.addWidget(combo)
    try:
        qapp.setStyle("Fusion")
        host.resize(350, 240)
        host.show()
        host.activateWindow()
        qtbot.waitUntil(host.isActiveWindow)
        qapp.processEvents()
        for index, theme in enumerate((Theme.DARK, Theme.LIGHT, Theme.DARK)):
            setTheme(theme, qapp)
            if index == 0 or not change_while_open:
                combo.setFocus()
                qapp.processEvents()
                combo.showPopup()
                qtbot.waitUntil(combo.view().window().isVisible)
            qapp.processEvents()
            popup = combo.view().window()
            assert popup.isVisible()
            background = QColor(getPalette().surface2)
            for group in (QPalette.Active, QPalette.Inactive, QPalette.Disabled):
                for role in (QPalette.Window, QPalette.Base):
                    assert popup.palette().color(group, role) == background
            # Fusion's non-editable menu leaves space above the list. Render
            # that exposed container area, which was white in the Fedora case.
            if combo.view().y() > 2:
                image = popup.grab().toImage()
                margin_y = int(combo.view().y() / 2 * image.devicePixelRatio())
                pixel = image.pixelColor(image.width() // 2, margin_y)
                # Fusion adds a small native gradient over the palette color.
                assert pixel.alpha() == 255
                assert all(abs(actual - expected) <= 12 for actual, expected in
                           zip(pixel.getRgb()[:3], background.getRgb()[:3]))
            if not change_while_open:
                combo.hidePopup()
        combo.hidePopup()
        combo.showPopup()
        qtbot.waitUntil(combo.view().window().isVisible)
        qapp.processEvents()
        qtbot.keyClick(combo.view(), Qt.Key_Down)
        qtbot.keyClick(combo.view(), Qt.Key_Return)
        assert combo.currentIndex() == 1
        assert not combo.view().window().isVisible()
    finally:
        combo.hidePopup()
        host.close()
        qapp.setStyle(old_style)
        qapp.setPalette(old_palette)
        setTheme(old_theme, qapp)
        qapp.setStyleSheet(old_stylesheet)


@pytest.mark.parametrize("theme", [Theme.DARK, Theme.LIGHT])
@pytest.mark.parametrize("combo_type", [ComboBox, EditableComboBox])
@pytest.mark.parametrize("dialog_type", [MessageBoxBase, MaskedMessageBoxBase])
def test_dialog_combo_popup_has_opaque_themed_background(qapp, qtbot, theme, combo_type, dialog_type):
    old_theme = ThemeManager.instance().currentTheme
    old_stylesheet = qapp.styleSheet()
    host = QWidget()
    qtbot.addWidget(host)
    host.resize(640, 480)
    host.show()
    dialog = dialog_type("Popup regression", parent=host)
    qtbot.addWidget(dialog)
    combo = combo_type()
    combo.addItems(["First", "Second", "Third"])
    dialog.viewLayout.addWidget(combo)
    dialog.viewLayout.addWidget(LineEdit())
    try:
        setTheme(theme, qapp)
        dialog.show()
        qapp.processEvents()
        combo.showPopup()
        qapp.processEvents()

        popup = combo.view().window()
        image = QImage(popup.size(), QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(Qt.GlobalColor.transparent)
        popup.render(image)
        # Sample away from text in an unselected row, in popup coordinates.
        view = combo.view()
        row = view.visualRect(combo.model().index(1, 0))
        point = view.viewport().mapTo(popup, row.center())
        assert image.pixelColor(point) == QColor(getPalette().surface2)
        assert popup.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    finally:
        combo.hidePopup()
        dialog.close()
        setTheme(old_theme, qapp)
        qapp.setStyleSheet(old_stylesheet)


@pytest.mark.parametrize('combo_type', [ComboBox, EditableComboBox])
@pytest.mark.parametrize('text,width', [('31', 58), ('2026', 75), ('September', 110)])
def test_narrow_combo_popup_fits_complete_items(qapp, qtbot, combo_type, text, width):
    old_theme = ThemeManager.instance().currentTheme
    old_stylesheet = qapp.styleSheet()
    combo = combo_type()
    qtbot.addWidget(combo)
    combo.addItems([text] * 20)
    combo.setFixedWidth(width)
    try:
        setTheme(Theme.DARK, qapp)
        combo.show()
        combo.showPopup()
        qapp.processEvents()
        view = combo.view()
        # The styled item hint includes the text, padding and margins. The
        # viewport must accommodate it even when a scrollbar consumes space.
        assert view.viewport().width() >= view.sizeHintForColumn(0)
        combo.hidePopup()
        combo.setItemText(1, 'A considerably longer dropdown entry')
        combo.showPopup()
        qapp.processEvents()
        assert view.viewport().width() >= view.sizeHintForColumn(0)
        qtbot.keyClick(view, Qt.Key_Down)
        qtbot.keyClick(view, Qt.Key_Return)
        assert combo.currentIndex() == 1
    finally:
        combo.hidePopup()
        combo.close()
        setTheme(old_theme, qapp)
        qapp.setStyleSheet(old_stylesheet)
