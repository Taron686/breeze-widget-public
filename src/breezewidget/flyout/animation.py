"""Slide / fade helpers used by Flyout and TeachingTip."""
from __future__ import annotations

from enum import Enum

from PySide6.QtCore import (
    QEasingCurve,
    QParallelAnimationGroup,
    QPoint,
    QPropertyAnimation,
)
from PySide6.QtWidgets import QGraphicsOpacityEffect, QWidget


class FlyoutAnimationType(str, Enum):
    """Visual reveal style for a flyout-style overlay."""

    NONE = "none"
    FADE_IN = "fade"
    SLIDE_UP = "slide_up"
    SLIDE_DOWN = "slide_down"
    SLIDE_LEFT = "slide_left"
    SLIDE_RIGHT = "slide_right"


def _slide_offset(animation_type: FlyoutAnimationType, distance: int) -> QPoint:
    return {
        FlyoutAnimationType.SLIDE_DOWN: QPoint(0, -distance),
        FlyoutAnimationType.SLIDE_UP: QPoint(0, distance),
        FlyoutAnimationType.SLIDE_LEFT: QPoint(distance, 0),
        FlyoutAnimationType.SLIDE_RIGHT: QPoint(-distance, 0),
    }.get(animation_type, QPoint(0, 0))


def make_show_animation(
    widget: QWidget,
    animation_type: FlyoutAnimationType = FlyoutAnimationType.SLIDE_DOWN,
    duration: int = 200,
    distance: int = 12,
) -> QParallelAnimationGroup | None:
    """Return a parallel animation that fades + slides ``widget`` into view.

    The widget must already be positioned at its final geometry. Caller
    must ``start()`` the returned group; it is parented to ``widget``
    so it cleans up automatically. Returns ``None`` for
    :class:`FlyoutAnimationType.NONE`.
    """
    if animation_type == FlyoutAnimationType.NONE:
        return None

    group = QParallelAnimationGroup(widget)

    effect = widget.graphicsEffect()
    if not isinstance(effect, QGraphicsOpacityEffect):
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
    effect.setOpacity(0.0)

    fade = QPropertyAnimation(effect, b"opacity", group)
    fade.setDuration(duration)
    fade.setStartValue(0.0)
    fade.setEndValue(1.0)
    fade.setEasingCurve(QEasingCurve.Type.OutCubic)
    group.addAnimation(fade)

    if animation_type != FlyoutAnimationType.FADE_IN:
        end_pos = widget.pos()
        offset = _slide_offset(animation_type, distance)
        widget.move(end_pos + offset)

        slide = QPropertyAnimation(widget, b"pos", group)
        slide.setDuration(duration)
        slide.setStartValue(end_pos + offset)
        slide.setEndValue(end_pos)
        slide.setEasingCurve(QEasingCurve.Type.OutCubic)
        group.addAnimation(slide)

    return group
