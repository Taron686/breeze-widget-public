"""Public API constants for the breezewidget toolkit.

The names and string values defined here are part of the public API contract.
They identify the Qt dynamic properties that downstream code may set on its
own widgets to hook into the Breeze stylesheet, plus the small set of allowed
values for those properties.

Renaming or removing an entry here is a breaking change for any application
that styles custom widgets through these properties or supplies its own QSS
overrides keyed on them.
"""
from __future__ import annotations

from typing import Final

# --- Qt dynamic property names -------------------------------------------------

PROP_ROLE: Final = "breezeRole"
PROP_LABEL: Final = "breezeLabel"
PROP_CARD: Final = "breezeCard"
PROP_INFO_BAR: Final = "breezeInfoBar"
PROP_THEME_PILL: Final = "breezeThemePill"
PROP_PILL: Final = "breezePill"
PROP_SWITCH: Final = "breezeSwitch"

PROP_NAVIGATION: Final = "breezeNavigation"
PROP_NAVIGATION_COMPACT: Final = "breezeNavigationCompact"
PROP_NAVIGATION_ITEM: Final = "breezeNavigationItem"
PROP_NAVIGATION_ITEM_COMPACT: Final = "breezeNavigationItemCompact"
PROP_NAVIGATION_INDICATOR: Final = "breezeNavigationIndicator"

PROP_WINDOW_CONTENT_HOST: Final = "breezeWindowContentHost"
PROP_WINDOW_CONTENT: Final = "breezeWindowContent"

PROP_TITLE_BAR: Final = "breezeTitleBar"
PROP_TITLE_LABEL: Final = "breezeTitleLabel"
PROP_TITLE_ICON: Final = "breezeTitleIcon"
PROP_TITLE_BUTTON: Final = "breezeTitleButton"
PROP_TITLE_BUTTON_ROLE: Final = "breezeTitleButtonRole"

PROP_BADGE: Final = "breezeBadge"
PROP_STATE_TOOLTIP: Final = "breezeStateToolTip"
PROP_FLYOUT: Final = "breezeFlyout"
PROP_TEACHING_TIP: Final = "breezeTeachingTip"

PROP_PIVOT: Final = "breezePivot"
PROP_PIVOT_ITEM: Final = "breezePivotItem"
PROP_SEGMENTED: Final = "breezeSegmented"
PROP_SEGMENTED_ITEM: Final = "breezeSegmentedItem"
PROP_BREADCRUMB: Final = "breezeBreadcrumb"
PROP_BREADCRUMB_ITEM: Final = "breezeBreadcrumbItem"
PROP_TAB_BAR: Final = "breezeTabBar"
PROP_TAB_ITEM: Final = "breezeTabItem"

PROP_ROUND_MENU: Final = "breezeRoundMenu"
PROP_COMMAND_BAR: Final = "breezeCommandBar"
PROP_COMMAND_ITEM: Final = "breezeCommandItem"

PROP_DIALOG: Final = "breezeDialog"

PROP_CALENDAR_PICKER: Final = "breezeCalendarPicker"
PROP_DATE_PICKER: Final = "breezeDatePicker"
PROP_TIME_PICKER: Final = "breezeTimePicker"

PROP_SPLASH_SCREEN: Final = "breezeSplashScreen"

PROP_ITEM_VIEW: Final = "breezeItemView"
PROP_FLIP_VIEW: Final = "breezeFlipView"
PROP_CYCLE_LIST: Final = "breezeCycleList"
PROP_AVATAR: Final = "breezeAvatar"
PROP_PLAY_BAR: Final = "breezePlayBar"
PROP_VIDEO_WIDGET: Final = "breezeVideoWidget"

# --- Allowed property values ---------------------------------------------------

ROLE_PRIMARY: Final = "primary"
ROLE_TRANSPARENT: Final = "transparent"

LABEL_CAPTION: Final = "caption"
LABEL_BODY_STRONG: Final = "bodyStrong"
LABEL_SUBTITLE: Final = "subtitle"
LABEL_TITLE: Final = "title"

CARD_DEFAULT: Final = "true"
CARD_ELEVATED: Final = "elevated"

BADGE_DEFAULT: Final = "default"
BADGE_INFO: Final = "info"
BADGE_SUCCESS: Final = "success"
BADGE_ATTENTION: Final = "attention"
BADGE_WARNING: Final = "warning"
BADGE_DANGER: Final = "danger"

TITLE_BUTTON_ROLE_BACK: Final = "back"
TITLE_BUTTON_ROLE_ACTION: Final = "action"
TITLE_BUTTON_ROLE_CLOSE: Final = "close"
TITLE_BUTTON_ROLE_MINIMIZE: Final = "minimize"
TITLE_BUTTON_ROLE_MAXIMIZE: Final = "maximize"
TITLE_BUTTON_ROLE_RESTORE: Final = "restore"
