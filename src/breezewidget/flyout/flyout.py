"""Generic Flyout overlay — anchored popup with optional pointer arrow."""
from __future__ import annotations

from enum import Enum

from PySide6.QtCore import QEvent, QPoint, QRect, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QPolygonF
from PySide6.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget

from ..constants import PROP_FLYOUT
from ..theme import getPalette
from .animation import FlyoutAnimationType, make_show_animation


class FlyoutPlacement(str, Enum):
    """Where the flyout appears relative to its target."""

    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"


class Flyout(QWidget):
    """Anchored popup that hosts a single content widget.

    Lifecycle:
      * Construct with optional ``content``, ``target`` and ``parent``.
      * Call :meth:`exec` (or :meth:`showAt`) to display — the widget
        positions itself relative to its target, animates in, and
        installs an event filter on :class:`QApplication` so a click
        outside the popup dismisses it.
      * Emits :pyattr:`closed` when dismissed.

    The arrow tip is drawn as part of the rounded background and
    only painted when a target is set.
    """

    closed = Signal()

    _ARROW_SIZE = 9
    _RADIUS = 8
    _MIN_BODY_WIDTH = 220
    _MAX_BODY_WIDTH = 360

    def __init__(
        self,
        content: QWidget | None = None,
        target: QWidget | None = None,
        parent: QWidget | None = None,
        placement: FlyoutPlacement = FlyoutPlacement.BOTTOM,
        animation_type: FlyoutAnimationType = FlyoutAnimationType.SLIDE_DOWN,
    ):
        super().__init__(parent)
        self.setProperty(PROP_FLYOUT, True)
        flags = (
            Qt.WindowType.Popup
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.NoDropShadowWindowHint
        )
        if parent is None:
            flags |= Qt.WindowType.Window
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)

        self._target: QWidget | None = target
        self._placement = placement
        self._animation_type = animation_type
        self._show_animation = None
        self._content: QWidget | None = None

        self._outer = QHBoxLayout(self)
        self._outer.setSpacing(0)
        self._applyArrowMargin()

        self._body = QWidget(self)
        self._body.setMinimumWidth(self._MIN_BODY_WIDTH)
        self._body.setMaximumWidth(self._MAX_BODY_WIDTH)
        # Body has no background of its own — the rounded shape painted in
        # paintEvent on the Flyout itself acts as the visible surface,
        # otherwise the body would render a square opaque rectangle that
        # bleeds through the rounded corners.
        self._body.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._body.setStyleSheet("background: transparent;")
        self._body_layout = QVBoxLayout(self._body)
        self._body_layout.setContentsMargins(14, 12, 14, 12)
        self._body_layout.setSpacing(6)
        self._outer.addWidget(self._body)

        if content is not None:
            self.setContent(content)

    # --- public API -----------------------------------------------------

    def setTarget(self, target: QWidget | None) -> None:
        self._target = target
        self._applyArrowMargin()

    def target(self) -> QWidget | None:
        return self._target

    def placement(self) -> FlyoutPlacement:
        return self._placement

    def setPlacement(self, placement: FlyoutPlacement) -> None:
        self._placement = placement
        self._applyArrowMargin()

    def _applyArrowMargin(self) -> None:
        """Reserve transparent layout margin for the arrow + 1px border AA.

        A 1px gutter on every side ensures the 1px cosmetic border has
        whole-pixel room to render around the rounded body without
        getting clipped at the widget edge.  The arrow side gets that
        gutter plus the arrow size on top.
        """
        size = self._ARROW_SIZE
        gutter = 1
        if self._target is None:
            margins = (gutter, gutter, gutter, gutter)
        elif self._placement == FlyoutPlacement.BOTTOM:
            margins = (gutter, gutter + size, gutter, gutter)
        elif self._placement == FlyoutPlacement.TOP:
            margins = (gutter, gutter, gutter, gutter + size)
        elif self._placement == FlyoutPlacement.LEFT:
            margins = (gutter, gutter, gutter + size, gutter)
        else:  # RIGHT
            margins = (gutter + size, gutter, gutter, gutter)
        self._outer.setContentsMargins(*margins)

    def setContent(self, widget: QWidget) -> None:
        if self._content is not None:
            self._body_layout.removeWidget(self._content)
            self._content.setParent(None)
            self._content.deleteLater()
        self._content = widget
        widget.setParent(self._body)
        self._body_layout.addWidget(widget)

    def content(self) -> QWidget | None:
        return self._content

    def addContentLayout(self, layout) -> None:
        """Append a Qt layout to the body — used by subclasses."""
        self._body_layout.addLayout(layout)

    def exec(self) -> None:
        self.adjustSize()
        if self._target is not None:
            self._placeRelativeTo(self._target)
        QApplication.instance().installEventFilter(self)
        self.show()
        self._show_animation = make_show_animation(self, self._animation_type)
        if self._show_animation is not None:
            self._show_animation.start()

    showFlyout = exec  # alias

    def showAt(self, point: QPoint) -> None:
        self.adjustSize()
        self.move(point)
        QApplication.instance().installEventFilter(self)
        self.show()
        self._show_animation = make_show_animation(self, self._animation_type)
        if self._show_animation is not None:
            self._show_animation.start()

    # --- placement ------------------------------------------------------

    def _placeRelativeTo(self, target: QWidget) -> None:
        target_top_left = target.mapToGlobal(QPoint(0, 0))
        target_rect = QRect(target_top_left, target.size())
        size = self.size()
        if self._placement == FlyoutPlacement.BOTTOM:
            x = target_rect.center().x() - size.width() // 2
            y = target_rect.bottom() + 4
        elif self._placement == FlyoutPlacement.TOP:
            x = target_rect.center().x() - size.width() // 2
            y = target_rect.top() - size.height() - 4
        elif self._placement == FlyoutPlacement.LEFT:
            x = target_rect.left() - size.width() - 4
            y = target_rect.center().y() - size.height() // 2
        else:  # RIGHT
            x = target_rect.right() + 4
            y = target_rect.center().y() - size.height() // 2
        self.move(x, y)

    # --- event handling -------------------------------------------------

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            global_pos = event.globalPosition().toPoint() if hasattr(event, "globalPosition") else event.globalPos()
            if not self.geometry().contains(global_pos):
                self.close()
                return False
        return super().eventFilter(obj, event)

    def closeEvent(self, event) -> None:
        QApplication.instance().removeEventFilter(self)
        self.closed.emit()
        super().closeEvent(event)

    # --- painting -------------------------------------------------------

    def paintEvent(self, event) -> None:
        del event
        palette = getPalette()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # The outer layout already reserves a 1px gutter on every side
        # of the body so a 1px cosmetic border can render in full
        # without clipping.  Build a single rounded-body+arrow path and
        # paint it in one pass: fill *then* stroke the same shape so
        # the seam between body and arrow stays continuous.
        body_geo = self._body.geometry()
        path = QPainterPath()
        path.addRoundedRect(QRectF(body_geo), self._RADIUS, self._RADIUS)

        if self._target is not None:
            arrow = self._arrowPolygon(body_geo)
            if arrow is not None:
                arrow_path = QPainterPath()
                arrow_path.addPolygon(arrow)
                arrow_path.closeSubpath()
                path = path.united(arrow_path)

        pen = QPen(QColor(palette.border1), 1)
        pen.setCosmetic(True)
        painter.setPen(pen)
        painter.setBrush(QColor(palette.surface2))
        painter.drawPath(path)
        painter.end()

    def _arrowPolygon(self, body: QRect) -> QPolygonF | None:
        size = self._ARROW_SIZE
        cx = body.center().x()
        cy = body.center().y()
        if self._placement == FlyoutPlacement.BOTTOM:
            return QPolygonF([
                QPoint(cx - size, body.top()),
                QPoint(cx, body.top() - size),
                QPoint(cx + size, body.top()),
            ])
        if self._placement == FlyoutPlacement.TOP:
            return QPolygonF([
                QPoint(cx - size, body.bottom()),
                QPoint(cx, body.bottom() + size),
                QPoint(cx + size, body.bottom()),
            ])
        if self._placement == FlyoutPlacement.LEFT:
            return QPolygonF([
                QPoint(body.right(), cy - size),
                QPoint(body.right() + size, cy),
                QPoint(body.right(), cy + size),
            ])
        if self._placement == FlyoutPlacement.RIGHT:
            return QPolygonF([
                QPoint(body.left(), cy - size),
                QPoint(body.left() - size, cy),
                QPoint(body.left(), cy + size),
            ])
        return None
