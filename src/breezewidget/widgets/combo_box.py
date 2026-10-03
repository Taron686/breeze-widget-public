from __future__ import annotations

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QPainter, QPalette
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
        view = self.view()
        if not self._popupStyled:
            apply_breeze_popup_window(view.window())
            self._popupStyled = True
        view.ensurePolished()
        margins = view.contentsMargins()
        # Qt sizes the popup from the combo's width, which can be too narrow
        # for styled items. Include their padding plus the view's frame and
        # scrollbar, and recalculate after item/font/theme changes.
        width = (view.sizeHintForColumn(self.modelColumn())
                 + margins.left() + margins.right()
                 + view.verticalScrollBar().sizeHint().width())
        view.setMinimumWidth(min(width, self.screen().availableGeometry().width()))
        self.refreshTheme()
        super().showPopup()
        # Qt can reset the native container palette while preparing the popup.
        self.refreshTheme()

    def refreshTheme(self) -> None:
        if not self._popupStyled:
            return
        popup = self.view().window()
        palette = popup.palette()
        background = QColor(getPalette().surface2)
        # Native menu margins and rounded list corners expose the container.
        palette.setColor(QPalette.ColorRole.Window, background)
        palette.setColor(QPalette.ColorRole.Base, background)
        popup.setPalette(palette)

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
