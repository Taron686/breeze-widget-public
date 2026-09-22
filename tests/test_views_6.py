"""Smoke tests for Phase 6: Daten-Views & Media."""
from __future__ import annotations

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPixmap, QStandardItem, QStandardItemModel
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtWidgets import QLineEdit, QStyle, QStyleOptionViewItem, QTableWidgetItem

from breezewidget import (
    Avatar,
    CycleListWidget,
    FlipView,
    ListView,
    MediaPlayer,
    PlayBar,
    Theme,
    TableItemDelegate,
    TableView,
    TableWidget,
    TreeView,
    VideoWidget,
    getPalette,
    setTheme,
    setThemeColor,
)


def _solid_pixmap(color: str, size: int = 64) -> QPixmap:
    pm = QPixmap(size, size)
    pm.fill(QColor(color))
    return pm


def _close_color(color: QColor, expected: QColor, tolerance: int = 3) -> bool:
    return (
        color.alpha() > 200
        and abs(color.red() - expected.red()) <= tolerance
        and abs(color.green() - expected.green()) <= tolerance
        and abs(color.blue() - expected.blue()) <= tolerance
    )


def _count_pixels(image: QImage, predicate) -> int:
    return sum(
        1
        for y in range(image.height())
        for x in range(image.width())
        if predicate(image.pixelColor(x, y))
    )


# ---------------------------------------------------------------------------
# Item views
# ---------------------------------------------------------------------------

def test_list_view_constructs(qapp):
    view = ListView()
    assert view.property("breezeItemView") == "list"
    assert view.alternatingRowColors() is True


def test_table_view_hides_vertical_header(qapp):
    view = TableView()
    assert view.property("breezeItemView") == "table"
    assert view.showGrid() is False
    assert isinstance(view.itemDelegate(), TableItemDelegate)
    assert view.verticalHeader().isVisible() is False


def test_table_widget_has_border_helpers(qapp):
    table = TableWidget()
    assert table.property("breezeItemView") == "tableWidget"
    assert table.showGrid() is False
    assert isinstance(table.itemDelegate(), TableItemDelegate)
    table.setBorderVisible(False)
    assert table.frameShape() == table.Shape.NoFrame
    table.setBorderVisible(True)
    assert table.frameShape() == table.Shape.StyledPanel
    table.setBorderRadius(12)
    assert table.borderRadius() == 12
    assert table.property("_breezeTableRadius") == 12


def test_table_item_delegate_constructs(qapp):
    table = TableWidget()
    delegate = TableItemDelegate(table)
    table.setItemDelegate(delegate)
    assert table.itemDelegate() is delegate


def test_table_widget_current_cell_uses_theme_accent(qapp, qtbot):
    setTheme(Theme.DARK, qapp)
    setThemeColor("#11d9f3", qapp)
    accent = QColor(getPalette().primary4)

    table = TableWidget()
    qtbot.addWidget(table)
    table.setRowCount(2)
    table.setColumnCount(2)
    table.setHorizontalHeaderLabels(["Mo", "Di"])
    table.setItem(0, 0, QTableWidgetItem("kl"))
    table.setCurrentCell(0, 0)
    table.resize(260, 140)
    table.show()
    qtbot.waitExposed(table)
    qapp.processEvents()

    image = QImage(table.size(), QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    table.render(image)

    assert _count_pixels(
        image,
        lambda color: _close_color(color, accent),
    ) > 8


def test_table_view_current_cell_uses_theme_accent(qapp, qtbot):
    setTheme(Theme.DARK, qapp)
    setThemeColor("#11d9f3", qapp)
    accent = QColor(getPalette().primary4)

    table = TableView()
    qtbot.addWidget(table)
    model = QStandardItemModel(0, 2, table)
    model.setHorizontalHeaderLabels(["Name", "Status"])
    model.appendRow([QStandardItem("Deploy"), QStandardItem("Pending")])
    table.setModel(model)
    table.setCurrentIndex(model.index(0, 0))
    table.resize(260, 120)
    table.show()
    qtbot.waitExposed(table)
    qapp.processEvents()

    image = QImage(table.size(), QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    table.render(image)

    assert _count_pixels(
        image,
        lambda color: _close_color(color, accent),
    ) > 8


def test_table_item_editor_uses_theme_accent(qapp):
    setTheme(Theme.DARK, qapp)
    setThemeColor("#23a6d5", qapp)
    table = TableWidget()
    table.setRowCount(1)
    table.setColumnCount(1)
    table.setItem(0, 0, QTableWidgetItem("kl"))

    index = table.model().index(0, 0)
    editor = table.itemDelegate().createEditor(table, QStyleOptionViewItem(), index)

    assert isinstance(editor, QLineEdit)
    assert getPalette().primary4 in editor.styleSheet()


def test_table_item_delegate_skips_cell_text_while_editing(qapp):
    setTheme(Theme.DARK, qapp)
    table = TableWidget()
    table.setRowCount(1)
    table.setColumnCount(1)
    table.setItem(0, 0, QTableWidgetItem("jkl"))
    table.setCurrentCell(0, 0)

    option = QStyleOptionViewItem()
    option.widget = table
    option.rect = QRect(0, 0, 120, 40)
    option.state = (
        QStyle.StateFlag.State_Enabled
        | QStyle.StateFlag.State_Selected
        | QStyle.StateFlag.State_Editing
    )

    image = QImage(option.rect.size(), QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    table.itemDelegate().paint(painter, option, table.model().index(0, 0))
    painter.end()

    text_color = QColor(getPalette().text1)
    assert _count_pixels(image, lambda color: _close_color(color, text_color)) < 8


def test_tree_view_animated(qapp):
    view = TreeView()
    assert view.property("breezeItemView") == "tree"
    assert view.isAnimated() is True


def test_list_view_accepts_model(qapp):
    view = ListView()
    model = QStandardItemModel()
    view.setModel(model)
    assert view.model() is model


def test_list_view_selection_does_not_fill_with_theme_accent(qapp, qtbot):
    setTheme(Theme.DARK, qapp)
    setThemeColor("#11d9f3", qapp)
    accent = QColor(getPalette().primary4)

    view = ListView()
    qtbot.addWidget(view)
    model = QStandardItemModel()
    for text in ["Apple", "Banana", "Cherry", "Date"]:
        model.appendRow(QStandardItem(text))
    view.setModel(model)
    view.setCurrentIndex(model.index(3, 0))
    view.resize(260, 140)
    view.show()
    qtbot.waitExposed(view)
    qapp.processEvents()

    image = QImage(view.size(), QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    view.render(image)

    assert _count_pixels(
        image,
        lambda color: _close_color(color, accent),
    ) < 120


# ---------------------------------------------------------------------------
# FlipView
# ---------------------------------------------------------------------------

def test_flip_view_starts_empty(qapp):
    view = FlipView()
    assert view.count() == 0
    assert view.currentIndex() == -1 or view.currentIndex() == 0


def test_flip_view_add_pixmaps(qapp):
    view = FlipView()
    idx0 = view.addPixmap(_solid_pixmap("#ff0000"))
    idx1 = view.addPixmap(_solid_pixmap("#00ff00"))
    assert idx0 == 0
    assert idx1 == 1
    assert view.count() == 2


def test_flip_view_next_previous(qapp, qtbot):
    view = FlipView()
    view.addPixmap(_solid_pixmap("#ff0000"))
    view.addPixmap(_solid_pixmap("#00ff00"))
    view.addPixmap(_solid_pixmap("#0000ff"))
    view.setCurrentIndex(0, animate=False)
    with qtbot.waitSignal(view.currentChanged, timeout=500) as sig:
        view.next()
    assert sig.args == [1]
    assert view.currentIndex() == 1
    view.previous()
    assert view.currentIndex() == 0


def test_flip_view_button_state(qapp):
    view = FlipView()
    view.addPixmap(_solid_pixmap("#ff0000"))
    view.addPixmap(_solid_pixmap("#00ff00"))
    view.setCurrentIndex(0, animate=False)
    assert view._prevButton.isEnabled() is False
    assert view._nextButton.isEnabled() is True


def test_flip_view_set_pixmaps_replaces(qapp):
    view = FlipView()
    view.addPixmap(_solid_pixmap("#ff0000"))
    view.setPixmaps([_solid_pixmap("#000000"), _solid_pixmap("#ffffff")])
    assert view.count() == 2


# ---------------------------------------------------------------------------
# CycleListWidget
# ---------------------------------------------------------------------------

def test_cycle_list_initial_items(qapp):
    cycle = CycleListWidget(["A", "B", "C"])
    assert cycle.count() == 3
    assert cycle.currentRow() == 0


def test_cycle_list_step_next_wraps(qapp, qtbot):
    cycle = CycleListWidget(["A", "B", "C"])
    cycle.setCurrentRow(2)
    with qtbot.waitSignal(cycle.cycled, timeout=500) as sig:
        cycle.stepNext()
    assert sig.args == [0]
    assert cycle.currentRow() == 0


def test_cycle_list_step_previous_wraps(qapp, qtbot):
    cycle = CycleListWidget(["A", "B", "C"])
    cycle.setCurrentRow(0)
    with qtbot.waitSignal(cycle.cycled, timeout=500) as sig:
        cycle.stepPrevious()
    assert sig.args == [2]
    assert cycle.currentRow() == 2


def test_cycle_list_step_no_signal_without_wrap(qapp):
    cycle = CycleListWidget(["A", "B", "C"])
    cycle.setCurrentRow(0)
    fired: list[int] = []
    cycle.cycled.connect(fired.append)
    cycle.stepNext()
    assert fired == []
    assert cycle.currentRow() == 1


def test_cycle_list_arrow_keys(qapp, qtbot):
    cycle = CycleListWidget(["A", "B", "C"])
    cycle.setCurrentRow(0)
    qtbot.keyClick(cycle, Qt.Key.Key_Down)
    assert cycle.currentRow() == 1


# ---------------------------------------------------------------------------
# Avatar
# ---------------------------------------------------------------------------

def test_avatar_default_diameter(qapp):
    avatar = Avatar(40, name="Alice")
    assert avatar.diameter() == 40
    assert avatar.size().width() == 40
    assert avatar.name() == "Alice"


def test_avatar_set_pixmap(qapp):
    avatar = Avatar(40)
    pm = _solid_pixmap("#1f6feb")
    avatar.setPixmap(pm)
    assert avatar.pixmap() is pm


def test_avatar_resize(qapp):
    avatar = Avatar(40)
    avatar.setDiameter(64)
    assert avatar.diameter() == 64
    assert avatar.size().width() == 64


def test_avatar_paints_without_error(qapp, qtbot):
    avatar = Avatar(64, name="Bob")
    avatar.show()
    qtbot.waitExposed(avatar)
    avatar.update()


# ---------------------------------------------------------------------------
# Media
# ---------------------------------------------------------------------------

def test_media_player_constructs(qapp):
    mp = MediaPlayer()
    assert mp.player() is not None
    assert mp.audioOutput() is not None
    assert mp.hasMedia() is False


def test_media_player_volume_clamps(qapp):
    mp = MediaPlayer()
    mp.setVolume(2.0)
    assert mp.volume() <= 1.0
    mp.setVolume(-1.0)
    assert mp.volume() >= 0.0


def test_media_player_state_initial(qapp):
    mp = MediaPlayer()
    assert mp.playbackState() == QMediaPlayer.PlaybackState.StoppedState


def test_play_bar_binds_player(qapp):
    mp = MediaPlayer()
    bar = PlayBar(mp)
    assert bar.mediaPlayer() is mp
    # Volume slider reflects player volume.
    assert bar.volumeSlider.value() == int(mp.volume() * 100)


def test_play_bar_volume_changes_player(qapp):
    mp = MediaPlayer()
    bar = PlayBar(mp)
    bar.volumeSlider.setValue(50)
    assert abs(mp.volume() - 0.5) < 0.01


def test_play_bar_mute_toggle(qapp):
    mp = MediaPlayer()
    bar = PlayBar(mp)
    bar.muteButton.setChecked(True)
    assert mp.isMuted() is True
    bar.muteButton.setChecked(False)
    assert mp.isMuted() is False


def test_video_widget_constructs(qapp):
    video = VideoWidget()
    assert video.property("breezeVideoWidget") is True


def test_media_demo_embeds_video_widget_in_host(qapp):
    from examples.widget_demo_pages.media import MediaDemoPage

    page = MediaDemoPage()
    videos = page.findChildren(VideoWidget)

    assert len(videos) == 1
    assert videos[0].parentWidget() is not page
    assert videos[0].isHidden()
