from __future__ import annotations

import weakref
from enum import Enum
from typing import Any, ClassVar

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication, QWidget
from shiboken6 import isValid as _is_qobject_valid

from .palette import BreezePalette, _build_palette
from .provider_base import StyleSheetBase
from .styles import _StyleSheetRegistry


class Theme(str, Enum):
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


class ThemeManager(QObject):
    themeChanged = Signal(Theme)
    themeColorChanged = Signal(QColor)

    _instance: "ThemeManager | None" = None

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._theme = Theme.LIGHT
        self._accent_color = QColor("#0067c0")

    @classmethod
    def instance(cls) -> "ThemeManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def currentTheme(self) -> Theme:
        return self._theme

    @property
    def accentColor(self) -> QColor:
        return QColor(self._accent_color)

    def resolvedTheme(self) -> Theme:
        if self._theme != Theme.AUTO:
            return self._theme

        app = QApplication.instance()
        if app is None:
            return Theme.LIGHT

        window = app.palette().color(QPalette.ColorRole.Window)
        return Theme.DARK if window.lightness() < 128 else Theme.LIGHT

    def isDarkTheme(self) -> bool:
        return self.resolvedTheme() == Theme.DARK

    def setTheme(self, value: Theme | str, target: Any | None = None) -> None:
        theme = _normalize_theme(value)
        changed = theme != self._theme
        self._theme = theme
        _apply_theme(target)
        if changed:
            self.themeChanged.emit(theme)

    def setThemeColor(self, value: Any, target: Any | None = None) -> None:
        color = _normalize_color(value)
        changed = color != self._accent_color
        self._accent_color = color
        _apply_theme(target)
        if changed:
            self.themeColorChanged.emit(QColor(color))

    def applyTheme(self, target: Any | None = None) -> None:
        _apply_theme(target)


def _normalize_theme(value: Theme | str) -> Theme:
    if isinstance(value, Theme):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"light", "l"}:
        return Theme.LIGHT
    if normalized in {"dark", "d"}:
        return Theme.DARK
    if normalized in {"auto", "system"}:
        return Theme.AUTO
    raise ValueError(f"Unknown theme: {value!r}")


def _normalize_color(value: Any) -> QColor:
    if isinstance(value, QColor):
        color = QColor(value)
    else:
        try:
            color = QColor(*value) if isinstance(value, (tuple, list)) else QColor(value)
        except TypeError:
            color = QColor(str(value))
    if not color.isValid():
        raise ValueError(f"Invalid color: {value!r}")
    return QColor(color)


def _target_or_app(target: Any | None) -> Any | None:
    return target if target is not None else QApplication.instance()


def isDarkTheme() -> bool:
    return ThemeManager.instance().isDarkTheme()


def setTheme(value: Theme | str, target: Any | None = None) -> None:
    ThemeManager.instance().setTheme(value, target)


def setThemeColor(value: Any, target: Any | None = None) -> None:
    ThemeManager.instance().setThemeColor(value, target)


def applyTheme(target: Any | None = None) -> None:
    ThemeManager.instance().applyTheme(target)


def _apply_theme(target: Any | None = None) -> None:
    receiver = _target_or_app(target)
    stylesheet = build_stylesheet()
    if isinstance(receiver, QWidget) and receiver.property("_breezeCustomLightQss") is not None:
        _apply_custom_stylesheet(receiver)
    elif receiver is not None and hasattr(receiver, "setStyleSheet"):
        receiver.setStyleSheet(stylesheet)
        if isinstance(receiver, QWidget):
            receiver.setProperty("_breezeAppliedStyleSheet", stylesheet)
    _refresh_theme_widgets(receiver, stylesheet)


def _refresh_theme_widgets(receiver: Any | None, stylesheet: str) -> None:
    if receiver is None:
        return
    if isinstance(receiver, QApplication):
        visited = set()
        for window in receiver.topLevelWidgets():
            if window.property("_breezeCustomLightQss") is not None:
                _apply_custom_stylesheet(window)
            elif window.styleSheet() and window.styleSheet() == window.property("_breezeAppliedStyleSheet"):
                window.setStyleSheet(stylesheet)
                window.setProperty("_breezeAppliedStyleSheet", stylesheet)
            _refresh_widget_tree(window, visited)
        return
    if isinstance(receiver, QWidget):
        _refresh_widget_tree(receiver)
    elif hasattr(receiver, "refreshTheme"):
        receiver.refreshTheme()


def _refresh_widget_tree(widget: QWidget, visited: set | None = None) -> None:
    visited = set() if visited is None else visited
    for current in [widget, *widget.findChildren(QWidget)]:
        if current in visited:
            continue
        visited.add(current)
        if hasattr(current, "refreshTheme"):
            current.refreshTheme()
        current.update()


def getPalette() -> BreezePalette:
    manager = ThemeManager.instance()
    return _build_palette(manager.isDarkTheme(), manager.accentColor)


class StyleSheetManager(_StyleSheetRegistry):
    _instance: ClassVar["StyleSheetManager | None"] = None

    @classmethod
    def instance(cls) -> "StyleSheetManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def register(cls, widget_type: Any, provider: StyleSheetBase) -> None:
        cls.instance()._register(widget_type, provider)

    @classmethod
    def unregister(cls, widget_type: Any) -> None:
        cls.instance()._providers = [
            (owner, provider)
            for owner, provider in cls.instance()._providers
            if owner != widget_type
        ]

    @classmethod
    def build(cls) -> str:
        return cls.instance()._build(getPalette())


def build_stylesheet() -> str:
    return StyleSheetManager.build()


def setCustomStyleSheet(widget: QWidget, light_qss: str, dark_qss: str | None = None) -> None:
    """Apply a light/dark custom stylesheet and refresh it on theme changes."""

    widget.setProperty("_breezeCustomLightQss", str(light_qss))
    widget.setProperty("_breezeCustomDarkQss", str(dark_qss if dark_qss is not None else light_qss))
    _apply_custom_stylesheet(widget)

    if widget.property("_breezeCustomStyleConnected") is True:
        return

    widget_ref = weakref.ref(widget)

    def refresh(_value=None) -> None:
        current = widget_ref()
        if current is not None:
            _apply_custom_stylesheet(current)

    manager = ThemeManager.instance()

    def disconnect_refresh(_destroyed: object | None = None) -> None:
        for signal in (manager.themeChanged, manager.themeColorChanged):
            try:
                signal.disconnect(refresh)
            except (RuntimeError, TypeError):
                pass

    manager.themeChanged.connect(refresh)
    manager.themeColorChanged.connect(refresh)
    widget.destroyed.connect(disconnect_refresh)
    widget.setProperty("_breezeCustomStyleConnected", True)


def _apply_custom_stylesheet(widget: QWidget) -> None:
    if not _is_live_widget(widget):
        return

    qss = widget.property("_breezeCustomDarkQss") if isDarkTheme() else widget.property("_breezeCustomLightQss")
    widget.setStyleSheet(str(qss or ""))


def _is_live_widget(widget: QWidget) -> bool:
    try:
        return bool(_is_qobject_valid(widget))
    except RuntimeError:
        return False
