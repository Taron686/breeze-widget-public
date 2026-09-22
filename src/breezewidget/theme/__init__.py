"""Theme, palette and stylesheet subsystem."""
from __future__ import annotations

from .listener import OSThemeListener
from .palette import BreezePalette
from .provider_base import StyleSheetBase
from .theme import (
    StyleSheetManager,
    build_stylesheet,
    getPalette,
    setCustomStyleSheet,
    Theme,
    ThemeManager,
    applyTheme,
    isDarkTheme,
    setTheme,
    setThemeColor,
)

__all__ = [
    "Theme",
    "ThemeManager",
    "BreezePalette",
    "setTheme",
    "setThemeColor",
    "applyTheme",
    "getPalette",
    "isDarkTheme",
    "StyleSheetBase",
    "StyleSheetManager",
    "build_stylesheet",
    "setCustomStyleSheet",
    "OSThemeListener",
]
