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
