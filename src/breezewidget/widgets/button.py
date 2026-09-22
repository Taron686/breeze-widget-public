from __future__ import annotations

from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QColor, QDesktopServices, QPainter
from PySide6.QtWidgets import QHBoxLayout, QMenu, QPushButton, QToolButton, QWidget

from ..constants import PROP_PILL, PROP_ROLE, ROLE_PRIMARY, ROLE_TRANSPARENT
from ..icons._themed import ThemedIcon, default_icon_color, primary_icon_color
from ..theme import getPalette
from ._base import _BreezeWidgetMixin
from ._chevron import paint_chevron


class PushButton(QPushButton, _BreezeWidgetMixin):
    def __init__(self, text: str = "", parent: QWidget | None = None, icon=None):
        super().__init__(str(text), parent)
        self._themedIcon = ThemedIcon(
            lambda rendered: QPushButton.setIcon(self, rendered),
            color=lambda: primary_icon_color() if self.property(PROP_ROLE) == ROLE_PRIMARY else default_icon_color(),
        )
        if icon is not None:
            self.setIcon(icon)
        self._finish()

    def setIcon(self, icon) -> None:  # type: ignore[override]
        self._themedIcon.set(icon)

    def refreshTheme(self) -> None:
        self._themedIcon.refresh()


class PrimaryPushButton(PushButton):
    def __init__(self, text: str = "", parent: QWidget | None = None, icon=None):
        super().__init__(text, parent, icon)
        self.setProperty(PROP_ROLE, ROLE_PRIMARY)
        self.refreshTheme()


class PillPushButton(PushButton):
    """Pill-shaped push button.

    Toggle-able (``setCheckable(True)``) with two visual states:
    * unchecked → transparent surface, palette border
    * checked   → accent fill, ``palette.primary_text`` foreground

    Constructors mirror PyQt-Fluent-Widgets:

        PillPushButton("Tag")
        PillPushButton("Tag", parent)
        PillPushButton(BreezeIcon.ADD, "Tag")
        PillPushButton(BreezeIcon.ADD, "Tag", parent)
    """

    PILL_HEIGHT = 36

    def __init__(self, *args, parent: QWidget | None = None, icon=None, text: str | None = None):
        resolved_text, resolved_parent, resolved_icon = _resolve_button_args(
            args, parent=parent, icon=icon, text=text
        )
        super().__init__(resolved_text, resolved_parent, icon=None)
        self._themedIcon = ThemedIcon(
            lambda rendered: QPushButton.setIcon(self, rendered),
            color=lambda: primary_icon_color() if self.isChecked() else default_icon_color(),
        )
        self.setProperty(PROP_PILL, "true")
        self.setCheckable(True)
        self.setFixedHeight(self.PILL_HEIGHT)
        self.toggled.connect(lambda _checked: self.refreshTheme())
        self.setIcon(resolved_icon)
        self.style().unpolish(self)
        self.style().polish(self)

def _resolve_button_args(
    args: tuple,
    *,
    parent: QWidget | None = None,
    icon=None,
    text: str | None = None,
) -> tuple[str, QWidget | None, object]:
    """Accept either ``(text, parent, icon)`` or ``(icon, text, parent)`` positional forms."""
    resolved_text = text if text is not None else ""
    resolved_parent = parent
    resolved_icon = icon
    if args:
        first = args[0]
        is_text_first = type(first) is str
        if is_text_first:
            resolved_text = first
            if len(args) > 1:
                resolved_parent = args[1]
            if len(args) > 2 and resolved_icon is None:
                resolved_icon = args[2]
        else:
            if resolved_icon is None:
                resolved_icon = first
            if len(args) > 1 and isinstance(args[1], str):
                resolved_text = args[1]
            if len(args) > 2:
                resolved_parent = args[2]
    return resolved_text, resolved_parent, resolved_icon


class TransparentPushButton(PushButton):
    def __init__(self, text: str = "", parent: QWidget | None = None, icon=None):
        super().__init__(text, parent, icon)
        self.setProperty(PROP_ROLE, ROLE_TRANSPARENT)


class ToggleButton(PushButton):
    def __init__(self, text: str = "", parent: QWidget | None = None, icon=None):
        super().__init__(text, parent, icon)
        self.setCheckable(True)


class HyperlinkButton(TransparentPushButton):
    def __init__(self, url: str, text: str | None = None, parent: QWidget | None = None, icon=None):
        super().__init__(text or url, parent, icon)
        self.url = url
        self.clicked.connect(self._open_url)

    def _open_url(self) -> None:
        QDesktopServices.openUrl(QUrl(self.url))


class DropDownPushButton(PushButton):
    _CHEVRON_SLOT = 22

    def __init__(
        self,
        text: str = "",
        parent: QWidget | None = None,
        icon=None,
        menu: QMenu | None = None,
    ):
        super().__init__(text, parent, icon)
        self.setMenu(menu or QMenu(self))
        margins = self.contentsMargins()
        margins.setRight(self._CHEVRON_SLOT)
        self.setContentsMargins(margins)

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        palette = getPalette()
        is_primary = self.property(PROP_ROLE) == ROLE_PRIMARY
        color = QColor(palette.primary_text if is_primary else default_icon_color())
        if not self.isEnabled():
            color = QColor(palette.text2)
        cx = self.width() - self._CHEVRON_SLOT / 2
        cy = self.height() / 2
        paint_chevron(
            painter,
            cx=cx,
            cy=cy,
            half_size=5.0,
            color=color,
            stroke_width=1.5,
            direction="down",
        )
        painter.end()


class SplitPushButton(QWidget):
    clicked = Signal()

    def __init__(
        self,
        text: str = "",
        parent: QWidget | None = None,
        icon=None,
        menu: QMenu | None = None,
    ):
        super().__init__(parent)
        self._button = PushButton(text, self, icon)
        self._menuButton = ToolButton(None, self)
        self._menuButton.setIcon("chevron-down")
        self._menuButton.setFixedWidth(34)
        self._menu = menu or QMenu(self)
        self._button.clicked.connect(lambda checked=False: self.clicked.emit())
        self._menuButton.clicked.connect(self.showMenu)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.addWidget(self._button)
        layout.addWidget(self._menuButton)

    def setMenu(self, menu: QMenu) -> None:
        self._menu = menu

    def menu(self) -> QMenu:
        return self._menu

    def showMenu(self) -> None:
        # Re-parent the menu to the top-level window before popping it
        # up — Qt's QMenu expects its widget-window chain to reach a
        # real top-level widget, otherwise it logs
        # ``QWidgetWindow(...) must be a top level window`` and the
        # popup misbehaves on subsequent activations.
        top = self.window()
        if top is not None and self._menu.parent() is not top:
            self._menu.setParent(top)
            self._menu.setWindowFlag(Qt.WindowType.Popup, True)
        self._menu.popup(self._menuButton.mapToGlobal(self._menuButton.rect().bottomLeft()))

    def setText(self, text: str) -> None:
        self._button.setText(text)

    def text(self) -> str:
        return self._button.text()

    def setIcon(self, icon) -> None:
        self._button.setIcon(icon)

    def setEnabled(self, enabled: bool) -> None:
        super().setEnabled(enabled)
        self._button.setEnabled(enabled)
        self._menuButton.setEnabled(enabled)


class ToolButton(QToolButton, _BreezeWidgetMixin):
    def __init__(self, icon=None, parent: QWidget | None = None):
        super().__init__(parent)
        self._themedIcon = ThemedIcon(
            lambda rendered: QToolButton.setIcon(self, rendered),
            color=lambda: primary_icon_color() if self.property(PROP_ROLE) == ROLE_PRIMARY else default_icon_color(),
        )
        if icon is not None:
            self.setIcon(icon)
        self._finish()

    def setIcon(self, icon) -> None:  # type: ignore[override]
        self._themedIcon.set(icon)

    def refreshTheme(self) -> None:
        self._themedIcon.refresh()


class PrimaryToolButton(ToolButton):
    def __init__(self, icon=None, parent: QWidget | None = None):
        super().__init__(icon, parent)
        self.setProperty(PROP_ROLE, ROLE_PRIMARY)
        self.refreshTheme()


class TransparentToolButton(ToolButton):
    def __init__(self, icon=None, parent: QWidget | None = None):
        super().__init__(icon, parent)
        self.setProperty(PROP_ROLE, ROLE_TRANSPARENT)
        self.refreshTheme()
