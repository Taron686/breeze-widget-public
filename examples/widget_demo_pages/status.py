"""Status & info — InfoBadge variants, ProgressRing, StateToolTip."""
from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QLabel, QWidget

from breezewidget import (
    BodyLabel,
    BreezeIcon,
    ClickableSlider,
    DotInfoBadge,
    IconInfoBadge,
    IndeterminateProgressRing,
    InfoBadge,
    ProgressRing,
    PushButton,
    StateToolTip,
)

from ._gallery import GalleryPage, _row


class StatusDemoPage(GalleryPage):
    """Phase-3a showcase: badges, progress rings, state tooltip."""

    def __init__(self):
        super().__init__("Status & info", "breezewidget.status", "phase3a-status")
        self._tip: StateToolTip | None = None
        self.addExample("InfoBadge variants", self._badgePreview())
        self.addExample("ProgressRing and IndeterminateProgressRing", self._ringPreview())
        self.addExample("StateToolTip for long running tasks", self._tooltipPreview())
        self.setStatus("Status & info bereit")
        self.finish()

    def _badgePreview(self) -> QWidget:
        return _row(
            InfoBadge.info("3"),
            InfoBadge.success("Ok"),
            InfoBadge.attention("!"),
            InfoBadge.warning("3"),
            InfoBadge.error("99+"),
            QLabel("Dot"),
            DotInfoBadge(),
            QLabel("Icon"),
            IconInfoBadge(BreezeIcon.CHECK, variant="success"),
            IconInfoBadge(BreezeIcon.WARNING, variant="warning"),
        )

    def _ringPreview(self) -> QWidget:
        ring = ProgressRing()
        ring.setRange(0, 100)
        ring.setTextVisible(True)
        ring.setValue(35)

        slider = ClickableSlider(Qt.Orientation.Horizontal)
        slider.setFixedWidth(240)
        slider.setRange(0, 100)
        slider.setValue(35)
        slider.valueChanged.connect(ring.setValue)
        slider.valueChanged.connect(lambda value: self.setStatus(f"ProgressRing: {value}%"))

        spinner = IndeterminateProgressRing()
        return _row(ring, slider, spinner, BodyLabel("Indeterminate spinner"))

    def _tooltipPreview(self) -> QWidget:
        state_button = PushButton("Lange Aufgabe starten", icon=BreezeIcon.DOWNLOAD)
        state_button.clicked.connect(self._runFakeJob)
        return _row(state_button)

    def _runFakeJob(self) -> None:
        if self._tip is not None and not self._tip.isDone():
            return
        tip = StateToolTip("Daten werden synchronisiert", "Bitte warten...", self.window())
        tip.closed.connect(self._clearTip)
        self._tip = tip
        tip.show()
        self.setStatus("StateToolTip gestartet")
        QTimer.singleShot(2000, self._completeFakeJob)

    def _clearTip(self) -> None:
        self._tip = None

    def _completeFakeJob(self) -> None:
        if self._tip is None:
            return
        self._tip.setState(True)
        self.setStatus("StateToolTip abgeschlossen")
