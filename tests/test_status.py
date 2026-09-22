from __future__ import annotations

from PySide6.QtWidgets import QWidget

from breezewidget import (
    BreezeIcon,
    DotInfoBadge,
    IconInfoBadge,
    IndeterminateProgressRing,
    InfoBadge,
    ProgressRing,
    StateToolTip,
)
from breezewidget.constants import (
    BADGE_ATTENTION,
    BADGE_DANGER,
    BADGE_INFO,
    BADGE_SUCCESS,
    BADGE_WARNING,
    PROP_BADGE,
    PROP_STATE_TOOLTIP,
)


def test_info_badge_factories_set_variant_property(qapp):
    cases = [
        (InfoBadge.info("3"), BADGE_INFO),
        (InfoBadge.success("ok"), BADGE_SUCCESS),
        (InfoBadge.attention("!"), BADGE_ATTENTION),
        (InfoBadge.warning("!"), BADGE_WARNING),
        (InfoBadge.error("9"), BADGE_DANGER),
    ]
    for badge, variant in cases:
        assert badge.property(PROP_BADGE) == variant
        assert badge.text() in {"3", "ok", "!", "9"}


def test_info_badge_resizes_with_text(qapp):
    short = InfoBadge.info("1")
    wide = InfoBadge.info("999+")
    assert wide.sizeHint().width() >= short.sizeHint().width()


def test_info_badge_set_variant_updates_property(qapp):
    badge = InfoBadge.info("1")
    badge.setVariant(BADGE_DANGER)
    assert badge.property(PROP_BADGE) == BADGE_DANGER
    assert badge.variant == BADGE_DANGER


def test_dot_badge_is_fixed_size(qapp):
    dot = DotInfoBadge(diameter=12)
    assert dot.size().width() == 12
    assert dot.size().height() == 12
    assert dot.property(PROP_BADGE) == BADGE_ATTENTION


def test_icon_badge_renders_pixmap(qapp):
    badge = IconInfoBadge(BreezeIcon.CHECK, variant=BADGE_SUCCESS, size=14)
    assert badge.property(PROP_BADGE) == BADGE_SUCCESS
    assert not badge.pixmap().isNull()


def test_progress_ring_clamps_value(qapp):
    ring = ProgressRing()
    ring.setRange(0, 50)
    ring.setValue(120)
    assert ring.value() == 50
    ring.setValue(-5)
    assert ring.value() == 0


def test_progress_ring_progress_fraction(qapp):
    ring = ProgressRing()
    ring.setRange(0, 200)
    ring.setValue(50)
    assert abs(ring.progress() - 0.25) < 1e-6


def test_progress_ring_text_visibility_toggles(qapp):
    ring = ProgressRing()
    assert ring.isTextVisible() is False
    ring.setTextVisible(True)
    assert ring.isTextVisible() is True


def test_indeterminate_progress_ring_is_running(qapp):
    ring = IndeterminateProgressRing()
    ring.show()
    assert ring.isRunning() is True
    ring.stop()
    assert ring.isRunning() is False


def test_state_tooltip_done_swaps_visuals(qapp):
    parent = QWidget()
    parent.resize(400, 300)
    tip = StateToolTip("Working", "Please wait", parent)
    tip.setAutoCloseDelay(0)
    assert tip.property(PROP_STATE_TOOLTIP) is True
    assert tip.isDone() is False
    tip.setState(True)
    assert tip.isDone() is True


def test_state_tooltip_setters_update_labels(qapp):
    parent = QWidget()
    tip = StateToolTip("A", "B", parent)
    tip.setAutoCloseDelay(0)
    tip.setTitle("New title")
    tip.setContent("New content")
    assert tip._title.text() == "New title"
    assert tip._content.text() == "New content"


def test_state_tooltip_set_state_after_close_is_safe(qapp, qtbot):
    parent = QWidget()
    tip = StateToolTip("A", "B", parent)
    tip.setAutoCloseDelay(0)
    qtbot.addWidget(tip)
    tip.close()
    qtbot.wait(50)
    tip.setState(True)
    tip.setState(False)
