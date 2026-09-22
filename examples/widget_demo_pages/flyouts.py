"""Flyouts — TeachingTip, generic Flyout, InfoBar."""
from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout, QWidget

from breezewidget import (
    BodyLabel,
    BreezeIcon,
    Flyout,
    FlyoutPlacement,
    InfoBar,
    PrimaryPushButton,
    PushButton,
    StrongBodyLabel,
    TeachingTip,
)

from ._gallery import GalleryPage, _row


class DialogsFlyoutsDemoPage(GalleryPage):
    def __init__(self):
        super().__init__("Dialogs & flyouts", "breezewidget.flyout", "dialogs-flyouts")
        self.addExample("A TeachingTip attached to a button", self._teachingTipPreview())
        self.addExample("A generic Flyout with custom content", self._flyoutPreview())
        self.addExample("A top-right InfoBar notification", self._infoBarPreview())
        self.setStatus("Dialogs & flyouts bereit")
        self.finish()

    def _teachingTipPreview(self) -> QWidget:
        button = PushButton("TeachingTip zeigen", icon=BreezeIcon.INFO)
        button.clicked.connect(lambda: self._showTeachingTip(button))
        return _row(button)

    def _flyoutPreview(self) -> QWidget:
        button = PushButton("Flyout zeigen", icon=BreezeIcon.MORE)
        button.clicked.connect(lambda: self._showFlyout(button))
        return _row(button)

    def _infoBarPreview(self) -> QWidget:
        button = PrimaryPushButton("InfoBar anzeigen", icon=BreezeIcon.INFO)
        button.clicked.connect(lambda: InfoBar.success("BreezeWidget", "Benachrichtigung aus der Demo", self.window()))
        return _row(button)

    def _showTeachingTip(self, target: QWidget) -> None:
        tip = TeachingTip(
            "TeachingTip",
            "Diese Hinweisblase ist am ausloesenden Button verankert und kann Aktionen enthalten.",
            target=target,
            parent=self.window(),
            icon=BreezeIcon.INFO,
            placement=FlyoutPlacement.BOTTOM,
        )
        tip.addButton("Verstanden")
        tip.exec()
        self.setStatus("TeachingTip angezeigt")

    def _showFlyout(self, target: QWidget) -> None:
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(4)
        body_layout.addWidget(StrongBodyLabel("Flyout"))
        body_layout.addWidget(BodyLabel("Beliebiger Inhalt: Text, Buttons oder eigene Widgets. dddddddddddd   ddddd  ddddddddd"))
        flyout = Flyout(content=body, target=target, parent=self.window(), placement=FlyoutPlacement.TOP)
        flyout.exec()
        self.setStatus("Flyout angezeigt")
