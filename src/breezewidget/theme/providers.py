from __future__ import annotations

from .palette import BreezePalette
from .provider_base import StyleSheetBase

QssSelector = str | tuple[str, ...]
QssDeclaration = tuple[str, str]


def _qss_rule(selectors: QssSelector, *declarations: QssDeclaration) -> str:
    selector_text = ",\n".join(selectors) if isinstance(selectors, tuple) else selectors
    body = "\n".join(f"    {name}: {value};" for name, value in declarations)
    return f"{selector_text} {{\n{body}\n}}"


def _state_selectors(selectors: QssSelector, state: str) -> QssSelector:
    if isinstance(selectors, tuple):
        return tuple(f"{selector}:{state}" for selector in selectors)
    return f"{selectors}:{state}"


def _background_state_rule(
    selectors: QssSelector,
    state: str,
    background: str,
    *,
    radius: str | None = None,
    border_color: str | None = None,
    color: str | None = None,
) -> str:
    declarations: list[QssDeclaration] = [("background", background)]
    if border_color is not None:
        declarations.append(("border-color", border_color))
    if color is not None:
        declarations.append(("color", color))
    if radius is not None:
        declarations.append(("border-radius", radius))
    return _qss_rule(_state_selectors(selectors, state), *declarations)


class BaseStyleSheet(StyleSheetBase):
    def build(self, palette: BreezePalette) -> str:
        return f"""
QWidget {{
    color: {palette.text1};
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 14px;
}}

QWidget:window {{
    background: {palette.surface1};
}}

QLabel {{
    background: transparent;
}}
"""


class WindowStyleSheet(StyleSheetBase):
    def build(self, palette: BreezePalette) -> str:
        return f"""
QWidget[breezeWindowContentHost="true"] {{
    background: {palette.surface1};
    border: none;
}}

QWidget[breezeWindowContent="true"],
QStackedWidget[breezeWindowContent="true"] {{
    background: {palette.surface2};
    border: none;
    border-radius: 8px;
}}
"""


class ButtonStyleSheet(StyleSheetBase):
    def build(self, palette: BreezePalette) -> str:
        control_radius = "8px"
        buttons = ("QPushButton", "QToolButton")
        primary_buttons = ('QPushButton[breezeRole="primary"]', 'QToolButton[breezeRole="primary"]')
        pill = 'QPushButton[breezePill="true"]'
        checked_pill = 'QPushButton[breezePill="true"]:checked'
        return f"""
QPushButton, QToolButton {{
    background: {palette.surface2};
    border: 1px solid {palette.border1};
    border-radius: {control_radius};
    padding: 6px 12px;
    min-height: 22px;
}}

{_background_state_rule(buttons, "hover", palette.surface4, radius=control_radius)}

{_background_state_rule(buttons, "pressed", palette.surface5, radius=control_radius)}

{_background_state_rule(buttons, "disabled", palette.surface3, radius=control_radius, color=palette.text2)}

QPushButton[breezeRole="primary"], QToolButton[breezeRole="primary"] {{
    background: {palette.primary4};
    border-color: {palette.primary4};
    color: {palette.primary_text};
}}

{_background_state_rule(primary_buttons, "hover", palette.primary3, radius=control_radius, border_color=palette.primary3)}

{_background_state_rule(primary_buttons, "pressed", palette.primary5, radius=control_radius, border_color=palette.primary5)}

QPushButton[breezeRole="transparent"], QToolButton[breezeRole="transparent"] {{
    background: transparent;
    border-color: transparent;
    border-radius: {control_radius};
}}

QPushButton[breezePill="true"] {{
    background: {palette.surface2};
    border: 1px solid {palette.border1};
    border-radius: 18px;
    padding-left: 18px;
    padding-right: 18px;
}}

{_background_state_rule(pill, "hover", palette.surface4, radius="18px")}

{_background_state_rule(pill, "pressed", palette.surface5, radius="18px")}

QPushButton[breezePill="true"]:checked {{
    background: {palette.primary4};
    border-color: {palette.primary4};
    color: {palette.primary_text};
    border-radius: 18px;
}}

{_background_state_rule(checked_pill, "hover", palette.primary3, radius="18px", border_color=palette.primary3)}

{_background_state_rule(checked_pill, "pressed", palette.primary5, radius="18px", border_color=palette.primary5)}

QPushButton::menu-indicator,
QToolButton::menu-indicator {{
    image: none;
    width: 0;
    height: 0;
    subcontrol-origin: padding;
    subcontrol-position: right center;
}}

QToolButton[breezeExpandToggle="true"] {{
    padding: 0;
    min-height: 0;
}}
"""


class InputStyleSheet(StyleSheetBase):
    def build(self, palette: BreezePalette) -> str:
        control_radius = "8px"
        return f"""
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox,
QDoubleSpinBox, QDateEdit, QTimeEdit, QDateTimeEdit {{
    background: {palette.surface2};
    border: 1px solid {palette.border1};
    border-radius: {control_radius};
    padding: 5px 8px;
    selection-background-color: {palette.primary4};
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus,
QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus,
QDateEdit:focus, QTimeEdit:focus, QDateTimeEdit:focus {{
    border-color: {palette.primary4};
    border-radius: {control_radius};
}}

QComboBox::drop-down,
QDateEdit::drop-down, QTimeEdit::drop-down, QDateTimeEdit::drop-down {{
    background: transparent;
    border: none;
    border-radius: {control_radius};
    width: 24px;
    subcontrol-origin: padding;
    subcontrol-position: top right;
}}

QComboBox::down-arrow,
QDateEdit::down-arrow, QTimeEdit::down-arrow, QDateTimeEdit::down-arrow {{
    image: none;
    width: 0;
    height: 0;
    background: transparent;
    border: none;
}}

QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button,
QDateEdit::up-button, QDateEdit::down-button,
QTimeEdit::up-button, QTimeEdit::down-button,
QDateTimeEdit::up-button, QDateTimeEdit::down-button {{
    border: none;
    width: 20px;
}}

QSpinBox::up-arrow, QSpinBox::down-arrow,
QDoubleSpinBox::up-arrow, QDoubleSpinBox::down-arrow,
QDateEdit::up-arrow, QDateEdit::down-arrow,
QTimeEdit::up-arrow, QTimeEdit::down-arrow,
QDateTimeEdit::up-arrow, QDateTimeEdit::down-arrow {{
    image: none;
    width: 0;
    height: 0;
}}

QComboBox QAbstractItemView {{
    background: {palette.surface2};
    border: 1px solid {palette.border1};
    border-radius: 8px;
    padding: 4px;
    outline: none;
    selection-background-color: {palette.primary4};
    selection-color: {palette.primary_text};
}}

QComboBox QAbstractItemView::item {{
    border-radius: 6px;
    padding: 6px 10px;
    margin: 1px 2px;
    color: {palette.text1};
    background: transparent;
}}

QComboBox QAbstractItemView::item:hover {{
    background: {palette.surface4};
}}

QComboBox QAbstractItemView::item:selected {{
    background: {palette.primary4};
    color: {palette.primary_text};
}}
"""


class ChoiceStyleSheet(StyleSheetBase):
    def build(self, palette: BreezePalette) -> str:
        small_radius = "6px"
        pill_radius = "999px"
        return f"""
QCheckBox::indicator, QRadioButton::indicator {{
    width: 18px;
    height: 18px;
    border-radius: {small_radius};
}}

QCheckBox::indicator:checked {{
    background: {palette.primary4};
    border: 1px solid {palette.primary4};
    border-radius: {small_radius};
}}

QRadioButton::indicator:checked {{
    background: {palette.primary4};
    border: 1px solid {palette.primary4};
    border-radius: {pill_radius};
}}
"""


class SliderStyleSheet(StyleSheetBase):
    def build(self, palette: BreezePalette) -> str:
        del palette
        return """
QSlider {
    background: transparent;
}
"""


class ProgressStyleSheet(StyleSheetBase):
    def build(self, palette: BreezePalette) -> str:
        control_radius = "8px"
        return f"""
QProgressBar {{
    background: {palette.surface3};
    border: 1px solid {palette.border1};
    border-radius: {control_radius};
    text-align: center;
}}

QProgressBar::chunk {{
    background: {palette.primary4};
    border-radius: {control_radius};
}}
"""


class CardStyleSheet(StyleSheetBase):
    def build(self, palette: BreezePalette) -> str:
        del palette
        return """
QFrame[breezeCard="true"] {
    background: transparent;
    border: none;
}

QFrame[breezeCard="elevated"] {
    background: transparent;
    border: none;
}
"""


class InfoBarStyleSheet(StyleSheetBase):
    def build(self, palette: BreezePalette) -> str:
        control_radius = "8px"
        return f"""
QWidget[breezeInfoBar="true"] {{
    background: {palette.surface2};
    border: 1px solid {palette.border1};
    border-radius: {control_radius};
}}
"""


class BadgeStyleSheet(StyleSheetBase):
    def build(self, palette: BreezePalette) -> str:
        del palette
        return """
QWidget[breezeBadge="default"],
QWidget[breezeBadge="info"],
QWidget[breezeBadge="success"],
QWidget[breezeBadge="attention"],
QWidget[breezeBadge="warning"],
QWidget[breezeBadge="danger"] {
    background: transparent;
}
"""


class StateToolTipStyleSheet(StyleSheetBase):
    def build(self, palette: BreezePalette) -> str:
        del palette
        return """
QWidget[breezeStateToolTip="true"] {
    background: transparent;
}
"""


class FlyoutStyleSheet(StyleSheetBase):
    def build(self, palette: BreezePalette) -> str:
        del palette
        return """
QWidget[breezeFlyout="true"] {
    background: transparent;
}
"""


class TeachingTipStyleSheet(StyleSheetBase):
    def build(self, palette: BreezePalette) -> str:
        del palette
        return """
QWidget[breezeTeachingTip="true"] {
    background: transparent;
}
"""


class PivotStyleSheet(StyleSheetBase):
    def build(self, palette: BreezePalette) -> str:
        return f"""
QWidget[breezePivot="true"] {{
    background: transparent;
    border-bottom: 1px solid {palette.border1};
}}

QPushButton[breezePivotItem="true"] {{
    background: transparent;
    border: none;
    color: {palette.text2};
    padding: 4px 12px;
    font-weight: 500;
}}

QPushButton[breezePivotItem="true"]:hover {{
    color: {palette.text1};
}}

QPushButton[breezePivotItem="true"]:checked {{
    color: {palette.text1};
    font-weight: 600;
}}
"""


class SegmentedStyleSheet(StyleSheetBase):
    def build(self, palette: BreezePalette) -> str:
        item = 'QPushButton[breezeSegmentedItem="true"]'
        return f"""
QWidget[breezeSegmented="true"] {{
    background: {palette.surface3};
    border: 1px solid {palette.border1};
    border-radius: 8px;
    padding: 2px;
}}

QPushButton[breezeSegmentedItem="true"] {{
    background: transparent;
    border: none;
    border-radius: 6px;
    padding: 4px 14px;
    color: {palette.text1};
}}

{_background_state_rule(item, "hover", palette.surface4, radius="6px")}

{_background_state_rule(item, "checked", palette.primary4, radius="6px", color=palette.primary_text)}
"""


class BreadcrumbStyleSheet(StyleSheetBase):
    def build(self, palette: BreezePalette) -> str:
        return f"""
QWidget[breezeBreadcrumb="true"] {{
    background: transparent;
}}

QPushButton[breezeBreadcrumbItem="true"] {{
    background: transparent;
    border: none;
    color: {palette.text2};
    padding: 2px 6px;
}}

QPushButton[breezeBreadcrumbItem="true"]:hover {{
    color: {palette.text1};
}}

QPushButton[breezeBreadcrumbItem="true"][breezeBreadcrumbActive="true"] {{
    color: {palette.text1};
    font-weight: 600;
}}
"""


class TabBarStyleSheet(StyleSheetBase):
    def build(self, palette: BreezePalette) -> str:
        return f"""
QWidget[breezeTabBar="true"] {{
    background: transparent;
    border-bottom: 1px solid {palette.border1};
}}

QWidget[breezeTabItem="true"] {{
    background: transparent;
    border-radius: 6px;
}}

QPushButton[breezeTabItem="true"] {{
    background: transparent;
    border: none;
    border-radius: 6px;
    color: {palette.text2};
    padding: 4px 12px;
}}

QPushButton[breezeTabItem="true"]:hover {{
    background: {palette.surface4};
    color: {palette.text1};
    border-radius: 6px;
}}

QPushButton[breezeTabItem="true"]:checked {{
    background: {palette.surface2};
    color: {palette.text1};
    border-radius: 6px;
    font-weight: 600;
}}
"""


class NavigationStyleSheet(StyleSheetBase):
    def build(self, palette: BreezePalette) -> str:
        control_radius = "8px"
        item = 'QPushButton[breezeNavigationItem="true"]'
        compact_item = 'QPushButton[breezeNavigationItemCompact="true"]'
        return f"""
QWidget[breezeNavigation="true"] {{
    background: {palette.surface1};
    color: {palette.chrome_text};
    border-right: 1px solid {palette.chrome_border};
}}

QWidget[breezeNavigationCompact="true"] {{
    border-right: 1px solid {palette.chrome_border};
}}

QPushButton[breezeNavigationItem="true"] {{
    background: transparent;
    border-color: transparent;
    border-radius: {control_radius};
    color: {palette.chrome_text};
    text-align: left;
    padding: 0 10px;
    min-height: 40px;
    max-height: 40px;
}}

{_background_state_rule(item, "checked", palette.chrome_hover, radius=control_radius)}

QFrame[breezeNavigationIndicator="true"] {{
    background: {palette.primary4};
    border: none;
    border-radius: 2px;
}}

QPushButton[breezeNavigationItemCompact="true"] {{
    padding-left: 10px;
    padding-right: 10px;
    text-align: left;
}}

{_background_state_rule(compact_item, "hover", palette.chrome_hover, radius=control_radius)}

{_background_state_rule(compact_item, "checked", palette.chrome_hover, radius=control_radius)}

QPushButton[breezeNavigationItemCompact="false"] {{
    min-width: 0;
    text-align: left;
    padding-left: 10px;
    padding-right: 12px;
}}
"""


class TitleBarStyleSheet(StyleSheetBase):
    def build(self, palette: BreezePalette) -> str:
        control_radius = "8px"
        title_button = 'QToolButton[breezeTitleButton="true"]'
        close_button = 'QToolButton[breezeTitleButtonRole="close"]'
        return f"""
QWidget[breezeTitleBar="true"] {{
    background: {palette.chrome_bg};
    color: {palette.chrome_text};
    border-bottom: 1px solid {palette.chrome_border};
}}

QLabel[breezeTitleLabel="true"],
QLabel[breezeTitleIcon="true"] {{
    background: transparent;
    color: {palette.chrome_text};
}}

QToolButton[breezeTitleButton="true"] {{
    background: transparent;
    border: none;
    border-radius: {control_radius};
    color: {palette.chrome_text};
    font-size: 13px;
    min-width: 46px;
    max-width: 46px;
    min-height: 40px;
    max-height: 40px;
    padding: 0;
}}

QToolButton[breezeTitleButtonRole="back"],
QToolButton[breezeTitleButtonRole="action"] {{
    min-width: 42px;
    max-width: 42px;
}}

{_background_state_rule(title_button, "hover", palette.chrome_hover, radius=control_radius)}

{_background_state_rule(title_button, "pressed", palette.chrome_pressed, radius=control_radius)}

{_background_state_rule(close_button, "hover", palette.danger1, radius=control_radius, color=palette.danger_text)}
"""


class ThemePillStyleSheet(StyleSheetBase):
    def build(self, palette: BreezePalette) -> str:
        pill_radius = "999px"
        return f"""
QWidget[breezeThemePill="true"] {{
    background: {palette.primary6};
    border: 1px solid {palette.primary5};
    border-radius: {pill_radius};
}}
"""


class LabelStyleSheet(StyleSheetBase):
    def build(self, palette: BreezePalette) -> str:
        return f"""
QLabel[breezeLabel="caption"] {{
    color: {palette.text2};
    font-size: 12px;
}}

QLabel[breezeLabel="bodyStrong"] {{
    font-weight: 600;
}}

QLabel[breezeLabel="subtitle"] {{
    font-size: 16px;
    font-weight: 600;
}}

QLabel[breezeLabel="title"] {{
    font-size: 22px;
    font-weight: 600;
}}
"""


class ScrollStyleSheet(StyleSheetBase):
    def build(self, palette: BreezePalette) -> str:
        return f"""
QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 0;
    border-radius: 4px;
}}

QScrollBar::handle:vertical {{
    background: {palette.border1};
    min-height: 30px;
    border-radius: 4px;
    margin: 2px;
}}

QScrollBar::handle:vertical:hover {{
    background: {palette.text2};
}}

QScrollBar::handle:vertical:pressed {{
    background: {palette.text1};
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0;
    background: none;
    border: none;
}}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {{
    background: none;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 8px;
    margin: 0;
    border-radius: 4px;
}}

QScrollBar::handle:horizontal {{
    background: {palette.border1};
    min-width: 30px;
    border-radius: 4px;
    margin: 2px;
}}

QScrollBar::handle:horizontal:hover {{
    background: {palette.text2};
}}

QScrollBar::handle:horizontal:pressed {{
    background: {palette.text1};
}}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {{
    width: 0;
    background: none;
    border: none;
}}

QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {{
    background: none;
}}
"""


class RoundMenuStyleSheet(StyleSheetBase):
    def build(self, palette: BreezePalette) -> str:
        return f"""
QMenu[breezeRoundMenu="true"] {{
    background: {palette.surface2};
    border: 1px solid {palette.border1};
    border-radius: 8px;
    padding: 4px;
    color: {palette.text1};
}}

QMenu[breezeRoundMenu="true"]::item {{
    background: transparent;
    border-radius: 6px;
    padding: 6px 18px 6px 14px;
    margin: 1px 2px;
}}

QMenu[breezeRoundMenu="true"]::item:selected {{
    background: {palette.surface4};
    color: {palette.text1};
}}

QMenu[breezeRoundMenu="true"]::item:disabled {{
    color: {palette.text2};
}}

QMenu[breezeRoundMenu="true"]::separator {{
    height: 1px;
    background: {palette.border1};
    margin: 4px 6px;
}}

QMenu[breezeRoundMenu="true"]::indicator {{
    width: 14px;
    height: 14px;
    margin-left: 4px;
}}
"""


class CommandBarStyleSheet(StyleSheetBase):
    def build(self, palette: BreezePalette) -> str:
        item = 'QToolButton[breezeCommandItem="true"]'
        return f"""
QWidget[breezeCommandBar="true"] {{
    background: {palette.surface2};
    border: 1px solid {palette.border1};
    border-radius: 8px;
}}

QToolButton[breezeCommandItem="true"] {{
    background: transparent;
    border: none;
    border-radius: 6px;
    padding: 6px 10px;
    color: {palette.text1};
}}

{_background_state_rule(item, "hover", palette.surface4, radius="6px")}

{_background_state_rule(item, "pressed", palette.surface5, radius="6px")}

QToolButton[breezeCommandItem="true"]:disabled {{
    color: {palette.text2};
}}

QFrame#breezeCommandSeparator {{
    background: {palette.border1};
    border: none;
}}
"""


class DialogStyleSheet(StyleSheetBase):
    def build(self, palette: BreezePalette) -> str:
        return f"""
QDialog[breezeDialog="true"] {{
    background: transparent;
    color: {palette.text1};
}}

QFrame[breezeDialogCard="true"] {{
    background: {palette.surface2};
    border: 1px solid {palette.border1};
    border-radius: 12px;
}}

QWidget[breezeTitleBar="true"][breezeDialogTitleBar="true"] {{
    background: {palette.surface1};
    color: {palette.chrome_text};
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
    border-bottom: 1px solid {palette.border1};
}}

QFrame[breezeDialogButtonGroup="true"] {{
    background: {palette.surface1};
    border: none;
    border-top: 1px solid {palette.border1};
    border-bottom-left-radius: 12px;
    border-bottom-right-radius: 12px;
}}

QWidget[breezeDialogMask="true"] {{
    background: rgba(0, 0, 0, 140);
    border: none;
}}

QDialog[breezeDialog="true"] QListWidget {{
    background: {palette.surface2};
    border: 1px solid {palette.border1};
    border-radius: 8px;
    padding: 4px;
}}

QDialog[breezeDialog="true"] QListWidget::item {{
    padding: 4px 8px;
    border-radius: 4px;
}}

QDialog[breezeDialog="true"] QListWidget::item:selected {{
    background: {palette.surface4};
    color: {palette.text1};
}}
"""


class PickerStyleSheet(StyleSheetBase):
    def build(self, palette: BreezePalette) -> str:
        calendar_picker = 'QPushButton[breezeCalendarPicker="true"]'
        return f"""
QPushButton[breezeCalendarPicker="true"] {{
    background: {palette.surface2};
    border: 1px solid {palette.border1};
    border-radius: 8px;
    padding: 5px 12px;
    text-align: left;
    color: {palette.text1};
}}

{_background_state_rule(calendar_picker, "hover", palette.surface4, radius="8px")}

{_background_state_rule(calendar_picker, "pressed", palette.surface5, radius="8px")}

QWidget[breezeDatePicker="true"],
QWidget[breezeTimePicker="true"] {{
    background: transparent;
}}

QCalendarWidget QWidget {{
    alternate-background-color: {palette.surface3};
}}

QCalendarWidget QAbstractItemView:enabled {{
    background: {palette.surface2};
    color: {palette.text1};
    selection-background-color: {palette.primary4};
    selection-color: {palette.primary_text};
}}

QCalendarWidget QToolButton {{
    background: transparent;
    color: {palette.text1};
    border: none;
    border-radius: 6px;
    padding: 4px 8px;
}}

QCalendarWidget QToolButton:hover {{
    background: {palette.surface4};
}}

QCalendarWidget QSpinBox {{
    background: {palette.surface2};
    border: 1px solid {palette.border1};
    border-radius: 6px;
}}
"""


class SplashScreenStyleSheet(StyleSheetBase):
    def build(self, palette: BreezePalette) -> str:
        return f"""
QWidget[breezeSplashScreen="true"] {{
    background: {palette.surface2};
    border: 1px solid {palette.border1};
    border-radius: 12px;
}}
"""


class ItemViewStyleSheet(StyleSheetBase):
    def build(self, palette: BreezePalette) -> str:
        return f"""
QListView[breezeItemView="list"],
QTableView[breezeItemView="table"],
QTableWidget[breezeItemView="tableWidget"],
QTreeView[breezeItemView="tree"] {{
    background: {palette.surface2};
    alternate-background-color: {palette.surface3};
    border: 1px solid {palette.border1};
    border-radius: 8px;
    color: {palette.text1};
    selection-background-color: {palette.surface4};
    selection-color: {palette.text1};
}}

QListView[breezeItemView="list"]::viewport,
QTableView[breezeItemView="table"]::viewport,
QTableWidget[breezeItemView="tableWidget"]::viewport,
QTreeView[breezeItemView="tree"]::viewport {{
    background: {palette.surface2};
}}

QListView[breezeItemView="list"]::item,
QTreeView[breezeItemView="tree"]::item,
QTableView[breezeItemView="table"]::item,
QTableWidget[breezeItemView="tableWidget"]::item {{
    padding: 4px 8px;
    border-radius: 4px;
}}

QListView[breezeItemView="list"]::item:selected,
QTreeView[breezeItemView="tree"]::item:selected,
QTableView[breezeItemView="table"]::item:selected,
QTableWidget[breezeItemView="tableWidget"]::item:selected {{
    background: {palette.surface4};
    color: {palette.text1};
}}

QHeaderView::section {{
    background: {palette.surface3};
    color: {palette.text1};
    border: none;
    padding: 4px 8px;
}}

QTableCornerButton::section {{
    background: {palette.surface3};
    border: none;
}}

QListWidget[breezeCycleList="true"] {{
    background: {palette.surface2};
    border: 1px solid {palette.border1};
    border-radius: 8px;
    padding: 4px;
}}

QListWidget[breezeCycleList="true"]::item {{
    padding: 4px 12px;
    border-radius: 4px;
}}

QListWidget[breezeCycleList="true"]::item:selected {{
    background: {palette.primary4};
    color: {palette.primary_text};
}}
"""


class FlipViewStyleSheet(StyleSheetBase):
    def build(self, palette: BreezePalette) -> str:
        return f"""
QWidget[breezeFlipView="true"] {{
    background: {palette.surface2};
    border: 1px solid {palette.border1};
    border-radius: 8px;
}}
"""


class PlayBarStyleSheet(StyleSheetBase):
    def build(self, palette: BreezePalette) -> str:
        return f"""
QWidget[breezePlayBar="true"] {{
    background: {palette.surface2};
    border: 1px solid {palette.border1};
    border-radius: 8px;
}}

QWidget[breezePlayBar="true"] QToolButton {{
    background: transparent;
    border: none;
    border-radius: 6px;
    padding: 4px 6px;
}}

QWidget[breezePlayBar="true"] QToolButton:hover {{
    background: {palette.surface4};
}}

QWidget[breezePlayBar="true"] QLabel {{
    color: {palette.text2};
}}
"""
