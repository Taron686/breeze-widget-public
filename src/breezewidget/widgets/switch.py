from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Property, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QFontMetrics, QPainter, QPen
from PySide6.QtWidgets import QApplication, QCheckBox, QWidget

from ..constants import PROP_SWITCH, PROP_THEME_PILL
from ..icons import BreezeIcon, icon_from
from ..theme import Theme, getPalette, isDarkTheme, setTheme


def _clamp_unit(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _configure_thumb_animation(animation: QPropertyAnimation) -> None:
    animation.setDuration(180)
    animation.setEasingCurve(QEasingCurve.Type.OutCubic)


def _start_thumb_animation(animation: QPropertyAnimation, start: float, end: float) -> None:
    animation.stop()
    animation.setStartValue(start)
    animation.setEndValue(end)
    animation.start()


def _thumb_rect(track: QRectF, position: float, size: float, margin: float) -> QRectF:
    left_x = track.left() + margin
    right_x = track.right() - size - (margin - 1)
    thumb_x = left_x + (right_x - left_x) * position
    return QRectF(thumb_x, track.center().y() - size / 2, size, size)


_TRACK_WIDTH = 42
_TRACK_GAP = 8


class SwitchButton(QCheckBox):
    checkedChanged = Signal(bool)

    def hitButton(self, position) -> bool:
        return self.rect().contains(position)

    def __init__(self, text: str | QWidget = "", parent: QWidget | None = None):
        if isinstance(text, QWidget):
            parent = text
            text = ""
        super().__init__(text, parent)
        self.setProperty(PROP_SWITCH, True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(28)
        self._thumbPosition = 1.0 if self.isChecked() else 0.0
        self._animation = QPropertyAnimation(self, b"thumbPosition", self)
        _configure_thumb_animation(self._animation)
        self.toggled.connect(self._animateToggle)
        self.toggled.connect(self.checkedChanged.emit)
        self._stateLabelEnabled = True
        self._stateLabelPosition = "right"
        self._onText = "On"
        self._offText = "Off"

    def getThumbPosition(self) -> float:
        return self._thumbPosition

    def setThumbPosition(self, value: float) -> None:
        self._thumbPosition = _clamp_unit(value)
        self.update()

    thumbPosition = Property(float, getThumbPosition, setThumbPosition)

    def getStateLabelEnabled(self) -> bool:
        return self._stateLabelEnabled

    def setStateLabelEnabled(self, enabled: bool) -> None:
        enabled = bool(enabled)
        if enabled == self._stateLabelEnabled:
            return
        self._stateLabelEnabled = enabled
        self.updateGeometry()
        self.update()

    stateLabelEnabled = Property(bool, getStateLabelEnabled, setStateLabelEnabled)

    def getStateLabelPosition(self) -> str:
        return self._stateLabelPosition

    def setStateLabelPosition(self, position: str) -> None:
        normalized = str(position).lower()
        if normalized not in ("left", "right"):
            raise ValueError("stateLabelPosition must be 'left' or 'right'")
        if normalized == self._stateLabelPosition:
            return
        self._stateLabelPosition = normalized
        self.updateGeometry()
        self.update()

    stateLabelPosition = Property(str, getStateLabelPosition, setStateLabelPosition)

    def getOnText(self) -> str:
        return self._onText

    def setOnText(self, text: str) -> None:
        text = str(text)
        if text == self._onText:
            return
        self._onText = text
        self.updateGeometry()
        self.update()

    onText = Property(str, getOnText, setOnText)

    def getOffText(self) -> str:
        return self._offText

    def setOffText(self, text: str) -> None:
        text = str(text)
        if text == self._offText:
            return
        self._offText = text
        self.updateGeometry()
        self.update()

    offText = Property(str, getOffText, setOffText)

    def _currentStateText(self) -> str:
        return self._onText if self.isChecked() else self._offText

    def _stateLabelWidth(self) -> int:
        if not self._stateLabelEnabled:
            return 0
        metrics = QFontMetrics(self.font())
        return max(
            metrics.horizontalAdvance(self._onText),
            metrics.horizontalAdvance(self._offText),
        )

    def _trackLeft(self) -> float:
        if self._stateLabelEnabled and self._stateLabelPosition == "left":
            return self._stateLabelWidth() + _TRACK_GAP + 0.5
        return 0.5

    def _animateToggle(self, checked: bool) -> None:
        target = 1.0 if checked else 0.0
        _start_thumb_animation(self._animation, self._thumbPosition, target)
        if self._stateLabelEnabled:
            self.update()

    def setChecked(self, checked: bool) -> None:
        super().setChecked(checked)
        if self._animation.state() != QPropertyAnimation.State.Running:
            self._thumbPosition = 1.0 if checked else 0.0
            self.update()

    def sizeHint(self) -> QSize:
        metrics = QFontMetrics(self.font())
        text_width = metrics.horizontalAdvance(self.text())
        width = _TRACK_WIDTH + 4
        if self._stateLabelEnabled:
            width += self._stateLabelWidth() + _TRACK_GAP
        if self.text():
            width += _TRACK_GAP + text_width
        return QSize(width, 28)

    def paintEvent(self, event) -> None:
        del event
        palette = getPalette()
        enabled = self.isEnabled()
        position = self._thumbPosition

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        track = self._switchTrackRect()
        track_color, border_color, thumb_color, text_color = self._switchColors(
            palette,
            enabled,
            position,
        )

        self._drawSwitchTrack(painter, track, track_color, border_color)
        self._drawSwitchThumb(painter, track, position, thumb_color)
        self._drawSwitchLabels(painter, track, text_color)

        painter.end()

    def _switchTrackRect(self) -> QRectF:
        return QRectF(self._trackLeft(), (self.height() - 22) / 2, _TRACK_WIDTH, 22)

    def _switchColors(self, palette, enabled: bool, position: float) -> tuple[QColor, QColor, QColor, QColor]:
        track_color = _blend(QColor(palette.surface4), QColor(palette.primary4), position)
        border_color = _blend(QColor(palette.border1), QColor(palette.primary5), position)
        if not enabled:
            track_color = QColor(palette.surface3)
            border_color = QColor(palette.border1)

        thumb_color = _blend(QColor(palette.text2), QColor(palette.primary_text), position)
        text_color = QColor(palette.text1 if enabled else palette.text2)
        return track_color, border_color, thumb_color, text_color

    def _drawSwitchTrack(
        self,
        painter: QPainter,
        track: QRectF,
        track_color: QColor,
        border_color: QColor,
    ) -> None:
        painter.setPen(QPen(border_color, 1))
        painter.setBrush(track_color)
        painter.drawRoundedRect(track, 11, 11)

    def _drawSwitchThumb(
        self,
        painter: QPainter,
        track: QRectF,
        position: float,
        thumb_color: QColor,
    ) -> None:
        thumb_size = 14 + 2 * position
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(thumb_color)
        painter.drawEllipse(_thumb_rect(track, position, thumb_size, 4))

    def _drawSwitchLabels(self, painter: QPainter, track: QRectF, text_color: QColor) -> None:
        cursor_x = track.right() + _TRACK_GAP
        painter.setPen(text_color)

        if self._stateLabelEnabled:
            state_width = self._stateLabelWidth()
            if self._stateLabelPosition == "left":
                state_rect = QRectF(0, 0, state_width, self.height())
                cursor_x = track.right() + _TRACK_GAP
            else:
                state_rect = QRectF(cursor_x, 0, state_width, self.height())
                cursor_x += state_width + _TRACK_GAP
            painter.drawText(
                state_rect,
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                self._currentStateText(),
            )

        if self.text():
            painter.drawText(
                QRectF(cursor_x, 0, self.width() - cursor_x, self.height()),
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                self.text(),
            )


def _blend(start: QColor, end: QColor, t: float) -> QColor:
    t = max(0.0, min(1.0, float(t)))
    return QColor(
        int(round(start.red() + (end.red() - start.red()) * t)),
        int(round(start.green() + (end.green() - start.green()) * t)),
        int(round(start.blue() + (end.blue() - start.blue()) * t)),
        int(round(start.alpha() + (end.alpha() - start.alpha()) * t)),
    )


class BreezeThemeSwitch(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setProperty(PROP_THEME_PILL, True)
        self.setFixedSize(74, 32)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Theme wechseln")
        self._thumbPosition = 1.0 if isDarkTheme() else 0.0
        self._pendingTheme: Theme | None = None
        self._animation = QPropertyAnimation(self, b"thumbPosition", self)
        _configure_thumb_animation(self._animation)
        self._animation.finished.connect(self._finishThemeAnimation)

    def getThumbPosition(self) -> float:
        return self._thumbPosition

    def setThumbPosition(self, value: float) -> None:
        self._thumbPosition = _clamp_unit(value)
        self.update()

    thumbPosition = Property(float, getThumbPosition, setThumbPosition)

    def setThemeMode(self, theme: Theme) -> None:
        self._pendingTheme = theme
        _start_thumb_animation(
            self._animation,
            self._thumbPosition,
            1.0 if theme == Theme.DARK else 0.0,
        )

    def _finishThemeAnimation(self) -> None:
        if self._pendingTheme is None:
            return
        theme = self._pendingTheme
        self._pendingTheme = None
        setTheme(theme, QApplication.instance())
        self._thumbPosition = 1.0 if isDarkTheme() else 0.0
        self.update()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.setThemeMode(Theme.LIGHT if isDarkTheme() else Theme.DARK)
            event.accept()
            return
        super().mousePressEvent(event)

    def refreshTheme(self) -> None:
        if self._animation.state() != QPropertyAnimation.State.Running:
            self._thumbPosition = 1.0 if isDarkTheme() else 0.0
        self.update()

    def paintEvent(self, event) -> None:
        del event
        palette = getPalette()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        track = QRectF(0.5, 0.5, self.width() - 1, self.height() - 1)
        painter.setPen(QPen(QColor(palette.primary5), 1))
        painter.setBrush(QColor(palette.primary4))
        painter.drawRoundedRect(track, track.height() / 2, track.height() / 2)

        thumb_size = 26
        thumb_margin = 3
        thumb = QRectF(
            thumb_margin + (self.width() - thumb_size - thumb_margin * 2) * self._thumbPosition,
            thumb_margin,
            thumb_size,
            thumb_size,
        )
        painter.setPen(QPen(QColor(palette.primary4), 1))
        painter.setBrush(QColor(palette.chrome_bg))
        painter.drawEllipse(thumb)

        icon_color = QColor("#ffffff" if isDarkTheme() else "#000000")
        self._drawIcon(painter, BreezeIcon.SUN, icon_color, 18, self.height() / 2)
        self._drawIcon(painter, BreezeIcon.MOON, icon_color, self.width() - 18, self.height() / 2)
        painter.end()

    def _drawIcon(self, painter: QPainter, icon: BreezeIcon, color: QColor, cx: float, cy: float) -> None:
        size = 16
        rect = QRectF(cx - size / 2, cy - size / 2, size, size).toRect()
        icon_from(icon, color=color, size=size, stroke_width=1.6).paint(painter, rect)
