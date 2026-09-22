from __future__ import annotations

from PySide6.QtCore import QRect
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QDateEdit,
    QDateTimeEdit,
    QDoubleSpinBox,
    QSpinBox,
    QStyle,
    QStyleOptionComboBox,
    QStyleOptionSpinBox,
    QTimeEdit,
    QWidget,
)

from ..theme import getPalette
from ._chevron import paint_chevron


def _spin_arrow_rect(widget: QAbstractSpinBox, sub_control: QStyle.SubControl) -> QRect:
    option = QStyleOptionSpinBox()
    widget.initStyleOption(option)
    return widget.style().subControlRect(
        QStyle.ComplexControl.CC_SpinBox,
        option,
        sub_control,
        widget,
    )


def _paint_spinbox_chevrons(widget: QAbstractSpinBox, painter: QPainter) -> None:
    palette = getPalette()
    color = QColor(palette.text2 if not widget.isEnabled() else palette.text1)
    up_rect = _spin_arrow_rect(widget, QStyle.SubControl.SC_SpinBoxUp)
    down_rect = _spin_arrow_rect(widget, QStyle.SubControl.SC_SpinBoxDown)
    if not up_rect.isEmpty():
        paint_chevron(
            painter,
            cx=up_rect.center().x() + 0.5,
            cy=up_rect.center().y() + 0.5,
            half_size=4.0,
            color=color,
            stroke_width=1.4,
            direction="up",
        )
    if not down_rect.isEmpty():
        paint_chevron(
            painter,
            cx=down_rect.center().x() + 0.5,
            cy=down_rect.center().y() + 0.5,
            half_size=4.0,
            color=color,
            stroke_width=1.4,
            direction="down",
        )


def _paint_calendar_chevron(widget: QAbstractSpinBox, painter: QPainter) -> None:
    """Date/Time edits with calendarPopup expose a combo-style drop-down arrow."""
    option = QStyleOptionComboBox()
    option.initFrom(widget)
    option.subControls = QStyle.SubControl.SC_ComboBoxArrow
    arrow_rect = widget.style().subControlRect(
        QStyle.ComplexControl.CC_ComboBox,
        option,
        QStyle.SubControl.SC_ComboBoxArrow,
        widget,
    )
    if arrow_rect.isEmpty():
        arrow_rect = QRect(widget.width() - 24, 0, 24, widget.height())
    palette = getPalette()
    color = QColor(palette.text2 if not widget.isEnabled() else palette.text1)
    paint_chevron(
        painter,
        cx=arrow_rect.center().x() + 0.5,
        cy=arrow_rect.center().y() + 0.5,
        half_size=5.0,
        color=color,
        stroke_width=1.5,
        direction="down",
    )


def _paint_breeze_spin_chrome(widget: QAbstractSpinBox) -> None:
    painter = QPainter(widget)
    if hasattr(widget, "calendarPopup") and widget.calendarPopup():
        _paint_calendar_chevron(widget, painter)
    else:
        _paint_spinbox_chevrons(widget, painter)
    painter.end()


class _BreezeSpinMixin:
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setMinimumHeight(34)

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        _paint_breeze_spin_chrome(self)


class _CalendarPopupMixin:
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setCalendarPopup(True)


class SpinBox(_BreezeSpinMixin, QSpinBox):
    pass


class DoubleSpinBox(_BreezeSpinMixin, QDoubleSpinBox):
    pass


class DateEdit(_CalendarPopupMixin, _BreezeSpinMixin, QDateEdit):
    pass


class TimeEdit(_BreezeSpinMixin, QTimeEdit):
    pass


class DateTimeEdit(_CalendarPopupMixin, _BreezeSpinMixin, QDateTimeEdit):
    pass
