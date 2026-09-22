"""Smoke tests for Phase 4a: FlowLayout and ExpandLayout."""
from __future__ import annotations

import pytest

from PySide6.QtCore import QRect, QSize
from PySide6.QtWidgets import QLabel, QPushButton, QWidget

from breezewidget import ExpandLayout, FlowLayout


@pytest.fixture(autouse=True)
def isolate_layout_stylesheet(qapp):
    """Measure fixed native widgets independently of earlier themed tests."""
    previous = qapp.styleSheet()
    qapp.setStyleSheet("")
    try:
        yield
    finally:
        qapp.setStyleSheet(previous)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _buttons(parent: QWidget, n: int, w: int = 80, h: int = 32) -> list[QPushButton]:
    """Create *n* fixed-size buttons attached to *parent*."""
    btns = []
    for i in range(n):
        btn = QPushButton(str(i), parent)
        btn.setFixedSize(w, h)
        btns.append(btn)
    return btns


# ---------------------------------------------------------------------------
# FlowLayout
# ---------------------------------------------------------------------------

def test_flow_layout_constructs(qapp):
    layout = FlowLayout()
    assert layout.horizontalSpacing() == 8
    assert layout.verticalSpacing() == 8
    assert layout.count() == 0


def test_flow_layout_add_widget_increments_count(qapp):
    container = QWidget()
    layout = FlowLayout(container)
    btns = _buttons(container, 3)
    for btn in btns:
        layout.addWidget(btn)
    assert layout.count() == 3


def test_flow_layout_has_height_for_width(qapp):
    layout = FlowLayout()
    assert layout.hasHeightForWidth() is True


def test_flow_layout_height_for_width_single_row(qapp):
    # 3 buttons × 80px wide + 2 × 8px spacing = 256px — fits in 300px wide
    container = QWidget()
    layout = FlowLayout(container, h_spacing=8, v_spacing=8)
    btns = _buttons(container, 3, w=80, h=32)
    for btn in btns:
        layout.addWidget(btn)

    h_one_row = layout.heightForWidth(300)
    # Only one row: height should equal a single item height (32px)
    assert h_one_row == 32


def test_flow_layout_height_for_width_wraps_to_multiple_rows(qapp):
    # Width=100 fits only one 80px-wide button per row → 3 rows
    container = QWidget()
    layout = FlowLayout(container, h_spacing=8, v_spacing=8)
    btns = _buttons(container, 3, w=80, h=32)
    for btn in btns:
        layout.addWidget(btn)

    h_three_rows = layout.heightForWidth(100)
    # 3 rows × 32px + 2 gaps × 8px = 112px
    assert h_three_rows == 3 * 32 + 2 * 8


def test_flow_layout_set_geometry_places_widgets(qapp):
    container = QWidget()
    layout = FlowLayout(container)
    btns = _buttons(container, 2, w=80, h=32)
    for btn in btns:
        layout.addWidget(btn)

    layout.setGeometry(QRect(0, 0, 400, 200))

    for btn in btns:
        geom = layout.itemAt(btns.index(btn)).geometry()
        assert geom.width() == 80
        assert geom.height() == 32
        assert geom.x() >= 0
        assert geom.y() >= 0


def test_flow_layout_custom_spacing(qapp):
    layout = FlowLayout(h_spacing=4, v_spacing=12)
    assert layout.horizontalSpacing() == 4
    assert layout.verticalSpacing() == 12


def test_flow_layout_item_at_returns_item(qapp):
    container = QWidget()
    layout = FlowLayout(container)
    btn = QPushButton("x", container)
    layout.addWidget(btn)
    assert layout.itemAt(0) is not None
    assert layout.itemAt(1) is None


def test_flow_layout_take_at_decrements_count(qapp):
    container = QWidget()
    layout = FlowLayout(container)
    btns = _buttons(container, 3)
    for btn in btns:
        layout.addWidget(btn)

    assert layout.count() == 3
    item = layout.takeAt(0)
    assert item is not None
    assert layout.count() == 2


def test_flow_layout_empty_size_hint(qapp):
    layout = FlowLayout()
    hint = layout.sizeHint()
    assert hint == QSize(0, 0)


# ---------------------------------------------------------------------------
# ExpandLayout
# ---------------------------------------------------------------------------

def test_expand_layout_constructs(qapp):
    layout = ExpandLayout()
    assert layout.spacing() == 8
    margins = layout.contentsMargins()
    assert margins.left() == 0
    assert margins.top() == 0
    assert margins.right() == 0
    assert margins.bottom() == 0


def test_expand_layout_add_widget(qapp):
    container = QWidget()
    layout = ExpandLayout(container)
    layout.addWidget(QLabel("A", container))
    layout.addWidget(QLabel("B", container))
    assert layout.count() == 2
