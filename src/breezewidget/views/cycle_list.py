"""CycleListWidget — list with wrap-around navigation.

Useful for picker rollers (hour, day, …): instead of clamping the
selection at the ends, advancing past the last item wraps back to the
first.  Designed as a thin :class:`QListWidget` subclass so all
existing model APIs keep working.
"""
from __future__ import annotations

from typing import Iterable

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QWidget

from ..constants import PROP_CYCLE_LIST


class CycleListWidget(QListWidget):
    """List widget where Up/Down navigation wraps around at both ends.

    ``selectionChanged`` is the standard Qt signal; this class adds
    :pyattr:`currentTextChanged` to make plain text consumers easier
    to wire up (already exists on QListWidget).  The new bit here is
    :meth:`stepNext` / :meth:`stepPrevious` and key handling for
    Up/Down.
    """

    cycled = Signal(int)  # emitted with new row when wrap-around happens

    def __init__(
        self,
        items: Iterable[str] = (),
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setProperty(PROP_CYCLE_LIST, True)
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.addItems(list(items))
        if self.count() > 0:
            self.setCurrentRow(0)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def stepNext(self) -> None:
        if self.count() == 0:
            return
        new_row = (self.currentRow() + 1) % self.count()
        wrapped = new_row < self.currentRow()
        self.setCurrentRow(new_row)
        if wrapped:
            self.cycled.emit(new_row)

    def stepPrevious(self) -> None:
        if self.count() == 0:
            return
        new_row = (self.currentRow() - 1) % self.count()
        wrapped = new_row > self.currentRow()
        self.setCurrentRow(new_row)
        if wrapped:
            self.cycled.emit(new_row)

    def addItem(self, item) -> None:  # type: ignore[override]
        if isinstance(item, str):
            super().addItem(QListWidgetItem(item))
        else:
            super().addItem(item)

    # ------------------------------------------------------------------
    # Event override
    # ------------------------------------------------------------------

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Down:
            self.stepNext()
            event.accept()
            return
        if event.key() == Qt.Key.Key_Up:
            self.stepPrevious()
            event.accept()
            return
        super().keyPressEvent(event)
