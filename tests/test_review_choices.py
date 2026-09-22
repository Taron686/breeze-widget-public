import pytest
from PySide6.QtCore import Qt
from breezewidget import CheckBox, RadioButton, Theme, setTheme


@pytest.mark.parametrize("cls", [CheckBox, RadioButton])
@pytest.mark.parametrize("theme", [Theme.LIGHT, Theme.DARK])
def test_disabled_choice_preserves_visible_selection(qapp, qtbot, cls, theme):
    setTheme(theme, qapp)
    widget = cls()
    qtbot.addWidget(widget)
    widget.resize(30, 28)
    widget.setEnabled(False)
    widget.show()
    unchecked = widget.grab().toImage()
    widget.setChecked(True)
    assert widget.grab().toImage() != unchecked
    if cls is CheckBox:
        widget.setCheckState(Qt.CheckState.PartiallyChecked)
        assert widget.grab().toImage() != unchecked
