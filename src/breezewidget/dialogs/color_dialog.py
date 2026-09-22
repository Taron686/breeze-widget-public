"""ColorDialog — Breeze-styled RGB/Hex color picker dialog."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QWidget,
)

from ..widgets.line_edit import LineEdit
from ..widgets.slider import Slider
from ..widgets.spin_box import SpinBox
from .base import MessageBoxBase


class _ColorSwatch(QFrame):
    """Solid rectangle preview, repaints on :meth:`setColor`."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setMinimumSize(64, 32)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._color = QColor("#000000")

    def setColor(self, color: QColor) -> None:
        self._color = QColor(color)
        self.update()

    def color(self) -> QColor:
        return QColor(self._color)

    def paintEvent(self, event) -> None:
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._color)
        painter.drawRoundedRect(self.rect().adjusted(0, 0, -1, -1), 6, 6)
        painter.end()


class ColorDialog(MessageBoxBase):
    """Pick an RGB color via three sliders, three spin boxes and a hex input.

    All inputs stay in sync.  ``colorChanged`` fires whenever the
    internal color updates from any source (slider, spin box, hex edit
    or :meth:`setColor`).  Read the final value with :meth:`color`.
    """

    colorChanged = Signal(QColor)

    def __init__(
        self,
        color: QColor | str = "#1f6feb",
        title: str = "Choose color",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(title, parent)
        self._color = QColor(color)
        self._suspend = False

        self._swatch = _ColorSwatch(self)
        self.addContentWidget(self._swatch)

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(6)
        self._sliders: dict[str, Slider] = {}
        self._spins: dict[str, SpinBox] = {}
        for row, channel in enumerate(("R", "G", "B")):
            label = QLabel(channel, self)
            slider = Slider(Qt.Orientation.Horizontal, self)
            slider.setRange(0, 255)
            spin = SpinBox(self)
            spin.setRange(0, 255)
            slider.valueChanged.connect(
                lambda v, ch=channel: self._onChannelChanged(ch, v, source="slider")
            )
            spin.valueChanged.connect(
                lambda v, ch=channel: self._onChannelChanged(ch, v, source="spin")
            )
            grid.addWidget(label, row, 0)
            grid.addWidget(slider, row, 1)
            grid.addWidget(spin, row, 2)
            self._sliders[channel] = slider
            self._spins[channel] = spin
        self.addContentLayout(grid)

        hex_row = QHBoxLayout()
        hex_row.addWidget(QLabel("Hex", self))
        self._hexEdit = LineEdit(self)
        self._hexEdit.setMaxLength(7)
        self._hexEdit.editingFinished.connect(self._onHexEdited)
        hex_row.addWidget(self._hexEdit, 1)
        self.addContentLayout(hex_row)

        self.setColor(self._color)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def color(self) -> QColor:
        return QColor(self._color)

    def setColor(self, color: QColor | str) -> None:
        new = QColor(color)
        if not new.isValid():
            return
        self._color = new
        self._syncControls()
        self._swatch.setColor(self._color)
        self.colorChanged.emit(QColor(self._color))

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _onChannelChanged(self, channel: str, value: int, source: str) -> None:
        if self._suspend:
            return
        rgb = {"R": self._color.red(), "G": self._color.green(), "B": self._color.blue()}
        rgb[channel] = value
        new_color = QColor(rgb["R"], rgb["G"], rgb["B"])
        self._color = new_color
        self._suspend = True
        try:
            if source != "slider":
                self._sliders[channel].setValue(value)
            if source != "spin":
                self._spins[channel].setValue(value)
            self._hexEdit.setText(self._color.name())
        finally:
            self._suspend = False
        self._swatch.setColor(self._color)
        self.colorChanged.emit(QColor(self._color))

    def _onHexEdited(self) -> None:
        if self._suspend:
            return
        text = self._hexEdit.text().strip()
        if not text.startswith("#"):
            text = "#" + text
        new_color = QColor(text)
        if not new_color.isValid():
            self._hexEdit.setText(self._color.name())
            return
        self._color = new_color
        self._syncControls()
        self._swatch.setColor(self._color)
        self.colorChanged.emit(QColor(self._color))

    def _syncControls(self) -> None:
        self._suspend = True
        try:
            self._sliders["R"].setValue(self._color.red())
            self._sliders["G"].setValue(self._color.green())
            self._sliders["B"].setValue(self._color.blue())
            self._spins["R"].setValue(self._color.red())
            self._spins["G"].setValue(self._color.green())
            self._spins["B"].setValue(self._color.blue())
            self._hexEdit.setText(self._color.name())
        finally:
            self._suspend = False
