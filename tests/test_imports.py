from __future__ import annotations

import importlib

import breezewidget

EXPECTED_SYMBOLS = {
    "BreezeRouter",
    "ExceptionHandler",
    "Translator",
    "PropertyAnimation", "BackgroundColorAnimation", "DropShadowAnimation",
    "BreezeConfig", "ConfigItem", "RangeConfigItem", "OptionsConfigItem", "ColorConfigItem",
    "ConfigValidator", "RangeValidator", "OptionsValidator", "BoolValidator",
    "FolderValidator", "FolderListValidator",
    "ConfigSerializer", "ColorSerializer", "EnumSerializer",
    "ExpandLayout",
    "FlowLayout",
    "PipsPager",
    "SmoothScrollArea",
    "Theme", "ThemeManager", "OSThemeListener", "BreezePalette",
    "StyleSheetBase", "StyleSheetManager",
    "setTheme", "setThemeColor", "applyTheme", "getPalette", "isDarkTheme",
    "setCustomStyleSheet",
    "BreezeIcon", "IconRegistry", "icon_from",
    "PushButton", "PrimaryPushButton", "TransparentPushButton",
    "ToolButton", "PrimaryToolButton", "TransparentToolButton", "ToggleButton", "HyperlinkButton",
    "DropDownPushButton", "SplitPushButton", "PillPushButton",
    "IconWidget",
    "BreezeThemeSwitch",
    "LineEdit", "SearchLineEdit", "PasswordLineEdit",
    "TextEdit", "PlainTextEdit",
    "ComboBox", "EditableComboBox",
    "SpinBox", "DoubleSpinBox", "DateEdit", "TimeEdit", "DateTimeEdit",
    "Slider", "ClickableSlider",
    "ProgressBar", "IndeterminateProgressBar",
    "CheckBox", "RadioButton", "SwitchButton",
    "CardWidget", "SimpleCardWidget", "ElevatedCardWidget",
    "HeaderCardWidget",
    "SettingCard", "SettingCardGroup",
    "SwitchSettingCard", "ComboBoxSettingCard", "RangeSettingCard",
    "PushSettingCard", "HyperlinkCard", "ExpandSettingCard",
    "OptionsSettingCard", "CustomColorSettingCard",
    "BodyLabel", "CaptionLabel", "StrongBodyLabel", "TitleLabel", "SubtitleLabel",
    "InfoBar", "InfoBarPosition",
    "InfoBadge", "DotInfoBadge", "IconInfoBadge",
    "ProgressRing", "IndeterminateProgressRing",
    "StateToolTip",
    "Flyout", "FlyoutPlacement", "FlyoutAnimationType",
    "TeachingTip",
    "MessageBox",
    "RoundMenu", "CheckableMenu", "CommandBar",
    "CalendarPicker", "FastCalendarPicker", "DatePicker", "TimePicker",
    "NavigationInterface", "NavigationItemPosition",
    "Pivot", "PivotItem",
    "SegmentedWidget",
    "BreadcrumbBar", "BreadcrumbItem",
    "TabBar", "TabItem",
    "BreezeWindow", "BreezeTitleBar", "MSBreezeWindow", "SplitBreezeWindow",
    "ListView", "TableView", "TableWidget", "TableItemDelegate", "TreeView",
    "RichTextSegment", "RICH_TEXT_ROLE", "RichTextEdit", "RichTextTableItemDelegate",
    "RichTextBlock", "RICH_TEXT_BLOCKS_ROLE",
    "FlipView", "CycleListWidget", "Avatar",
    "MediaPlayer", "PlayBar", "VideoWidget",
}

EXPECTED_SUBMODULE_SYMBOLS = {
    "breezewidget.rich_text": {
        "RichTextSegment", "RICH_TEXT_ROLE", "RichTextEdit", "RichTextTableItemDelegate",
    "RichTextBlock", "RICH_TEXT_BLOCKS_ROLE",
    },
    "breezewidget.window": {
        "BreezeWindow",
        "BreezeTitleBar",
        "MSBreezeWindow",
        "SplitBreezeWindow",
        "BreezeSplashScreen",
        "MaterialEffect",
        "apply_material",
    },
    "breezewidget.theme": {
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
    },
    "breezewidget.icons": {
        "BreezeIcon",
        "icon_from",
        "IconRegistry",
    },
    "breezewidget.navigation": {
        "NavigationInterface",
        "NavigationItemPosition",
        "Pivot",
        "PivotItem",
        "SegmentedWidget",
        "BreadcrumbBar",
        "BreadcrumbItem",
        "TabBar",
        "TabItem",
    },
}


def test_all_contains_expected_symbols():
    declared = set(breezewidget.__all__)
    assert declared == EXPECTED_SYMBOLS


def test_all_symbol_count_matches_contract():
    assert len(breezewidget.__all__) == 140


def test_all_symbols_are_importable():
    for name in breezewidget.__all__:
        assert hasattr(breezewidget, name), f"{name} not importable from breezewidget"


def test_all_symbols_are_unique():
    assert len(breezewidget.__all__) == len(set(breezewidget.__all__))


def test_curated_submodule_exports_match_contract():
    for module_name, expected in EXPECTED_SUBMODULE_SYMBOLS.items():
        module = importlib.import_module(module_name)
        assert set(module.__all__) == expected


def test_curated_submodule_exports_are_importable_and_public():
    for module_name in EXPECTED_SUBMODULE_SYMBOLS:
        module = importlib.import_module(module_name)
        for name in module.__all__:
            assert not name.startswith("_")
            assert hasattr(module, name), f"{module_name}.{name} not importable"
        assert len(module.__all__) == len(set(module.__all__))
