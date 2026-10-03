from __future__ import annotations

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QWidget

from breezewidget import (
    PrimaryPushButton,
    PushButton,
    DropDownPushButton,
    SplitPushButton,
    Theme,
    ThemeManager,
    TransparentToolButton,
    setTheme,
    setThemeColor,
    getPalette,
)
from breezewidget.constants import PROP_ROLE, ROLE_TRANSPARENT
from examples.widget_demo_pages.basic_input import WidgetDemoPage


def test_gallery_button_menus_render_themed_background(qapp, qtbot):
    old_theme = ThemeManager.instance().currentTheme
    old_stylesheet = qapp.styleSheet()
    page = WidgetDemoPage()
    qtbot.addWidget(page)
    page.resize(1000, 700)
    page.show()
    try:
        for theme in (Theme.DARK, Theme.LIGHT):
            setTheme(theme, qapp)
            qapp.processEvents()
            for button_type in (DropDownPushButton, SplitPushButton):
                button = page.findChild(button_type)
                menu = button.menu()
                if isinstance(button, SplitPushButton):
                    button.showMenu()
                else:
                    menu.popup(button.mapToGlobal(button.rect().bottomLeft()))
                try:
                    qtbot.waitUntil(menu.isVisible)
                    image = menu.grab().toImage()
                    row = menu.actionGeometry(menu.actions()[1])
                    ratio = image.devicePixelRatio()
                    pixel = image.pixelColor(int((menu.width() - 10) * ratio),
                                             int(row.center().y() * ratio))
                    assert pixel == QColor(getPalette().surface2)
                    assert menu.palette().color(QPalette.WindowText) == QColor(getPalette().text1)
                finally:
                    menu.hide()
    finally:
        page.close()
        setTheme(old_theme, qapp)
        qapp.setStyleSheet(old_stylesheet)


def test_gallery_transparent_containers_do_not_override_primary_buttons(qapp):
    setTheme(Theme.DARK, qapp)
    setThemeColor("#11d9f3", qapp)

    page = WidgetDemoPage()
    page.resize(1000, 700)
    page.show()
    qapp.processEvents()

    button = next(
        child
        for child in page.findChildren(PrimaryPushButton)
        if child.text() == "Accent style button"
    )
    image = button.grab().toImage()
    accent = QColor("#11d9f3")

    accent_pixels = sum(
        1
        for y in range(image.height())
        for x in range(image.width())
        if _is_close_to(image.pixelColor(x, y), accent)
    )

    assert accent_pixels > 1000


def test_gallery_header_uses_view_background_and_visible_action_buttons(qapp):
    page = WidgetDemoPage()

    header_widget = page.findChild(QWidget, "galleryPageHeader")
    assert header_widget is not None
    assert "background: transparent" in header_widget.styleSheet()

    header_buttons = {
        child.text(): child
        for child in page.findChildren(PushButton)
        if child.text() in {"Documentation", "Source"}
    }

    assert set(header_buttons) == {"Documentation", "Source"}
    assert all(
        button.property(PROP_ROLE) != ROLE_TRANSPARENT
        for button in header_buttons.values()
    )
    assert len(page.findChildren(TransparentToolButton)) >= 2


def _is_close_to(color: QColor, expected: QColor) -> bool:
    return (
        color.alpha() > 32
        and abs(color.red() - expected.red()) < 12
        and abs(color.green() - expected.green()) < 12
        and abs(color.blue() - expected.blue()) < 12
    )
