"""Compact status indicators (count, dot, icon).

Badges are small chips that sit next to a host widget to draw attention to
a piece of state — an unread count, an attention dot, a status icon.
The visual variant is selected via the :data:`breezewidget.constants.PROP_BADGE`
dynamic property so downstream code can theme custom badges through QSS.
"""
from __future__ import annotations

from typing import Any

from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QFontMetrics, QPainter, QPen
from PySide6.QtWidgets import QLabel, QWidget

from ..constants import (
    BADGE_ATTENTION,
    BADGE_DANGER,
    BADGE_DEFAULT,
    BADGE_INFO,
    BADGE_SUCCESS,
    BADGE_WARNING,
    PROP_BADGE,
)
from ..icons import icon_from
from ..icons._themed import default_icon_color
from ..theme import getPalette


class _BadgeBase(QWidget):
    """Common painting code for round/pill count badges."""

    def __init__(self, variant: str, parent: QWidget | None = None):
        super().__init__(parent)
        self._variant = variant
        self.setProperty(PROP_BADGE, variant)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setMinimumSize(QSize(8, 8))

    @property
    def variant(self) -> str:
        return self._variant

    def setVariant(self, variant: str) -> None:
        self._variant = variant
        self.setProperty(PROP_BADGE, variant)
        self.update()

    def _backgroundColor(self) -> QColor:
        palette = getPalette()
        return QColor({
            BADGE_DEFAULT: palette.surface5,
            BADGE_INFO: palette.primary4,
            BADGE_SUCCESS: "#0f7b0f" if not self._isDark() else "#6ccb5f",
            BADGE_ATTENTION: palette.primary4,
            BADGE_WARNING: "#9d5d00" if not self._isDark() else "#fce100",
            BADGE_DANGER: palette.danger1,
        }.get(self._variant, palette.primary4))

    def _foregroundColor(self) -> QColor:
        palette = getPalette()
        if self._variant == BADGE_DEFAULT:
            return QColor(palette.text1)
        if self._variant == BADGE_WARNING and self._isDark():
            return QColor("#1a1a1a")
        return QColor(palette.primary_text)

    @staticmethod
    def _isDark() -> bool:
        from ..theme import isDarkTheme
        return isDarkTheme()


class InfoBadge(_BadgeBase):
    """Pill-shaped badge that displays a small text/number."""

    def __init__(
        self,
        text: str = "",
        parent: QWidget | None = None,
        variant: str = BADGE_INFO,
    ):
        super().__init__(variant, parent)
        self._text = str(text)
        self._padding_h = 6
        self._min_diameter = 18
        self.setMinimumHeight(self._min_diameter)

    def text(self) -> str:
        return self._text

    def setText(self, text: str) -> None:
        self._text = str(text)
        self.updateGeometry()
        self.update()

    @classmethod
    def info(cls, text: str = "", parent: QWidget | None = None) -> "InfoBadge":
        return cls(text, parent, BADGE_INFO)

    @classmethod
    def success(cls, text: str = "", parent: QWidget | None = None) -> "InfoBadge":
        return cls(text, parent, BADGE_SUCCESS)

    @classmethod
    def attention(cls, text: str = "", parent: QWidget | None = None) -> "InfoBadge":
        return cls(text, parent, BADGE_ATTENTION)

    @classmethod
    def warning(cls, text: str = "", parent: QWidget | None = None) -> "InfoBadge":
        return cls(text, parent, BADGE_WARNING)

    @classmethod
    def error(cls, text: str = "", parent: QWidget | None = None) -> "InfoBadge":
        return cls(text, parent, BADGE_DANGER)

    @classmethod
    def custom(
        cls,
        text: str = "",
        parent: QWidget | None = None,
        variant: str = BADGE_DEFAULT,
    ) -> "InfoBadge":
        return cls(text, parent, variant)

    def sizeHint(self) -> QSize:
        metrics = QFontMetrics(self.font())
        text_width = metrics.horizontalAdvance(self._text) if self._text else 0
        height = max(self._min_diameter, metrics.height() + 2)
        if not self._text:
            return QSize(height, height)
        return QSize(max(height, text_width + self._padding_h * 2), height)

    def paintEvent(self, event) -> None:
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        rect = QRectF(0.5, 0.5, self.width() - 1, self.height() - 1)
        radius = rect.height() / 2
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._backgroundColor())
        painter.drawRoundedRect(rect, radius, radius)

        if self._text:
            painter.setPen(QPen(self._foregroundColor()))
            painter.drawText(
                self.rect(),
                Qt.AlignmentFlag.AlignCenter,
                self._text,
            )
        painter.end()


class DotInfoBadge(_BadgeBase):
    """Small filled circle — pure attention indicator without text."""

    def __init__(
        self,
        parent: QWidget | None = None,
        variant: str = BADGE_ATTENTION,
        diameter: int = 10,
    ):
        super().__init__(variant, parent)
        self._diameter = max(4, int(diameter))
        self.setFixedSize(self._diameter, self._diameter)

    def setDiameter(self, diameter: int) -> None:
        self._diameter = max(4, int(diameter))
        self.setFixedSize(self._diameter, self._diameter)
        self.update()

    def diameter(self) -> int:
        return self._diameter

    def paintEvent(self, event) -> None:
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._backgroundColor())
        painter.drawEllipse(QRectF(0.5, 0.5, self.width() - 1, self.height() - 1))
        painter.end()


class IconInfoBadge(QLabel):
    """Tinted icon badge — render any :class:`BreezeIcon` as a status chip."""

    def __init__(
        self,
        icon: Any,
        parent: QWidget | None = None,
        variant: str = BADGE_INFO,
        size: int = 16,
    ):
        super().__init__(parent)
        self._icon = icon
        self._size = max(8, int(size))
        self._variant = variant
        self.setProperty(PROP_BADGE, variant)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._refresh()

    @property
    def variant(self) -> str:
        return self._variant

    def setVariant(self, variant: str) -> None:
        self._variant = variant
        self.setProperty(PROP_BADGE, variant)
        self._refresh()

    def setIcon(self, icon: Any) -> None:
        self._icon = icon
        self._refresh()

    def setIconSize(self, size: int) -> None:
        self._size = max(8, int(size))
        self._refresh()

    def refreshTheme(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        palette = getPalette()
        color = QColor({
            BADGE_DEFAULT: default_icon_color(),
            BADGE_INFO: palette.primary4,
            BADGE_SUCCESS: "#0f7b0f",
            BADGE_ATTENTION: palette.primary4,
            BADGE_WARNING: "#9d5d00",
            BADGE_DANGER: palette.danger1,
        }.get(self._variant, palette.primary4))
        pixmap = icon_from(self._icon, color=color, size=self._size).pixmap(self._size, self._size)
        self.setPixmap(pixmap)
        self.setFixedSize(self._size + 4, self._size + 4)
