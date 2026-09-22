"""Animations (7e) — PropertyAnimation, BackgroundColorAnimation, DropShadowAnimation."""
from __future__ import annotations

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QHBoxLayout, QWidget

from breezewidget import (
    BackgroundColorAnimation,
    BodyLabel,
    DropShadowAnimation,
    PropertyAnimation,
    PushButton,
    getPalette,
)

from ._gallery import GalleryPage


class AnimationsDemoPage(GalleryPage):
    """Phase 7e — PropertyAnimation, BackgroundColorAnimation, DropShadowAnimation."""

    def __init__(self):
        super().__init__("Animations", "breezewidget.animation", "animations")

        # --- PropertyAnimation: animate windowOpacity on a panel ---------
        prop_panel = QFrame()
        prop_panel.setMinimumSize(220, 60)
        prop_panel.setStyleSheet(f"background: {getPalette().primary4}; border-radius: 8px;")
        prop_label = BodyLabel("Click 'Pulse' to animate opacity", prop_panel)
        prop_layout = QHBoxLayout(prop_panel)
        prop_layout.addWidget(prop_label)

        prop_row = QWidget()
        prop_h = QHBoxLayout(prop_row)
        prop_h.setContentsMargins(0, 0, 0, 0)
        prop_h.setSpacing(10)
        prop_btn = PushButton("Pulse")
        self._prop_anim = PropertyAnimation(prop_panel, b"windowOpacity").from_(1.0).to(0.3).withDuration(400)

        def _pulse():
            self._prop_anim.stop()
            self._prop_anim.setDirection(self._prop_anim.Direction.Forward)
            self._prop_anim.start()

        prop_btn.clicked.connect(_pulse)
        prop_h.addWidget(prop_btn)
        prop_h.addWidget(prop_panel, 1)
        self.addExample("PropertyAnimation — chainable QPropertyAnimation wrapper", prop_row, "breezewidget.animation.property")

        # --- BackgroundColorAnimation -----------------------------------
        bg_panel = QFrame()
        bg_panel.setMinimumSize(220, 60)
        self._bg_anim = BackgroundColorAnimation(bg_panel, getPalette().primary4)

        bg_row = QWidget()
        bg_h = QHBoxLayout(bg_row)
        bg_h.setContentsMargins(0, 0, 0, 0)
        bg_h.setSpacing(10)
        red_btn = PushButton("→ Red")
        green_btn = PushButton("→ Green")
        accent_btn = PushButton("→ Accent")
        red_btn.clicked.connect(lambda: self._bg_anim.animateTo("#e84545"))
        green_btn.clicked.connect(lambda: self._bg_anim.animateTo("#34c759"))
        accent_btn.clicked.connect(lambda: self._bg_anim.animateTo(getPalette().primary4))
        bg_h.addWidget(red_btn)
        bg_h.addWidget(green_btn)
        bg_h.addWidget(accent_btn)
        bg_h.addWidget(bg_panel, 1)
        self.addExample("BackgroundColorAnimation — animate widget background color", bg_row, "breezewidget.animation.color")

        # --- DropShadowAnimation ----------------------------------------
        sh_panel = QFrame()
        sh_panel.setMinimumSize(220, 60)
        sh_panel.setStyleSheet(f"background: {getPalette().surface2}; border-radius: 8px;")
        sh_label = BodyLabel("Hover-style shadow", sh_panel)
        sh_layout = QHBoxLayout(sh_panel)
        sh_layout.addWidget(sh_label)
        self._shadow = DropShadowAnimation(sh_panel, color=QColor(0, 0, 0, 140), offset=(0.0, 4.0), initial_blur=0.0)

        sh_row = QWidget()
        sh_h = QHBoxLayout(sh_row)
        sh_h.setContentsMargins(0, 0, 0, 0)
        sh_h.setSpacing(10)
        raise_btn = PushButton("Raise")
        lower_btn = PushButton("Lower")
        raise_btn.clicked.connect(lambda: self._shadow.animateBlur(28.0))
        lower_btn.clicked.connect(lambda: self._shadow.animateBlur(0.0))
        sh_h.addWidget(raise_btn)
        sh_h.addWidget(lower_btn)
        sh_h.addWidget(sh_panel, 1)
        self.addExample("DropShadowAnimation — animate blur radius of a drop shadow", sh_row, "breezewidget.animation.shadow")

        self.finish()
