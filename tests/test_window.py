from __future__ import annotations

from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtGui import QEnterEvent, QImage, QPixmap
from PySide6.QtTest import QSignalSpy
from PySide6.QtWidgets import QLabel, QWidget

from breezewidget import (
    BreezeIcon,
    BreezeTitleBar,
    BreezeWindow,
    MessageBox,
    MSBreezeWindow,
    NavigationItemPosition,
    SplitBreezeWindow,
    Theme,
    ThemeManager,
    getPalette,
    setTheme,
    setThemeColor,
)
from breezewidget.constants import (
    TITLE_BUTTON_ROLE_CLOSE,
    TITLE_BUTTON_ROLE_MAXIMIZE,
    TITLE_BUTTON_ROLE_MINIMIZE,
    TITLE_BUTTON_ROLE_RESTORE,
)


def test_breeze_window_constructs(qapp):
    window = BreezeWindow()
    assert window.titleBar is not None
    assert window.navigationInterface is not None
    assert window.stackedWidget is not None


def test_breeze_window_content_background_differs_from_navigation_and_has_rounded_corner(qapp, qtbot):
    manager = ThemeManager.instance()
    old_theme = manager.currentTheme
    old_accent = manager.accentColor
    old_stylesheet = qapp.styleSheet()
    try:
        setTheme(Theme.DARK, qapp)
        palette = getPalette()
        window = BreezeWindow()
        qtbot.addWidget(window)
        page = QWidget()
        page.setObjectName("home")
        window.addSubInterface(page, BreezeIcon.HOME, "Home")
        window.resize(500, 300)
        window.show()
        qapp.processEvents()

        image = QImage(window.size(), QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(Qt.GlobalColor.transparent)
        window.render(image)

        nav_pos = window.navigationInterface.mapTo(window, QPoint(20, 90))
        content_pos = window.stackedWidget.mapTo(window, QPoint(20, 90))
        content_corner_pos = window.stackedWidget.mapTo(window, QPoint(1, 1))
        content_gap_pos = window.contentHost.mapTo(window, QPoint(2, 4))

        assert image.pixelColor(nav_pos).name() == palette.surface1
        assert image.pixelColor(content_pos).name() == palette.surface2
        assert image.pixelColor(content_corner_pos).name() == palette.surface1
        assert image.pixelColor(content_gap_pos).name() == palette.surface1
        assert window.stackedWidget.geometry().top() == 8
        assert window.stackedWidget.geometry().left() == 6
        assert palette.surface1 != palette.surface2
    finally:
        setTheme(old_theme, qapp)
        setThemeColor(old_accent, qapp)
        qapp.setStyleSheet(old_stylesheet)


def test_titlebar_is_breeze_titlebar(qapp):
    window = BreezeWindow()
    assert isinstance(window.titleBar, BreezeTitleBar)
    assert window.titleBar.property("breezeTitleBar") is True


def test_add_sub_interface_registers_route(qapp):
    window = BreezeWindow()
    page = QLabel("hello")
    page.setObjectName("home")
    window.addSubInterface(page, BreezeIcon.HOME, "Home")
    assert window.stackedWidget.count() == 1
    assert window.navigationInterface.currentItem() == "home"


def test_switch_to_changes_current_page(qapp):
    window = BreezeWindow()

    page_a = QLabel("A"); page_a.setObjectName("a")
    page_b = QLabel("B"); page_b.setObjectName("b")
    window.addSubInterface(page_a, BreezeIcon.HOME, "A")
    window.addSubInterface(page_b, BreezeIcon.SETTINGS, "B")

    window.switchTo("b")
    assert window.stackedWidget.currentWidget() is page_b
    assert window.navigationInterface.currentItem() == "b"


def test_navigation_click_emits_current_item_changed_once(qapp):
    window = BreezeWindow()

    page_a = QLabel("A"); page_a.setObjectName("a")
    page_b = QLabel("B"); page_b.setObjectName("b")
    window.addSubInterface(page_a, BreezeIcon.HOME, "A")
    window.addSubInterface(page_b, BreezeIcon.SETTINGS, "B")

    spy = QSignalSpy(window.navigationInterface.currentItemChanged)
    window.navigationInterface.item("b").click()
    qapp.processEvents()

    assert spy.count() == 1
    assert spy.at(0) == ["b"]
    assert window.router.current() == "b"


def test_switch_to_widget_reference(qapp):
    window = BreezeWindow()
    page = QLabel("x"); page.setObjectName("x")
    window.addSubInterface(page, BreezeIcon.HOME, "X")
    window.switchTo(page)
    assert window.stackedWidget.currentWidget() is page


def test_navigation_compact_toggle_via_window(qapp):
    window = BreezeWindow()
    window.setNavigationCompact(True)
    assert window.navigationInterface.isCompact() is True
    window.toggleNavigation(animated=False)
    assert window.navigationInterface.isCompact() is False


def test_titlebar_back_button_visibility(qapp):
    window = BreezeWindow()
    window.enableNavigationMenuButton(True)
    assert window.titleBar.backButton.isVisible() is True or window.titleBar.backButton.isVisibleTo(window.titleBar)


def test_titlebar_add_action_button(qapp):
    window = BreezeWindow()
    button = window.titleBar.addActionButton(BreezeIcon.SEARCH, "search")
    assert button.property("breezeTitleButton") is True


def test_titlebar_caption_buttons_are_custom_painted(qapp):
    window = BreezeWindow()

    assert type(window.titleBar.minButton).__name__ == "_CaptionButton"
    assert type(window.titleBar.maxButton).__name__ == "_CaptionButton"
    assert type(window.titleBar.closeButton).__name__ == "_CaptionButton"
    assert window.titleBar.minButton.property("_breezeCaptionRole") == TITLE_BUTTON_ROLE_MINIMIZE
    assert window.titleBar.maxButton.property("_breezeCaptionRole") == TITLE_BUTTON_ROLE_MAXIMIZE
    assert window.titleBar.closeButton.property("_breezeCaptionRole") == TITLE_BUTTON_ROLE_CLOSE


def test_titlebar_sync_window_state_updates_caption_role(qapp):
    window = BreezeWindow()

    window.show()
    window.showMaximized()
    qapp.processEvents()
    window.titleBar.syncWindowState()
    assert window.titleBar.maxButton.property("_breezeCaptionRole") == TITLE_BUTTON_ROLE_RESTORE

    window.showNormal()
    qapp.processEvents()
    window.titleBar.syncWindowState()
    assert window.titleBar.maxButton.property("_breezeCaptionRole") == TITLE_BUTTON_ROLE_MAXIMIZE


def test_titlebar_caption_glyphs_are_centered(qapp):
    setTheme(Theme.LIGHT, qapp)
    window = BreezeWindow()
    window.show()

    for button in (window.titleBar.minButton, window.titleBar.maxButton, window.titleBar.closeButton):
        bounds = _opaque_bounds(_render_widget(button))
        assert bounds is not None
        min_x, min_y, max_x, max_y = bounds
        assert 14 <= min_x <= 20
        assert 25 <= max_x <= 32
        assert 13 <= min_y <= 20
        assert 20 <= max_y <= 27


def test_titlebar_close_hover_uses_danger_background(qapp, qtbot):
    setTheme(Theme.LIGHT, qapp)
    window = BreezeWindow()
    qtbot.addWidget(window)
    window.show()
    qtbot.waitExposed(window)

    close_button = window.titleBar.closeButton
    # Offscreen mouse moves can miss Enter when a previous test left the
    # cursor at this position. Deliver the hover event explicitly.
    position = close_button.rect().center()
    qapp.sendEvent(close_button, QEnterEvent(
        QPointF(position), QPointF(close_button.mapTo(window, position)),
        QPointF(close_button.mapToGlobal(position)),
    ))
    assert close_button.underMouse()

    image = _render_widget(close_button)
    assert _count_pixels(image, lambda c: c.red() > 150 and c.green() < 80 and c.blue() < 80 and c.alpha() > 200) > 20
    assert _count_pixels(image, lambda c: c.red() > 220 and c.green() > 220 and c.blue() > 220 and c.alpha() > 100) > 0


def test_titlebar_add_widget(qapp):
    window = BreezeWindow()
    custom = QWidget()
    returned = window.titleBar.addWidget(custom)
    assert returned is custom


def test_ms_and_split_breeze_window_construct(qapp):
    from PySide6.QtWidgets import QMainWindow

    ms = MSBreezeWindow()
    # Phase 5: MS is no longer a BreezeWindow subclass; it has its own
    # top-pivot layout. It still inherits QMainWindow so the public
    # window contract holds.
    assert isinstance(ms, QMainWindow)
    assert hasattr(ms, "pivot")
    split = SplitBreezeWindow()
    assert isinstance(split, QMainWindow)
    assert hasattr(split, "splitter")


def test_message_box_constructs(qapp):
    box = MessageBox("Title", "Body")
    assert box.windowTitle() == "Title"
    assert box.isModal() is True
    assert box.yesButton is not None
    assert box.cancelButton is not None


def _render_widget(widget) -> object:
    pixmap = QPixmap(widget.size())
    pixmap.fill(Qt.GlobalColor.transparent)
    widget.render(pixmap)
    return pixmap.toImage()


def _opaque_bounds(image) -> tuple[int, int, int, int] | None:
    points = [
        (x, y)
        for y in range(image.height())
        for x in range(image.width())
        if image.pixelColor(x, y).alpha() > 32
    ]
    if not points:
        return None
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)


def _count_pixels(image, predicate) -> int:
    return sum(
        1
        for y in range(image.height())
        for x in range(image.width())
        if predicate(image.pixelColor(x, y))
    )
