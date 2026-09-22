from __future__ import annotations

from pathlib import Path

import pytest
from PySide6.QtGui import QColor, QIcon

from breezewidget import BreezeIcon, IconRegistry, icon_from

ASSET_ROOT = Path(__file__).resolve().parents[1] / "icons"


@pytest.mark.parametrize("icon", list(BreezeIcon))
def test_every_breeze_icon_renders(qapp, icon):
    rendered = icon_from(icon)
    assert isinstance(rendered, QIcon)
    assert not rendered.isNull(), f"{icon.name} produced an empty QIcon"


@pytest.mark.parametrize("icon", list(BreezeIcon))
def test_breeze_icon_method(qapp, icon):
    assert isinstance(icon.icon(), QIcon)


def test_icon_from_accepts_color_str(qapp):
    rendered = icon_from(BreezeIcon.SETTINGS, color="#ff0000")
    assert isinstance(rendered, QIcon) and not rendered.isNull()


def test_icon_from_accepts_qcolor(qapp):
    rendered = icon_from(BreezeIcon.SETTINGS, color=QColor("#00ff00"))
    assert isinstance(rendered, QIcon) and not rendered.isNull()


def test_icon_from_passes_through_qicon(qapp):
    original = QIcon()
    assert icon_from(original) is original


def test_icon_from_unknown_string_returns_empty(qapp):
    rendered = icon_from("definitely-not-an-icon")
    assert isinstance(rendered, QIcon) and rendered.isNull()


def test_icon_from_none_returns_empty(qapp):
    rendered = icon_from(None)
    assert isinstance(rendered, QIcon) and rendered.isNull()


def test_icon_registry_get_caches_rendered_icons(qapp):
    first = IconRegistry.get(BreezeIcon.SETTINGS, color="#123456")
    second = IconRegistry.get("settings", color="#123456")

    assert first is second
    assert isinstance(first, QIcon) and not first.isNull()


def test_all_breeze_icons_are_backed_by_svg_assets():
    registry = IconRegistry.instance()

    for icon in BreezeIcon:
        path = registry._svg_paths.get(icon.value)
        assert path is not None and path.exists(), f"{icon.value} has no registered SVG asset"


def test_icon_registry_renders_colored_svg(qapp):
    IconRegistry.register_svg("test-home-svg", ASSET_ROOT / "outline" / "home-2.svg")

    rendered = IconRegistry.get("test-home-svg", color="#ff0000", size=32, stroke_width=3)

    assert isinstance(rendered, QIcon) and not rendered.isNull()
    assert _count_pixels(
        rendered,
        lambda color: color.alpha() > 32 and color.red() > 180 and color.green() < 90 and color.blue() < 90,
    ) > 0


def test_icon_registry_svg_cache_includes_stroke_width(qapp):
    IconRegistry.register_svg("test-home-svg-cache", ASSET_ROOT / "outline" / "home-2.svg")

    first = IconRegistry.get("test-home-svg-cache", color="#123456", size=24, stroke_width=1.5)
    second = IconRegistry.get("test-home-svg-cache", color="#123456", size=24, stroke_width=1.5)
    third = IconRegistry.get("test-home-svg-cache", color="#123456", size=24, stroke_width=4)

    assert first is second
    assert first is not third


def test_more_icon_renders_three_visible_dots(qapp):
    rendered = icon_from(BreezeIcon.MORE, color="#ffffff", size=16, stroke_width=2)
    image = rendered.pixmap(16, 16).toImage()
    columns = [
        x
        for x in range(image.width())
        if any(image.pixelColor(x, y).alpha() > 32 for y in range(image.height()))
    ]
    groups = 0
    previous = None
    for x in columns:
        if previous is None or x > previous + 1:
            groups += 1
        previous = x

    assert groups == 3
    assert min(columns) >= 4
    assert max(columns) <= 11


def test_svg_stroke_width_changes_rendered_weight(qapp):
    svg_path = ASSET_ROOT / "outline" / "home-2.svg"

    thin = IconRegistry.get(svg_path, color="#000000", size=32, stroke_width=1)
    thick = IconRegistry.get(svg_path, color="#000000", size=32, stroke_width=4)

    assert _count_opaque_pixels(thick) > _count_opaque_pixels(thin)


def _count_opaque_pixels(icon: QIcon) -> int:
    return _count_pixels(icon, lambda color: color.alpha() > 32)


def _count_pixels(icon: QIcon, predicate) -> int:
    image = icon.pixmap(32, 32).toImage()
    return sum(
        1
        for y in range(image.height())
        for x in range(image.width())
        if predicate(image.pixelColor(x, y))
    )
