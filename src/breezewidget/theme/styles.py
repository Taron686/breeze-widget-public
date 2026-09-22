from __future__ import annotations

from typing import Any

from .palette import BreezePalette
from .provider_base import StyleSheetBase
from .providers import (
    BadgeStyleSheet,
    BaseStyleSheet,
    BreadcrumbStyleSheet,
    ButtonStyleSheet,
    CardStyleSheet,
    ChoiceStyleSheet,
    CommandBarStyleSheet,
    DialogStyleSheet,
    FlipViewStyleSheet,
    FlyoutStyleSheet,
    InfoBarStyleSheet,
    InputStyleSheet,
    ItemViewStyleSheet,
    LabelStyleSheet,
    NavigationStyleSheet,
    PickerStyleSheet,
    PivotStyleSheet,
    PlayBarStyleSheet,
    ProgressStyleSheet,
    RoundMenuStyleSheet,
    ScrollStyleSheet,
    SegmentedStyleSheet,
    SliderStyleSheet,
    SplashScreenStyleSheet,
    StateToolTipStyleSheet,
    TabBarStyleSheet,
    TeachingTipStyleSheet,
    ThemePillStyleSheet,
    TitleBarStyleSheet,
    WindowStyleSheet,
)


class _StyleSheetRegistry:
    """Render registered providers with an explicitly supplied palette."""

    def __init__(self) -> None:
        self._providers: list[tuple[Any, StyleSheetBase]] = []
        self._register_defaults()

    def _register(self, widget_type: Any, provider: StyleSheetBase) -> None:
        if not isinstance(provider, StyleSheetBase):
            raise TypeError("provider must be a StyleSheetBase instance")
        self._providers = [
            (owner, existing)
            for owner, existing in self._providers
            if owner != widget_type
        ]
        self._providers.append((widget_type, provider))

    def _build(self, palette: BreezePalette) -> str:
        fragments = [provider.build(palette).strip() for _, provider in self._providers]
        return "\n\n".join(fragment for fragment in fragments if fragment)

    def _register_defaults(self) -> None:
        for owner, provider in (
            ("base", BaseStyleSheet()),
            ("window", WindowStyleSheet()),
            ("button", ButtonStyleSheet()),
            ("input", InputStyleSheet()),
            ("choice", ChoiceStyleSheet()),
            ("slider", SliderStyleSheet()),
            ("progress", ProgressStyleSheet()),
            ("card", CardStyleSheet()),
            ("info_bar", InfoBarStyleSheet()),
            ("badge", BadgeStyleSheet()),
            ("state_tooltip", StateToolTipStyleSheet()),
            ("flyout", FlyoutStyleSheet()),
            ("teaching_tip", TeachingTipStyleSheet()),
            ("navigation", NavigationStyleSheet()),
            ("pivot", PivotStyleSheet()),
            ("segmented", SegmentedStyleSheet()),
            ("breadcrumb", BreadcrumbStyleSheet()),
            ("tab_bar", TabBarStyleSheet()),
            ("title_bar", TitleBarStyleSheet()),
            ("theme_pill", ThemePillStyleSheet()),
            ("label", LabelStyleSheet()),
            ("scroll", ScrollStyleSheet()),
            ("round_menu", RoundMenuStyleSheet()),
            ("command_bar", CommandBarStyleSheet()),
            ("dialog", DialogStyleSheet()),
            ("picker", PickerStyleSheet()),
            ("splash_screen", SplashScreenStyleSheet()),
            ("item_view", ItemViewStyleSheet()),
            ("flip_view", FlipViewStyleSheet()),
            ("play_bar", PlayBarStyleSheet()),
        ):
            self._register(owner, provider)
