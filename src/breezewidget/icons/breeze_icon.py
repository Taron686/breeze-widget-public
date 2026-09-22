from __future__ import annotations

from enum import Enum
from typing import Any

from PySide6.QtGui import QColor, QIcon

from .registry import IconRegistry
from .svg_icons import register_default_svg_icons

register_default_svg_icons()


class BreezeIcon(str, Enum):
    ADD = "add"
    BACK = "back"
    CALENDAR = "calendar"
    CHECK = "check"
    CLOSE = "close"
    DELETE = "delete"
    DOCUMENT = "document"
    DOWNLOAD = "download"
    EDIT = "edit"
    ERROR = "error"
    EXTERNAL_LINK = "external-link"
    FOLDER = "folder"
    HOME = "home"
    INFO = "info"
    MENU = "menu"
    MOON = "moon"
    MORE = "more"
    NEXT = "next"
    PEOPLE = "people"
    SAVE = "save"
    SEARCH = "search"
    SETTINGS = "settings"
    SUN = "sun"
    WARNING = "warning"

    def icon(
        self,
        color: QColor | str | None = None,
        size: int = 32,
        stroke_width: float | int | str | None = None,
        **attributes: Any,
    ) -> QIcon:
        return icon_from(self, color=color, size=size, stroke_width=stroke_width, **attributes)


def icon_from(
    value: Any,
    color: QColor | str | None = None,
    size: int = 32,
    stroke_width: float | int | str | None = None,
    **attributes: Any,
) -> QIcon:
    return IconRegistry.get(value, color=color, size=size, stroke_width=stroke_width, **attributes)
