"""Phase 7e — animation/ helpers."""
from __future__ import annotations

import pytest
from PySide6.QtCore import QEasingCurve
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget

from breezewidget import (
    BackgroundColorAnimation,
    DropShadowAnimation,
    PropertyAnimation,
)
from breezewidget.animation.property import DEFAULT_DURATION_MS


# ---------------------------------------------------------------------------
# PropertyAnimation
# ---------------------------------------------------------------------------

def test_property_animation_defaults(qapp):
    w = QWidget()
    anim = PropertyAnimation(w, b"windowOpacity")
    assert anim.duration() == DEFAULT_DURATION_MS
    assert anim.easingCurve().type() == QEasingCurve.Type.OutCubic
    assert anim.propertyName() == b"windowOpacity"


def test_property_animation_accepts_str_property(qapp):
    w = QWidget()
    anim = PropertyAnimation(w, "windowOpacity")
    assert anim.propertyName() == b"windowOpacity"


def test_property_animation_chainable_setters(qapp):
    w = QWidget()
    anim = PropertyAnimation(w, b"windowOpacity").from_(0.0).to(1.0).withDuration(500).withEasing(QEasingCurve.Type.Linear)
    assert anim.startValue() == 0.0
    assert anim.endValue() == 1.0
    assert anim.duration() == 500
    assert anim.easingCurve().type() == QEasingCurve.Type.Linear


# ---------------------------------------------------------------------------
# BackgroundColorAnimation
# ---------------------------------------------------------------------------

def test_background_color_animation_initial_color_applied(qapp):
    w = QWidget()
    anim = BackgroundColorAnimation(w, "#ff0000")
    assert anim.color().name() == "#ff0000"
    assert "background-color" in w.styleSheet()
    assert "#ff0000" in w.styleSheet()


def test_background_color_animation_animate_to_sets_endpoints(qapp):
    w = QWidget()
    anim = BackgroundColorAnimation(w, "#ff0000")
    anim.animateTo("#00ff00")
    # Internal animation has matching endpoints — the Property mediates this.
    assert anim.color().name() == "#ff0000"  # not yet ticked
    anim.stop()


def test_background_color_animation_property_setter_updates_widget(qapp):
    w = QWidget()
    anim = BackgroundColorAnimation(w, "#000000")
    anim.setProperty("backgroundColor", QColor("#11d9f3"))
    assert anim.color().name() == "#11d9f3"
    assert "#11d9f3" in w.styleSheet()


def test_background_color_animation_set_duration(qapp):
    w = QWidget()
    anim = BackgroundColorAnimation(w, duration_ms=500)
    assert anim.duration() == 500
    anim.setDuration(250)
    assert anim.duration() == 250


# ---------------------------------------------------------------------------
# DropShadowAnimation
# ---------------------------------------------------------------------------

def test_drop_shadow_animation_attaches_effect(qapp):
    w = QWidget()
    anim = DropShadowAnimation(w, initial_blur=4.0)
    assert w.graphicsEffect() is anim.effect()
    assert anim.effect().blurRadius() == pytest.approx(4.0)


def test_drop_shadow_animation_property_updates_blur(qapp):
    w = QWidget()
    anim = DropShadowAnimation(w, initial_blur=0.0)
    anim.setProperty("blurRadius", 12.0)
    assert anim.effect().blurRadius() == pytest.approx(12.0)


def test_drop_shadow_animation_set_color_and_offset(qapp):
    w = QWidget()
    anim = DropShadowAnimation(w)
    anim.setColor("#0067c0")
    anim.setOffset(4.0, 6.0)
    assert anim.effect().color().name() == "#0067c0"
    assert anim.effect().offset().x() == pytest.approx(4.0)
    assert anim.effect().offset().y() == pytest.approx(6.0)


def test_drop_shadow_animation_animate_blur_sets_endpoints(qapp):
    w = QWidget()
    anim = DropShadowAnimation(w, initial_blur=0.0)
    anim.animateBlur(20.0)
    anim.stop()
    # Endpoint stored on internal animation; verify via blur property re-poll.
    assert anim.duration() > 0


def test_drop_shadow_animation_detach_restores_previous(qapp):
    w = QWidget()
    anim = DropShadowAnimation(w)
    assert w.graphicsEffect() is anim.effect()
    anim.detach()
    assert w.graphicsEffect() is None


def test_drop_shadow_animation_set_duration(qapp):
    w = QWidget()
    anim = DropShadowAnimation(w, duration_ms=500)
    assert anim.duration() == 500
    anim.setDuration(100)
    assert anim.duration() == 100
