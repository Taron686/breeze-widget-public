from __future__ import annotations

from PySide6.QtCore import QCoreApplication, QEvent
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget

from breezewidget import (
    BreezeIcon,
    BreezePalette,
    PushButton,
    StyleSheetBase,
    StyleSheetManager,
    Theme,
    ThemeManager,
    applyTheme,
    getPalette,
    isDarkTheme,
    setCustomStyleSheet,
    setTheme,
    setThemeColor,
)
from breezewidget.theme import build_stylesheet


def test_theme_enum_values():
    assert Theme.LIGHT.value == "light"
    assert Theme.DARK.value == "dark"
    assert Theme.AUTO.value == "auto"


def test_set_theme_switches_dark(qapp):
    setTheme(Theme.DARK, qapp)
    assert isDarkTheme() is True
    setTheme(Theme.LIGHT, qapp)
    assert isDarkTheme() is False


def test_theme_refresh_recolors_child_button_icons(qapp):
    parent = QWidget()
    button = PushButton("Icon button", parent=parent, icon=BreezeIcon.SAVE)
    parent.show()

    setTheme(Theme.DARK, qapp)
    assert _count_icon_pixels(
        button,
        lambda color: color.alpha() > 32 and color.red() > 220 and color.green() > 220 and color.blue() > 220,
    ) > 0

    setTheme(Theme.LIGHT, qapp)
    assert _count_icon_pixels(
        button,
        lambda color: color.alpha() > 32 and color.red() < 40 and color.green() < 40 and color.blue() < 40,
    ) > 0


def test_set_theme_accepts_string(qapp):
    setTheme("dark", qapp)
    assert isDarkTheme() is True
    setTheme("light", qapp)
    assert isDarkTheme() is False


def test_get_palette_returns_breeze_palette(qapp):
    setTheme(Theme.LIGHT, qapp)
    palette = getPalette()
    assert isinstance(palette, BreezePalette)
    for field in ("primary4", "surface1", "text1", "border1", "chrome_bg", "danger1"):
        value = getattr(palette, field)
        assert isinstance(value, str) and value.startswith("#")


def test_palette_changes_between_light_and_dark(qapp):
    setTheme(Theme.LIGHT, qapp)
    light_surface = getPalette().surface1
    setTheme(Theme.DARK, qapp)
    dark_surface = getPalette().surface1
    assert light_surface != dark_surface


def test_set_theme_color_changes_primary(qapp):
    setTheme(Theme.LIGHT, qapp)
    setThemeColor("#11d9f3", qapp)
    palette_a = getPalette()
    setThemeColor("#0067c0", qapp)
    palette_b = getPalette()
    assert palette_a.primary4 != palette_b.primary4


def test_apply_theme_does_not_raise(qapp):
    applyTheme(qapp)


def test_set_custom_stylesheet_tracks_theme(qapp):
    setTheme(Theme.LIGHT, qapp)
    widget = QWidget()
    setCustomStyleSheet(widget, "QWidget { color: #111111; }", "QWidget { color: #eeeeee; }")
    assert "#111111" in widget.styleSheet()
    setTheme(Theme.DARK, qapp)
    assert "#eeeeee" in widget.styleSheet()


def test_set_custom_stylesheet_ignores_deleted_widget(qapp):
    setTheme(Theme.LIGHT, qapp)
    widget = PushButton("Deleted")
    setCustomStyleSheet(widget, "QPushButton { color: #111111; }", "QPushButton { color: #eeeeee; }")

    widget.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)

    setTheme(Theme.DARK, qapp)
    setThemeColor("#11d9f3", qapp)


def test_primary_text_follows_theme(qapp):
    setTheme(Theme.LIGHT, qapp)
    assert getPalette().primary_text == "#ffffff"
    setTheme(Theme.DARK, qapp)
    assert getPalette().primary_text == "#000000"


def test_primary_text_independent_of_accent(qapp):
    setTheme(Theme.DARK, qapp)
    setThemeColor("#11d9f3", qapp)
    light_accent_dark_theme = getPalette().primary_text
    setThemeColor("#0067c0", qapp)
    dark_accent_dark_theme = getPalette().primary_text
    assert light_accent_dark_theme == dark_accent_dark_theme == "#000000"


def test_theme_manager_signal_fires_on_set_theme(qapp, qtbot):
    setTheme(Theme.LIGHT, qapp)
    manager = ThemeManager.instance()

    with qtbot.waitSignal(manager.themeChanged, timeout=1000) as signal:
        setTheme(Theme.DARK, qapp)

    assert signal.args == [Theme.DARK]


def test_stylesheet_manager_register_includes_custom_qss(qapp):
    class CustomWidget:
        pass

    class CustomProvider(StyleSheetBase):
        def build(self, palette):
            return f'QWidget[breezeCustom="true"] {{ color: {palette.primary4}; }}'

    StyleSheetManager.register(CustomWidget, CustomProvider())
    try:
        qss = build_stylesheet()
    finally:
        StyleSheetManager.unregister(CustomWidget)

    assert 'QWidget[breezeCustom="true"]' in qss


def test_stylesheet_styles_table_corner_button(qapp):
    qss = build_stylesheet()

    assert "QTableCornerButton::section" in qss


def _count_icon_pixels(button: PushButton, predicate) -> int:
    image = button.icon().pixmap(32, 32).toImage()
    return sum(
        1
        for y in range(image.height())
        for x in range(image.width())
        if predicate(image.pixelColor(x, y))
    )
