"""Verify PillPushButton renders with the rounded radius applied via QSS."""
from __future__ import annotations

from PySide6.QtGui import QColor

from breezewidget import PillPushButton, Theme, setTheme, setThemeColor


def test_pill_button_radius_applied(qapp, qtbot):
    setTheme(Theme.DARK, qapp)
    setThemeColor("#11d9f3", qapp)

    button = PillPushButton("Cyan")
    qtbot.addWidget(button)
    button.adjustSize()
    button.show()
    qtbot.waitExposed(button)
    qapp.processEvents()

    image = button.grab().toImage()
    top_left = QColor(image.pixel(0, 0))
    mid_left = QColor(image.pixel(0, button.height() // 2))

    # Pill rule applied: corner sits outside the rounded path so it is
    # filled with the surface background, while the middle of the left
    # edge crosses the border arc and reads as the border colour.
    assert top_left != mid_left, (
        f"corner {top_left.name()} matched mid-edge {mid_left.name()} — "
        "the pill QSS rule is not applying any rounding"
    )
    assert button.property("breezePill") == "true"
    assert button.height() == PillPushButton.PILL_HEIGHT
