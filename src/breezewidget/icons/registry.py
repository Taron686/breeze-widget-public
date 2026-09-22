from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, ClassVar

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QApplication

from ._svg import SvgAttributes, SvgIconEngine, _color, normalized_svg_attributes, write_svg

PainterIcon = Callable[[QPainter, QColor], None]
IconCacheKey = tuple[str, str, int, str | None, SvgAttributes]
ResolvedIconOptions = tuple[QColor, int, str | None, SvgAttributes]


class IconRegistry:
    _instance: ClassVar["IconRegistry | None"] = None

    def __init__(self) -> None:
        self._painters: dict[str, PainterIcon] = {}
        self._svg_paths: dict[str, Path] = {}
        self._cache: dict[IconCacheKey, QIcon] = {}

    @classmethod
    def instance(cls) -> "IconRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def register_painter(cls, name: str) -> Callable[[PainterIcon], PainterIcon]:
        def decorator(painter: PainterIcon) -> PainterIcon:
            cls.instance()._painters[_normalize_name(name)] = painter
            cls.instance()._cache.clear()
            return painter

        return decorator

    @classmethod
    def register_svg(cls, name: str, path: str | Path) -> None:
        cls.instance()._svg_paths[_normalize_name(name)] = Path(path)
        cls.instance()._cache.clear()

    @classmethod
    def get(
        cls,
        value: Any,
        color: QColor | str | None = None,
        size: int = 32,
        stroke_width: float | int | str | None = None,
        **attributes: Any,
    ) -> QIcon:
        return cls.instance().icon(
            value,
            color=color,
            size=size,
            stroke_width=stroke_width,
            **attributes,
        )

    @classmethod
    def clearCache(cls) -> None:
        cls.instance()._cache.clear()

    def icon(
        self,
        value: Any,
        color: QColor | str | None = None,
        size: int = 32,
        stroke_width: float | int | str | None = None,
        **attributes: Any,
    ) -> QIcon:
        if value is None:
            return QIcon()
        if isinstance(value, QIcon):
            return value

        raw = value.value if hasattr(value, "value") else value
        if isinstance(raw, (str, Path)):
            icon_path = Path(raw)
            if icon_path.exists():
                return self._path_icon(icon_path, color, size, stroke_width, attributes)

        name = _normalize_name(raw)
        if not name:
            return QIcon()

        resolved_color, resolved_size, resolved_stroke_width, svg_attributes = _resolve_options(
            color,
            size,
            stroke_width,
            attributes,
        )
        return self._cached_icon(
            _cache_key(name, resolved_color, resolved_size, resolved_stroke_width, svg_attributes),
            lambda: self._render(
                name,
                resolved_color,
                resolved_size,
                resolved_stroke_width,
                svg_attributes,
            ),
        )

    def _render(
        self,
        name: str,
        color: QColor,
        size: int,
        stroke_width: str | None,
        attributes: SvgAttributes,
    ) -> QIcon:
        svg_path = self._svg_paths.get(name)
        if svg_path is not None and svg_path.exists():
            return self._render_svg(svg_path, color, size, stroke_width, attributes)

        painter = self._painters.get(name)
        if painter is not None:
            return self._render_painter(painter, color, size, stroke_width)

        return QIcon()

    def _path_icon(
        self,
        icon_path: Path,
        color: QColor | str | None,
        size: int,
        stroke_width: float | int | str | None,
        attributes: dict[str, Any],
    ) -> QIcon:
        if icon_path.suffix.lower() != ".svg":
            return QIcon(str(icon_path))

        resolved_color, resolved_size, resolved_stroke_width, svg_attributes = _resolve_options(
            color,
            size,
            stroke_width,
            attributes,
        )
        return self._cached_icon(
            _cache_key(
                f"path:{icon_path.resolve()}",
                resolved_color,
                resolved_size,
                resolved_stroke_width,
                svg_attributes,
            ),
            lambda: self._render_svg(
                icon_path,
                resolved_color,
                resolved_size,
                resolved_stroke_width,
                svg_attributes,
            ),
        )

    def _cached_icon(self, key: IconCacheKey, render: Callable[[], QIcon]) -> QIcon:
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        icon = render()
        if not icon.isNull():
            self._cache[key] = icon
        return icon

    def _render_painter(
        self,
        icon_painter: PainterIcon,
        color: QColor,
        size: int,
        stroke_width: str | None,
    ) -> QIcon:
        if QApplication.instance() is None:
            return QIcon()

        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        if size != 32:
            scale = size / 32
            painter.scale(scale, scale)
        painter.setPen(
            QPen(
                color,
                float(stroke_width) if stroke_width is not None else 2.4,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin,
            )
        )
        painter.setBrush(Qt.BrushStyle.NoBrush)
        icon_painter(painter, color)
        painter.end()
        return QIcon(pixmap)

    def _render_svg(
        self,
        svg_path: Path,
        color: QColor,
        size: int,
        stroke_width: str | None,
        attributes: SvgAttributes,
    ) -> QIcon:
        if QApplication.instance() is None:
            return QIcon()

        svg = write_svg(
            svg_path,
            color=color,
            stroke_width=stroke_width,
            **dict(attributes),
        )
        if not svg:
            return QIcon()
        return QIcon(SvgIconEngine(svg, QSize(size, size)))


def _normalize_name(value: Any) -> str:
    return str(value).strip().lower()


def _resolve_options(
    color: QColor | str | None,
    size: int,
    stroke_width: float | int | str | None,
    attributes: dict[str, Any],
) -> ResolvedIconOptions:
    return (
        _color(color),
        max(1, int(size)),
        _stroke_width(stroke_width),
        normalized_svg_attributes(attributes),
    )


def _cache_key(
    name: str,
    color: QColor,
    size: int,
    stroke_width: str | None,
    attributes: SvgAttributes,
) -> IconCacheKey:
    return (name, color.name(), size, stroke_width, attributes)


def _stroke_width(value: float | int | str | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, (float, int)):
        return f"{float(value):g}"
    return str(value)


