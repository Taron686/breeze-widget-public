from __future__ import annotations

from collections.abc import Callable
from typing import Any
import weakref

from PySide6.QtGui import QIcon
from shiboken6 import isValid

from .breeze_icon import icon_from

IconColorProvider = Callable[[], str | None]
IconApplier = Callable[[QIcon], None]


def default_icon_color() -> str:
    from ..theme import isDarkTheme

    return "#ffffff" if isDarkTheme() else "#000000"


def primary_icon_color() -> str:
    from ..theme import getPalette

    return getPalette().primary_text


class ThemedIcon:
    def __init__(
        self,
        apply_icon: IconApplier,
        *,
        color: IconColorProvider | None = default_icon_color,
        size: int = 32,
        stroke_width: float | int | str | None = None,
    ) -> None:
        self._apply_icon = apply_icon
        self._color = color
        self._size = size
        self._stroke_width = stroke_width
        self._source: Any = None

    @property
    def source(self) -> Any:
        return self._source

    def set(self, source: Any) -> None:
        self._source = source
        self.refresh()

    def refresh(self) -> None:
        self._apply_icon(self.render())

    def render(self) -> QIcon:
        if self._source is None:
            return QIcon()
        if isinstance(self._source, QIcon):
            return self._source
        color = self._color() if self._color is not None else None
        return icon_from(
            self._source,
            color=color,
            size=self._size,
            stroke_width=self._stroke_width,
        )


class ThemedActionIcons:
    def __init__(
        self,
        *,
        color: IconColorProvider | None = default_icon_color,
        size: int = 32,
        stroke_width: float | int | str | None = None,
    ) -> None:
        self._color = color
        self._size = size
        self._stroke_width = stroke_width
        self._sources: dict[Any, Any] = {}
        self._watched: weakref.WeakSet = weakref.WeakSet()

    def set(self, action: Any, source: Any) -> None:
        if source is None:
            self._sources.pop(action, None)
            action.setIcon(QIcon())
            return
        if isinstance(source, QIcon):
            self._sources.pop(action, None)
            action.setIcon(source)
            return
        if action not in self._watched:
            owner_ref, action_ref = weakref.ref(self), weakref.ref(action)

            def on_destroyed(_object=None):
                owner, current = owner_ref(), action_ref()
                if owner is not None and current is not None:
                    owner._sources.pop(current, None)
                    owner._watched.discard(current)

            action.destroyed.connect(on_destroyed)
            self._watched.add(action)
        self._sources[action] = source
        action.setIcon(self.render(source))

    def refresh(self) -> None:
        for action in list(self._sources):
            if action not in self._sources or not isValid(action):
                continue
            source = self._sources[action]
            icon = self.render(source)
            if isValid(action) and self._sources.get(action) is source:
                action.setIcon(icon)

    def render(self, source: Any) -> QIcon:
        color = self._color() if self._color is not None else None
        return icon_from(
            source,
            color=color,
            size=self._size,
            stroke_width=self._stroke_width,
        )
