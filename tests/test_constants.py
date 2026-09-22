from __future__ import annotations

import pytest

from breezewidget import constants
from breezewidget.theme import build_stylesheet

PROPERTY_NAMES = [
    constants.PROP_ROLE,
    constants.PROP_LABEL,
    constants.PROP_CARD,
    constants.PROP_INFO_BAR,
    constants.PROP_THEME_PILL,
    constants.PROP_PILL,
    constants.PROP_SWITCH,
    constants.PROP_NAVIGATION,
    constants.PROP_NAVIGATION_COMPACT,
    constants.PROP_NAVIGATION_ITEM,
    constants.PROP_NAVIGATION_ITEM_COMPACT,
    constants.PROP_NAVIGATION_INDICATOR,
    constants.PROP_WINDOW_CONTENT_HOST,
    constants.PROP_WINDOW_CONTENT,
    constants.PROP_TITLE_BAR,
    constants.PROP_TITLE_LABEL,
    constants.PROP_TITLE_ICON,
    constants.PROP_TITLE_BUTTON,
    constants.PROP_TITLE_BUTTON_ROLE,
    constants.PROP_BADGE,
    constants.PROP_STATE_TOOLTIP,
    constants.PROP_FLYOUT,
    constants.PROP_TEACHING_TIP,
    constants.PROP_PIVOT,
    constants.PROP_PIVOT_ITEM,
    constants.PROP_SEGMENTED,
    constants.PROP_SEGMENTED_ITEM,
    constants.PROP_BREADCRUMB,
    constants.PROP_BREADCRUMB_ITEM,
    constants.PROP_TAB_BAR,
    constants.PROP_TAB_ITEM,
]

# Properties set in code but with no matching QSS rule yet.
# Phase 2 (widget upgrade) gives these their own styling.
PROPERTIES_WITHOUT_QSS_YET = {constants.PROP_SWITCH}


def test_all_property_names_are_breeze_prefixed():
    for name in PROPERTY_NAMES:
        assert name.startswith("breeze"), name


@pytest.mark.parametrize(
    "name", [n for n in PROPERTY_NAMES if n not in PROPERTIES_WITHOUT_QSS_YET]
)
def test_property_name_appears_in_stylesheet(qapp, name):
    qss = build_stylesheet()
    assert name in qss, (
        f"property name {name!r} from constants.py is not referenced in the "
        f"stylesheet — code and QSS would drift apart"
    )


@pytest.mark.parametrize(
    "value",
    [
        constants.ROLE_PRIMARY,
        constants.ROLE_TRANSPARENT,
        constants.LABEL_CAPTION,
        constants.LABEL_BODY_STRONG,
        constants.LABEL_SUBTITLE,
        constants.LABEL_TITLE,
        constants.CARD_DEFAULT,
        constants.CARD_ELEVATED,
        constants.BADGE_DEFAULT,
        constants.BADGE_INFO,
        constants.BADGE_SUCCESS,
        constants.BADGE_ATTENTION,
        constants.BADGE_WARNING,
        constants.BADGE_DANGER,
    ],
)
def test_property_value_appears_in_stylesheet(qapp, value):
    qss = build_stylesheet()
    assert f'"{value}"' in qss, (
        f"property value {value!r} from constants.py is not used in the QSS"
    )
