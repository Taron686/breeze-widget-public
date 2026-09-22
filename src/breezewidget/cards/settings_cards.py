from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QColor, QIcon
from PySide6.QtWidgets import (
    QColorDialog,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ..icons import BreezeIcon, icon_from
from ..icons._themed import ThemedIcon, default_icon_color
from ..layout._utils import clear_layout
from ..navigation.segmented import SegmentedWidget
from ..theme import getPalette
from ..widgets import (
    BodyLabel,
    CaptionLabel,
    ClickableSlider,
    ComboBox,
    HyperlinkButton,
    PushButton,
    StrongBodyLabel,
    SwitchButton,
    ToolButton,
)
from .card import CardWidget

_PROP_SETTING_ACTION = "_breezeSettingAction"


class SettingCard(CardWidget):
    """One settings row with icon, title, optional caption and an action slot."""

    clicked = Signal()

    def __init__(
        self,
        icon: Any = None,
        title: str = "",
        caption: str = "",
        parent: QWidget | None = None,
        action: QWidget | None = None,
    ):
        super().__init__(parent)
        self.setMinimumHeight(72)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._actionWidget: QWidget | None = None

        self.iconLabel = QLabel(self)
        self.iconLabel.setFixedSize(28, 28)
        self.iconLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon = ThemedIcon(self._applyIcon, size=20, stroke_width=1.7)

        self.titleLabel = StrongBodyLabel(title, self)
        self.captionLabel = CaptionLabel(caption, self)
        self.captionLabel.setVisible(bool(caption))

        self.textLayout = QVBoxLayout()
        self.textLayout.setContentsMargins(0, 0, 0, 0)
        self.textLayout.setSpacing(2)
        self.textLayout.addWidget(self.titleLabel)
        self.textLayout.addWidget(self.captionLabel)

        self.actionLayout = QHBoxLayout()
        self.actionLayout.setContentsMargins(0, 0, 0, 0)
        self.actionLayout.setSpacing(8)

        self._rowLayout = QHBoxLayout()
        self._rowLayout.setContentsMargins(0, 0, 0, 0)
        self._rowLayout.setSpacing(12)
        self._rowLayout.addWidget(self.iconLabel, 0, Qt.AlignmentFlag.AlignTop)
        self._rowLayout.addLayout(self.textLayout, 1)
        self._rowLayout.addLayout(self.actionLayout, 0)

        self._rootLayout = QVBoxLayout(self)
        self._rootLayout.setContentsMargins(16, 12, 16, 12)
        self._rootLayout.setSpacing(10)
        self._rootLayout.addLayout(self._rowLayout)

        self.setIcon(icon)
        if action is not None:
            self.setActionWidget(action)

    def title(self) -> str:
        return self.titleLabel.text()

    def setTitle(self, title: str) -> None:
        self.titleLabel.setText(title)

    def caption(self) -> str:
        return self.captionLabel.text()

    def setCaption(self, caption: str) -> None:
        self.captionLabel.setText(caption)
        self.captionLabel.setVisible(bool(caption))

    def icon(self) -> Any:
        return self._icon.source

    def setIcon(self, icon: Any) -> None:
        self._icon.set(icon)

    def actionWidget(self) -> QWidget | None:
        return self._actionWidget

    def setActionWidget(self, widget: QWidget | None) -> None:
        clear_layout(self.actionLayout)
        self._actionWidget = widget
        if widget is not None:
            if type(widget) is QWidget:
                widget.setProperty(_PROP_SETTING_ACTION, True)
                widget.setStyleSheet(
                    f'QWidget[{_PROP_SETTING_ACTION}="true"] {{ background: transparent; border: none; }}'
                )
            self.actionLayout.addWidget(widget, 0, Qt.AlignmentFlag.AlignVCenter)

    def refreshTheme(self) -> None:
        self._icon.refresh()

    def _applyIcon(self, icon) -> None:
        if icon.isNull():
            self.iconLabel.clear()
            self.iconLabel.setVisible(False)
            return

        pixmap = icon.pixmap(QSize(20, 20))
        self.iconLabel.setPixmap(pixmap)
        self.iconLabel.setVisible(not pixmap.isNull())



class SettingCardGroup(QWidget):
    """Titled vertical group for settings cards."""

    def __init__(self, title: str = "", parent: QWidget | None = None):
        super().__init__(parent)
        self.titleLabel = StrongBodyLabel(title, self)
        self.cardLayout = QVBoxLayout()
        self.cardLayout.setContentsMargins(0, 0, 0, 0)
        self.cardLayout.setSpacing(8)
        self._cards: list[SettingCard] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(self.titleLabel)
        layout.addLayout(self.cardLayout)

    def title(self) -> str:
        return self.titleLabel.text()

    def setTitle(self, title: str) -> None:
        self.titleLabel.setText(title)

    def addSettingCard(self, card: SettingCard) -> SettingCard:
        self._cards.append(card)
        self.cardLayout.addWidget(card)
        return card

    addCard = addSettingCard

    def cards(self) -> list[SettingCard]:
        return list(self._cards)


class SwitchSettingCard(SettingCard):
    checkedChanged = Signal(bool)

    def __init__(
        self,
        icon: Any = None,
        title: str = "",
        caption: str = "",
        parent: QWidget | None = None,
        checked: bool = False,
    ):
        self.switchButton = SwitchButton("", parent)
        super().__init__(icon, title, caption, parent, self.switchButton)
        self.switchButton.setChecked(checked)
        self.switchButton.toggled.connect(self.checkedChanged.emit)

    def isChecked(self) -> bool:
        return self.switchButton.isChecked()

    def setChecked(self, checked: bool) -> None:
        self.switchButton.setChecked(checked)


class ComboBoxSettingCard(SettingCard):
    currentIndexChanged = Signal(int)
    currentTextChanged = Signal(str)

    def __init__(
        self,
        items: Iterable[str] = (),
        icon: Any = None,
        title: str = "",
        caption: str = "",
        parent: QWidget | None = None,
        current_index: int = 0,
    ):
        self.comboBox = ComboBox(parent)
        self.comboBox.setMinimumWidth(180)
        super().__init__(icon, title, caption, parent, self.comboBox)
        self.comboBox.addItems([str(item) for item in items])
        if self.comboBox.count():
            self.comboBox.setCurrentIndex(max(0, min(current_index, self.comboBox.count() - 1)))
        self.comboBox.currentIndexChanged.connect(self.currentIndexChanged.emit)
        self.comboBox.currentTextChanged.connect(self.currentTextChanged.emit)

    def addItems(self, items: Iterable[str]) -> None:
        self.comboBox.addItems([str(item) for item in items])

    def currentText(self) -> str:
        return self.comboBox.currentText()

    def setCurrentIndex(self, index: int) -> None:
        self.comboBox.setCurrentIndex(index)


class RangeSettingCard(SettingCard):
    valueChanged = Signal(int)

    def __init__(
        self,
        icon: Any = None,
        title: str = "",
        caption: str = "",
        parent: QWidget | None = None,
        minimum: int = 0,
        maximum: int = 100,
        value: int = 0,
    ):
        action = QWidget(parent)
        action_layout = QHBoxLayout(action)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(10)

        self.valueLabel = BodyLabel("", action)
        self.valueLabel.setMinimumWidth(32)
        self.valueLabel.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.slider = ClickableSlider(Qt.Orientation.Horizontal, action)
        self.slider.setFixedWidth(180)
        self.slider.setRange(minimum, maximum)
        self.slider.setValue(value)

        action_layout.addWidget(self.valueLabel)
        action_layout.addWidget(self.slider)

        super().__init__(icon, title, caption, parent, action)
        self.slider.valueChanged.connect(self._syncValue)
        self.slider.valueChanged.connect(self.valueChanged.emit)
        self._syncValue(self.slider.value())

    def value(self) -> int:
        return self.slider.value()

    def setValue(self, value: int) -> None:
        self.slider.setValue(value)

    def setRange(self, minimum: int, maximum: int) -> None:
        self.slider.setRange(minimum, maximum)
        self._syncValue(self.slider.value())

    def _syncValue(self, value: int) -> None:
        self.valueLabel.setText(str(value))


class PushSettingCard(SettingCard):
    actionClicked = Signal()

    def __init__(
        self,
        text: str,
        icon: Any = None,
        title: str = "",
        caption: str = "",
        parent: QWidget | None = None,
    ):
        self.button = PushButton(text, parent)
        super().__init__(icon, title, caption, parent, self.button)
        self.button.clicked.connect(lambda checked=False: self.actionClicked.emit())
        self.clicked.connect(self.button.click)


class HyperlinkCard(SettingCard):
    def __init__(
        self,
        url: str,
        text: str | None = None,
        icon: Any = None,
        title: str = "",
        caption: str = "",
        parent: QWidget | None = None,
    ):
        self.button = HyperlinkButton(url, text, parent)
        super().__init__(icon, title, caption, parent, self.button)
        self.url = url
        self.clicked.connect(self.button.click)


class ExpandSettingCard(SettingCard):
    expandedChanged = Signal(bool)

    def __init__(
        self,
        icon: Any = None,
        title: str = "",
        caption: str = "",
        parent: QWidget | None = None,
        expanded: bool = False,
    ):
        self.expandButton = _ExpandButton(parent=parent)
        self.expandButton.setFixedSize(32, 32)
        self.expandButton.setProperty("breezeExpandToggle", "true")
        self.expandButton.style().unpolish(self.expandButton)
        self.expandButton.style().polish(self.expandButton)
        self.contentWidget = QWidget(parent)
        self.viewLayout = QVBoxLayout(self.contentWidget)
        self.viewLayout.setContentsMargins(40, 0, 0, 0)
        self.viewLayout.setSpacing(8)
        self._expanded = False

        super().__init__(icon, title, caption, parent, self.expandButton)
        self._rootLayout.addWidget(self.contentWidget)
        self.expandButton.clicked.connect(self.toggleExpanded)
        self.clicked.connect(self.toggleExpanded)
        self.setExpanded(expanded)

    def isExpanded(self) -> bool:
        return self._expanded

    def setExpanded(self, expanded: bool) -> None:
        expanded = bool(expanded)
        if expanded == self._expanded:
            self.contentWidget.setVisible(expanded)
            self._refreshExpandIcon()
            return
        self._expanded = expanded
        self.contentWidget.setVisible(expanded)
        self._refreshExpandIcon()
        self.expandedChanged.emit(expanded)

    def toggleExpanded(self) -> None:
        self.setExpanded(not self._expanded)

    def addWidget(self, widget: QWidget) -> None:
        self.viewLayout.addWidget(widget)

    def _refreshExpandIcon(self) -> None:
        self.expandButton.setExpanded(self._expanded)


class _ExpandButton(ToolButton):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(None, parent)
        self._expanded = False
        self.setIconSize(QSize(24, 24))

    def setExpanded(self, expanded: bool) -> None:
        self._expanded = bool(expanded)
        self.refreshTheme()

    def refreshTheme(self) -> None:
        QToolButton.setIcon(self, _expand_icon(self._expanded))


def _expand_icon(expanded: bool) -> QIcon:
    name = "chevron-down" if expanded else "chevron-right"
    return icon_from(
        name,
        color=default_icon_color(),
        size=24,
        stroke_width=2.2,
    )


class OptionsSettingCard(SettingCard):
    currentChanged = Signal(str)

    def __init__(
        self,
        options: Iterable[str | tuple[str, str]] = (),
        icon: Any = None,
        title: str = "",
        caption: str = "",
        parent: QWidget | None = None,
    ):
        self.segmentedWidget = SegmentedWidget(parent)
        super().__init__(icon, title, caption, parent, self.segmentedWidget)
        for option in options:
            self.addOption(option)
        self.segmentedWidget.currentChanged.connect(self.currentChanged.emit)

    def addOption(self, option: str | tuple[str, str]) -> None:
        if isinstance(option, tuple):
            text, key = option
        else:
            text = key = str(option)
        self.segmentedWidget.addItem(str(text), str(key))

    def currentOption(self) -> str | None:
        return self.segmentedWidget.currentRoute()

    def setCurrentOption(self, key: str) -> None:
        self.segmentedWidget.setCurrentRoute(key)


class CustomColorSettingCard(SettingCard):
    colorChanged = Signal(QColor)

    def __init__(
        self,
        color: QColor | str = "#0067c0",
        icon: Any = None,
        title: str = "",
        caption: str = "",
        parent: QWidget | None = None,
        button_text: str = "Choose",
    ):
        action = QWidget(parent)
        action_layout = QHBoxLayout(action)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(8)

        self.swatch = QLabel(action)
        self.swatch.setFixedSize(28, 28)
        self.button = PushButton(button_text, action)
        self._color = _coerce_color(color)

        action_layout.addWidget(self.swatch)
        action_layout.addWidget(self.button)

        super().__init__(icon, title, caption, parent, action)
        self.button.clicked.connect(self.chooseColor)
        self._refreshSwatch()

    def color(self) -> QColor:
        return QColor(self._color)

    def setColor(self, color: QColor | str) -> None:
        new_color = _coerce_color(color)
        if new_color == self._color:
            return
        self._color = new_color
        self._refreshSwatch()
        self.colorChanged.emit(QColor(new_color))

    def chooseColor(self) -> None:
        color = QColorDialog.getColor(self._color, self.window(), self.title())
        if color.isValid():
            self.setColor(color)

    def refreshTheme(self) -> None:
        super().refreshTheme()
        self._refreshSwatch()

    def _refreshSwatch(self) -> None:
        palette = getPalette()
        self.swatch.setStyleSheet(
            "QLabel { "
            f"background: {self._color.name()}; "
            f"border: 1px solid {palette.border1}; "
            "border-radius: 6px; "
            "}"
        )

def _coerce_color(value: QColor | str) -> QColor:
    color = QColor(value) if isinstance(value, QColor) else QColor(str(value))
    if not color.isValid():
        raise ValueError(f"Invalid color: {value!r}")
    return QColor(color)
