"""Windows (5) — MSBreezeWindow, SplitBreezeWindow, BreezeSplashScreen, Material."""
from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QLabel, QWidget

from breezewidget import (
    BreezeIcon,
    MSBreezeWindow,
    PushButton,
    SplitBreezeWindow,
)
from breezewidget.window import BreezeSplashScreen, MaterialEffect, apply_material

from ._gallery import GalleryPage, _row


class WindowsDemoPage(GalleryPage):
    """Phase 5 — MSBreezeWindow, SplitBreezeWindow, BreezeSplashScreen, Material."""

    def __init__(self):
        super().__init__("Windows & material", "breezewidget.window", "windows")

        ms_button = PushButton("Open MSBreezeWindow")
        ms_button.clicked.connect(self._openMSWindow)
        self.addExample("MSBreezeWindow — top-pivot navigation window", ms_button)

        split_button = PushButton("Open SplitBreezeWindow")
        split_button.clicked.connect(self._openSplitWindow)
        self.addExample("SplitBreezeWindow — drag-resizable sidebar", split_button)

        splash_button = PushButton("Show SplashScreen for 2 s")
        splash_button.clicked.connect(self._showSplash)
        self.addExample("BreezeSplashScreen — pre-window splash", splash_button)

        mica_row = _row(
            self._mkMaterialButton("Apply Mica", MaterialEffect.MICA),
            self._mkMaterialButton("Apply Acrylic", MaterialEffect.ACRYLIC),
            self._mkMaterialButton("Reset", MaterialEffect.NONE),
        )
        self.addExample(
            "apply_material — Windows 11 DWM backdrop (Mica / Acrylic)",
            mica_row,
        )

        self.finish()
        self._refs: list[QWidget] = []  # keep windows alive

    def _mkMaterialButton(self, text: str, effect: MaterialEffect) -> PushButton:
        btn = PushButton(text)
        btn.clicked.connect(lambda: self._applyMaterial(effect))
        return btn

    def _applyMaterial(self, effect: MaterialEffect) -> None:
        top = self.window()
        ok = apply_material(top, effect)
        self.setStatus(
            f"apply_material({effect.name}) → {'success' if ok else 'no-op (non-Win11)'}"
        )

    def _openMSWindow(self) -> None:
        win = MSBreezeWindow()
        win.setWindowTitle("MSBreezeWindow demo")
        for label, key in (("Home", "ms-home"), ("Library", "ms-lib"), ("Settings", "ms-set")):
            page = QLabel(f"Page: {label}")
            page.setAlignment(Qt.AlignmentFlag.AlignCenter)
            win.addSubInterface(page, label, routeKey=key)
        win.resize(720, 480)
        win.show()
        self._refs.append(win)

    def _openSplitWindow(self) -> None:
        win = SplitBreezeWindow()
        win.setWindowTitle("SplitBreezeWindow demo")
        for label, icon, key in (
            ("Home", BreezeIcon.HOME, "split-home"),
            ("Files", BreezeIcon.FOLDER, "split-files"),
            ("Settings", BreezeIcon.SETTINGS, "split-set"),
        ):
            page = QLabel(f"Page: {label}")
            page.setAlignment(Qt.AlignmentFlag.AlignCenter)
            win.addSubInterface(page, icon, label, routeKey=key)
        win.resize(900, 540)
        win.show()
        self._refs.append(win)

    def _showSplash(self) -> None:
        splash = BreezeSplashScreen(BreezeIcon.SETTINGS.icon(color="#11d9f3"), "BreezeWidget")
        splash.show()
        QTimer.singleShot(2000, splash.close)
        self._refs.append(splash)
