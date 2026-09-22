import pytest
from PySide6.QtCore import QPoint, Qt
from breezewidget import SwitchButton


@pytest.mark.parametrize("position", ["left", "right"])
def test_switch_track_and_label_are_clickable(qtbot, position):
    switch = SwitchButton()
    switch.setStateLabelPosition(position)
    qtbot.addWidget(switch)
    switch.resize(switch.sizeHint())
    switch.show()
    qtbot.mouseClick(switch, Qt.MouseButton.LeftButton,
                     pos=switch._switchTrackRect().center().toPoint())
    assert switch.isChecked()
    qtbot.mouseClick(switch, Qt.MouseButton.LeftButton,
                     pos=QPoint(switch.width() - 5, switch.height() // 2))
    assert not switch.isChecked()
