from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import QByteArray, QRect, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QIcon, QIconEngine, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtXml import QDomDocument
from PySide6.QtWidgets import QApplication

SvgAttributes = tuple[tuple[str, str], ...]
DRAWABLE_SVG_TAGS = ("path", "circle", "ellipse", "line", "polyline", "polygon", "rect")


class SvgIconEngine(QIconEngine):
    def __init__(self, svg: str, default_size: QSize | None = None):
        super().__init__()
        self.svg = svg
        self.default_size = QSize(default_size or QSize(32, 32))

    def paint(self, painter: QPainter, rect: QRect, mode: QIcon.Mode, state: QIcon.State) -> None:
        del mode, state
        draw_svg_icon(self.svg, painter, QRectF(rect))

    def clone(self) -> QIconEngine:
        return SvgIconEngine(self.svg, self.default_size)

    def pixmap(self, size: QSize, mode: QIcon.Mode, state: QIcon.State) -> QPixmap:
        target_size = size if size.isValid() else self.default_size
        dpr = 1.0
        app = QApplication.instance()
        if app is not None:
            dpr = float(app.devicePixelRatio()) or 1.0
        physical = QSize(
            max(1, round(target_size.width() * dpr)),
            max(1, round(target_size.height() * dpr)),
        )
        pixmap = QPixmap(physical)
        pixmap.setDevicePixelRatio(dpr)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        self.paint(painter, QRect(0, 0, target_size.width(), target_size.height()), mode, state)
        painter.end()
        return pixmap


def draw_svg_icon(svg: str, painter: QPainter, rect: QRectF) -> None:
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    renderer.render(painter, rect)


def write_svg(
    icon_path: str | Path,
    indexes: range | list[int] | tuple[int, ...] | None = None,
    color: QColor | str | None = None,
    stroke_width: str | None = None,
    **attributes: Any,
) -> str:
    path = Path(icon_path)
    if path.suffix.lower() != ".svg" or not path.exists():
        return ""

    document = QDomDocument()
    if not document.setContent(QByteArray(path.read_bytes())):
        return ""

    root = document.documentElement()
    normalized = dict(normalized_svg_attributes(attributes))
    if color is not None and "fill" not in normalized and "stroke" not in normalized:
        normalized[_default_color_attribute(root)] = _color(color).name()
    if stroke_width is not None and "stroke-width" not in normalized:
        normalized["stroke-width"] = stroke_width
    if not normalized:
        return path.read_text(encoding="utf-8")

    _set_svg_attributes(root, normalized)

    for tag in DRAWABLE_SVG_TAGS:
        nodes = document.elementsByTagName(tag)
        if tag == "path" and indexes is not None:
            selected = indexes
        else:
            selected = range(nodes.length())

        for index in selected:
            if 0 <= int(index) < nodes.length():
                _set_svg_attributes(nodes.at(int(index)).toElement(), normalized)

    return document.toString()


def normalized_svg_attributes(attributes: dict[str, Any]) -> SvgAttributes:
    normalized: list[tuple[str, str]] = []
    for key, value in attributes.items():
        if value is None:
            continue
        attr = key.replace("_", "-")
        if isinstance(value, QColor):
            normalized.append((attr, value.name()))
        else:
            normalized.append((attr, str(value)))
    return tuple(sorted(normalized))


def _color(value: QColor | str | None) -> QColor:
    if value is None:
        try:
            from ..theme import isDarkTheme

            return QColor("#ffffff" if isDarkTheme() else "#000000")
        except Exception:
            return QColor("#202020")
    color = value if isinstance(value, QColor) else QColor(str(value))
    return QColor(color) if color.isValid() else QColor("#202020")


def _default_color_attribute(root) -> str:
    fill = root.attribute("fill").strip().lower()
    stroke = root.attribute("stroke").strip().lower()
    if fill == "none" and stroke:
        return "stroke"
    return "fill"


def _set_svg_attributes(element, attributes: dict[str, str]) -> None:
    for key, value in attributes.items():
        element.setAttribute(key, value)
