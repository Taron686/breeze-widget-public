import pytest
from PySide6.QtGui import QColor

from breezewidget import ComboBox, EditableComboBox, Theme, getPalette, setTheme


@pytest.mark.parametrize("cls", [ComboBox, EditableComboBox])
def test_dropdown_rows_remain_opaque_after_theme_changes(qapp, qtbot, cls):
    combo = cls()
    qtbot.addWidget(combo)
    combo.resize(250, 40)
    combo.addItems(["Selected", "Second", "Third"])
    combo.show()
    for theme in (Theme.LIGHT, Theme.DARK, Theme.LIGHT):
        setTheme(theme, qapp)
        combo.showPopup()
        qapp.processEvents()
        try:
            view = combo.view()
            image = view.viewport().grab().toImage()
            for row in (1, 2):
                rect = view.visualRect(combo.model().index(row, 0))
                rect = rect.intersected(view.viewport().rect())
                assert not rect.isEmpty()
                color = image.pixelColor(rect.right() - 12, rect.center().y())
                assert color.alpha() == 255
                assert color == QColor(getPalette().surface2)
        finally:
            combo.hidePopup()
