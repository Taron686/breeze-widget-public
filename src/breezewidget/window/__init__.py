"""Window subsystem.

Keeps the import path ``breezewidget.window`` stable.
"""
from __future__ import annotations

from .breeze_window import BreezeWindow
from .material import MaterialEffect, apply_material
from .ms_breeze_window import MSBreezeWindow
from .splash_screen import BreezeSplashScreen
from .split_breeze_window import SplitBreezeWindow
from .title_bar import BreezeTitleBar

__all__ = [
    "BreezeWindow",
    "BreezeTitleBar",
    "MSBreezeWindow",
    "SplitBreezeWindow",
    "BreezeSplashScreen",
    "MaterialEffect",
    "apply_material",
]
