import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QStyle, QStyleOptionSlider
from breezewidget import Slider, ClickableSlider


@pytest.mark.parametrize("cls", [Slider, ClickableSlider])
@pytest.mark.parametrize("orientation", [Qt.Horizontal, Qt.Vertical])
@pytest.mark.parametrize("rtl", [False, True])
@pytest.mark.parametrize("inverted", [False, True])
def test_slider_paint_and_hit_geometry_agree(qtbot, cls, orientation, rtl, inverted):
    slider = cls(orientation)
    qtbot.addWidget(slider)
    slider.setLayoutDirection(Qt.RightToLeft if rtl else Qt.LeftToRight)
    slider.setInvertedAppearance(inverted)
    slider.setRange(0, 100)
    slider.setValue(25)
    slider.resize(slider.sizeHint())
    slider.show()
    option = QStyleOptionSlider()
    slider.initStyleOption(option)
    native = slider.style().subControlRect(QStyle.CC_Slider, option, QStyle.SC_SliderHandle, slider)
    painted = slider._sliderRects()[1].center().toPoint()
    assert native.contains(painted)
    qtbot.mousePress(slider, Qt.LeftButton, pos=painted)
    assert abs(slider.value() - 25) <= 1
    if cls is Slider:
        assert slider.isSliderDown()
    qtbot.mouseRelease(slider, Qt.LeftButton, pos=painted)
