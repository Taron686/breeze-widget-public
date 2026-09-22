"""FlipView — image carousel with previous/next animation."""
from __future__ import annotations

from typing import Iterable, Sequence

from PySide6.QtCore import (
    QEasingCurve,
    QParallelAnimationGroup,
    QPoint,
    QPropertyAnimation,
    Qt,
    Signal,
)
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QStackedWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ..constants import PROP_FLIP_VIEW
from ..icons import BreezeIcon
from ..icons._themed import ThemedIcon


class FlipView(QWidget):
    """Pixmap carousel with prev/next buttons and slide+fade transitions.

    Add images via :meth:`addPixmap` or :meth:`setPixmaps`.  Use the
    arrow buttons or :meth:`next` / :meth:`previous` to advance.
    ``currentChanged(int)`` fires whenever the visible index moves.
    """

    currentChanged = Signal(int)

    _DURATION_MS = 220

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty(PROP_FLIP_VIEW, True)

        self._stack = QStackedWidget(self)
        self._stack.setFrameShape(self._stack.frameShape())  # noqa: PLR0915

        self._prevButton = QToolButton(self)
        self._prevIcon = ThemedIcon(self._prevButton.setIcon)
        self._prevIcon.set(BreezeIcon.BACK)
        self._prevButton.setAutoRaise(True)
        self._prevButton.clicked.connect(self.previous)

        self._nextButton = QToolButton(self)
        self._nextIcon = ThemedIcon(self._nextButton.setIcon)
        self._nextIcon.set(BreezeIcon.NEXT)
        self._nextButton.setAutoRaise(True)
        self._nextButton.clicked.connect(self.next)

        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 0, 0, 0)
        button_row.addWidget(self._prevButton)
        button_row.addStretch(1)
        button_row.addWidget(self._nextButton)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(self._stack, 1)
        layout.addLayout(button_row)

        self._anim_group: QParallelAnimationGroup | None = None
        self._refreshButtonState()

    def refreshTheme(self) -> None:
        self._prevIcon.refresh()
        self._nextIcon.refresh()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def addPixmap(self, pixmap: QPixmap) -> int:
        label = QLabel(self._stack)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setPixmap(pixmap)
        label.setScaledContents(False)
        index = self._stack.addWidget(label)
        self._refreshButtonState()
        return index

    def setPixmaps(self, pixmaps: Iterable[QPixmap]) -> None:
        while self._stack.count():
            w = self._stack.widget(0)
            self._stack.removeWidget(w)
            w.deleteLater()
        for pm in pixmaps:
            self.addPixmap(pm)
        self.setCurrentIndex(0)

    def count(self) -> int:
        return self._stack.count()

    def currentIndex(self) -> int:
        return self._stack.currentIndex()

    def setCurrentIndex(self, index: int, animate: bool = True) -> None:
        if index < 0 or index >= self._stack.count():
            return
        if index == self._stack.currentIndex():
            return
        direction = 1 if index > self._stack.currentIndex() else -1
        if animate and self.isVisible():
            self._animateTo(index, direction)
        else:
            self._stack.setCurrentIndex(index)
        self._refreshButtonState()
        self.currentChanged.emit(index)

    def next(self) -> None:
        if self._stack.currentIndex() < self._stack.count() - 1:
            self.setCurrentIndex(self._stack.currentIndex() + 1)

    def previous(self) -> None:
        if self._stack.currentIndex() > 0:
            self.setCurrentIndex(self._stack.currentIndex() - 1)

    def pixmaps(self) -> Sequence[QPixmap]:
        result: list[QPixmap] = []
        for i in range(self._stack.count()):
            label = self._stack.widget(i)
            if isinstance(label, QLabel) and label.pixmap() is not None:
                result.append(label.pixmap())
        return result

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _animateTo(self, target_index: int, direction: int) -> None:
        new_widget = self._stack.widget(target_index)
        old_widget = self._stack.currentWidget()

        offset = self.width() // 4 or 40
        opacity = QGraphicsOpacityEffect(new_widget)
        new_widget.setGraphicsEffect(opacity)
        opacity.setOpacity(0.0)
        new_widget.move(direction * offset, 0)

        self._stack.setCurrentIndex(target_index)

        slide = QPropertyAnimation(new_widget, b"pos", self)
        slide.setStartValue(QPoint(direction * offset, 0))
        slide.setEndValue(QPoint(0, 0))
        slide.setDuration(self._DURATION_MS)
        slide.setEasingCurve(QEasingCurve.Type.OutCubic)

        fade = QPropertyAnimation(opacity, b"opacity", self)
        fade.setStartValue(0.0)
        fade.setEndValue(1.0)
        fade.setDuration(self._DURATION_MS)

        group = QParallelAnimationGroup(self)
        group.addAnimation(slide)
        group.addAnimation(fade)
        group.start()
        self._anim_group = group
        del old_widget  # kept by stack; just unused locally

    def _refreshButtonState(self) -> None:
        idx = self._stack.currentIndex()
        self._prevButton.setEnabled(idx > 0)
        self._nextButton.setEnabled(idx < self._stack.count() - 1)
