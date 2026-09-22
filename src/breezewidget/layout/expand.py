from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget


class ExpandLayout(QVBoxLayout):
    """Vertical layout with Breeze-standard spacing and zero outer margins.

    A thin wrapper around ``QVBoxLayout`` that applies consistent defaults:

    * ``spacing = 8 px``
    * ``contentsMargins = 0``

    Animation is intentionally omitted — animating a layout's items requires
    the parent widget to control its own ``maximumHeight``, which is the
    responsibility of the widget (e.g. ``ExpandSettingCard``), not the layout.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setSpacing(8)
        self.setContentsMargins(0, 0, 0, 0)

    def addWidget(  # type: ignore[override]
        self,
        widget: QWidget,
        stretch: int = 0,
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag(0),
    ) -> None:
        super().addWidget(widget, stretch, alignment)
