from __future__ import annotations

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QComboBox, QStyle, QStyleOptionComboBox, QWidget

from ..theme import getPalette
from ._chevron import paint_chevron
from ._popup import apply_breeze_popup_window


class ComboBox(QComboBox):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setMinimumHeight(34)
        self._popupStyled = False

    def showPopup(self) -> None:
        if not self._popupStyled:
            apply_breeze_popup_window(self.view().window())
            self._popupStyled = True
        super().showPopup()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        option = QStyleOptionComboBox()
        self.initStyleOption(option)
        arrow_rect: QRect = self.style().subControlRect(
            QStyle.ComplexControl.CC_ComboBox,
            option,
            QStyle.SubControl.SC_ComboBoxArrow,
            self,
        )
        if arrow_rect.isEmpty():
            arrow_rect = QRect(self.width() - 24, 0, 24, self.height())

        painter = QPainter(self)
        palette = getPalette()
        color = QColor(palette.text2 if not self.isEnabled() else palette.text1)
        paint_chevron(
            painter,
            cx=arrow_rect.center().x() + 0.5,
            cy=arrow_rect.center().y() + 0.5,
            half_size=5.0,
            color=color,
            stroke_width=1.5,
            direction="down",
        )
        painter.end()


class EditableComboBox(ComboBox):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setEditable(True)
