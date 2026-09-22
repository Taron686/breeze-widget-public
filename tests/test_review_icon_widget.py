from PySide6.QtWidgets import QWidget
from breezewidget import BreezeIcon, IconWidget, Theme, setTheme


def test_icon_widget_refreshes_builtin_icon_on_theme_change(qapp, qtbot):
    parent = QWidget()
    qtbot.addWidget(parent)
    setTheme(Theme.LIGHT, qapp)
    widget = IconWidget(BreezeIcon.HOME, parent)
    light = widget.pixmap().toImage()
    setTheme(Theme.DARK, qapp)
    assert widget.pixmap().toImage() != light
    assert widget.pixmap().toImage() == IconWidget(BreezeIcon.HOME, parent).pixmap().toImage()


def test_icon_widget_preserves_explicit_qicon(qapp, qtbot):
    source = BreezeIcon.HOME.icon(color="#ff0000")
    widget = IconWidget(source)
    qtbot.addWidget(widget)
    before = widget.icon().cacheKey()
    setTheme(Theme.LIGHT, qapp)
    assert widget.icon().cacheKey() == before
