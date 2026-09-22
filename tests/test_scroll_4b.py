"""Smoke tests for Phase 4b: SmoothScrollArea and PipsPager."""
from __future__ import annotations

from PySide6.QtCore import QPropertyAnimation
from PySide6.QtWidgets import QLabel

from breezewidget import PipsPager, SmoothScrollArea


# ---------------------------------------------------------------------------
# SmoothScrollArea
# ---------------------------------------------------------------------------

def test_smooth_scroll_area_constructs(qapp):
    area = SmoothScrollArea()
    assert area.smoothing() is True


def test_smooth_scroll_area_disable_smoothing(qapp):
    area = SmoothScrollArea()
    area.setSmoothing(False)
    assert area.smoothing() is False


def test_smooth_scroll_area_has_animations(qapp):
    area = SmoothScrollArea()
    assert isinstance(area._v_anim, QPropertyAnimation)
    assert isinstance(area._h_anim, QPropertyAnimation)


def test_smooth_scroll_area_v_anim_targets_vertical_scrollbar(qapp):
    area = SmoothScrollArea()
    assert area._v_anim.targetObject() is area.verticalScrollBar()


def test_smooth_scroll_area_h_anim_targets_horizontal_scrollbar(qapp):
    area = SmoothScrollArea()
    assert area._h_anim.targetObject() is area.horizontalScrollBar()


def test_smooth_scroll_area_accepts_widget(qapp):
    area = SmoothScrollArea()
    label = QLabel("content")
    area.setWidget(label)
    area.setWidgetResizable(True)
    assert area.widget() is label


# ---------------------------------------------------------------------------
# PipsPager
# ---------------------------------------------------------------------------

def test_pips_pager_constructs(qapp):
    pager = PipsPager()
    assert pager.pageCount() == 0
    assert pager.currentIndex() == 0


def test_pips_pager_set_page_count(qapp):
    pager = PipsPager()
    pager.setPageCount(5)
    assert pager.pageCount() == 5


def test_pips_pager_set_current_emits_signal(qapp, qtbot):
    pager = PipsPager()
    pager.setPageCount(3)
    with qtbot.waitSignal(pager.currentChanged, timeout=500) as sig:
        pager.setCurrentIndex(2)
    assert sig.args == [2]
    assert pager.currentIndex() == 2


def test_pips_pager_same_index_no_signal(qapp):
    pager = PipsPager()
    pager.setPageCount(3)
    pager.setCurrentIndex(1)
    signals: list[int] = []
    pager.currentChanged.connect(signals.append)
    pager.setCurrentIndex(1)
    assert signals == []


def test_pips_pager_size_hint_grows_with_count(qapp):
    pager = PipsPager()
    pager.setPageCount(3)
    w3 = pager.sizeHint().width()
    pager.setPageCount(5)
    w5 = pager.sizeHint().width()
    assert w5 > w3


def test_pips_pager_clamps_current_on_shrink(qapp):
    pager = PipsPager()
    pager.setPageCount(5)
    pager.setCurrentIndex(4)
    pager.setPageCount(3)
    assert pager.currentIndex() <= 2


def test_pips_pager_out_of_range_index_ignored(qapp):
    pager = PipsPager()
    pager.setPageCount(3)
    pager.setCurrentIndex(99)
    assert pager.currentIndex() == 0


def test_pips_pager_paints_without_error(qapp, qtbot):
    pager = PipsPager()
    pager.setPageCount(4)
    pager.setCurrentIndex(1)
    pager.resize(200, 20)
    pager.show()
    qtbot.waitExposed(pager)
    pager.update()
