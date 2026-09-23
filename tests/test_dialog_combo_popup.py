"""Rendering regressions for combo popups inside dialog content."""
import pytest

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QImage
from PySide6.QtWidgets import QWidget

from breezewidget import ComboBox, EditableComboBox, LineEdit, Theme, ThemeManager, getPalette, setTheme
from breezewidget.dialogs import MaskedMessageBoxBase, MessageBoxBase


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
