"""Navigation subsystem.

Keeps the import path ``breezewidget.navigation`` stable.
"""
from __future__ import annotations

from .breadcrumb import BreadcrumbBar, BreadcrumbItem
from .interface import NavigationInterface, NavigationItemPosition
from .pivot import Pivot, PivotItem
from .segmented import SegmentedWidget
from .tab_bar import TabBar, TabItem

__all__ = [
    "NavigationInterface",
    "NavigationItemPosition",
    "Pivot",
    "PivotItem",
    "SegmentedWidget",
    "BreadcrumbBar",
    "BreadcrumbItem",
    "TabBar",
    "TabItem",
]
