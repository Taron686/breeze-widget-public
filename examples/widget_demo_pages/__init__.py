"""Page modules for the BreezeWidget gallery demo.

Each module hosts a single :class:`GalleryPage` subclass corresponding
to one entry in the demo window's left navigation panel.
"""
from __future__ import annotations

from ._gallery import DemoExample, GalleryPage, PAGE_MARGIN
from .animations import AnimationsDemoPage
from .basic_input import WidgetDemoPage
from .calender_view import CalenderViewDemoPage
from .cards import CardsDemoPage
from .data_views import ViewsDemoPage
from .date_time import DateTimeDemoPage
from .dialogs import DialogsDemoPage
from .flyouts import DialogsFlyoutsDemoPage
from .infrastructure import InfrastructureDemoPage
from .media import MediaDemoPage
from .menus import MenusDemoPage
from .navigation import NavigationDemoPage
from .pickers import PickersDemoPage
from .status import StatusDemoPage
from .windows import WindowsDemoPage

__all__ = [
    "AnimationsDemoPage",
    "CalenderViewDemoPage",
    "CardsDemoPage",
    "DateTimeDemoPage",
    "DemoExample",
    "DialogsDemoPage",
    "DialogsFlyoutsDemoPage",
    "GalleryPage",
    "InfrastructureDemoPage",
    "MediaDemoPage",
    "MenusDemoPage",
    "NavigationDemoPage",
    "PAGE_MARGIN",
    "PickersDemoPage",
    "StatusDemoPage",
    "ViewsDemoPage",
    "WidgetDemoPage",
    "WindowsDemoPage",
]
