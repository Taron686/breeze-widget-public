"""Widget subsystem.

Keeps the import path ``breezewidget.widgets`` stable while splitting the
former single module into one file per widget family. Public symbols are
re-exported here.

Note: cards live in ``breezewidget.cards``, info bars in
``breezewidget.status``, and dialogs in ``breezewidget.dialogs`` — they used
to share ``widgets.py`` but are conceptually separate subsystems.
"""
from __future__ import annotations

from .button import (
    DropDownPushButton,
    HyperlinkButton,
    PillPushButton,
    PrimaryPushButton,
    PrimaryToolButton,
    PushButton,
    SplitPushButton,
    ToggleButton,
    ToolButton,
    TransparentPushButton,
    TransparentToolButton,
)
from .checkbox import CheckBox, RadioButton
from .combo_box import ComboBox, EditableComboBox
from .icon_widget import IconWidget
from .label import BodyLabel, CaptionLabel, StrongBodyLabel, SubtitleLabel, TitleLabel
from .line_edit import LineEdit, PasswordLineEdit, SearchLineEdit
from .progress import IndeterminateProgressBar, ProgressBar
from .slider import ClickableSlider, Slider
from .spin_box import DateEdit, DateTimeEdit, DoubleSpinBox, SpinBox, TimeEdit
from .switch import BreezeThemeSwitch, SwitchButton
from .text_edit import PlainTextEdit, TextEdit

__all__ = [
    "PushButton", "PrimaryPushButton", "TransparentPushButton",
    "ToolButton", "PrimaryToolButton", "TransparentToolButton", "ToggleButton",
    "HyperlinkButton", "DropDownPushButton", "SplitPushButton", "PillPushButton",
    "IconWidget",
    "CheckBox", "RadioButton",
    "SwitchButton", "BreezeThemeSwitch",
    "Slider", "ClickableSlider",
    "LineEdit", "SearchLineEdit", "PasswordLineEdit",
    "TextEdit", "PlainTextEdit",
    "ComboBox", "EditableComboBox",
    "SpinBox", "DoubleSpinBox", "DateEdit", "TimeEdit", "DateTimeEdit",
    "BodyLabel", "CaptionLabel", "StrongBodyLabel", "SubtitleLabel", "TitleLabel",
    "ProgressBar", "IndeterminateProgressBar",
]
