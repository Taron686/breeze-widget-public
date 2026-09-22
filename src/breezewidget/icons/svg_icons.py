from __future__ import annotations

from pathlib import Path

from .registry import IconRegistry

_OUTLINE_ROOT = Path(__file__).resolve().parent / "outline"

BREEZE_ICON_SVGS = {
    "add": "plus.svg",
    "back": "arrow-left.svg",
    "calendar": "calendar.svg",
    "check": "check.svg",
    "close": "x.svg",
    "delete": "trash.svg",
    "document": "file-text.svg",
    "download": "download.svg",
    "edit": "edit.svg",
    "error": "circle-x.svg",
    "external-link": "external-link.svg",
    "folder": "folder.svg",
    "home": "home.svg",
    "info": "info-circle.svg",
    "menu": "menu-2.svg",
    "moon": "moon.svg",
    "more": "dots.svg",
    "next": "arrow-right.svg",
    "people": "users.svg",
    "save": "device-floppy.svg",
    "search": "search.svg",
    "settings": "settings.svg",
    "sun": "sun.svg",
    "warning": "alert-triangle.svg",
}

TITLE_BUTTON_SVGS = {
    "chevron-down": "chevron-down.svg",
    "chevron-right": "chevron-right.svg",
}


def register_default_svg_icons() -> None:
    for name, filename in BREEZE_ICON_SVGS.items():
        path = _OUTLINE_ROOT / filename
        if path.exists():
            IconRegistry.register_svg(name, path)

    for name, filename in TITLE_BUTTON_SVGS.items():
        path = _OUTLINE_ROOT / filename
        if path.exists():
            IconRegistry.register_svg(name, path)
