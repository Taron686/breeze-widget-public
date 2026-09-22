from __future__ import annotations

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QWidget


class BreezeRouter(QObject):
    """Navigation history manager and route-to-widget registry.

    The router is a pure logical component — it owns no UI elements.
    Wire ``routeChanged`` to update the visible widget and navigation highlight.

    Typical usage inside ``BreezeWindow``::

        self.router = BreezeRouter(self)
        self.router.routeChanged.connect(self._onRouteChanged)

        # register + navigate
        self.router.addRoute("home", home_page)
        self.router.replace("home")     # initial route, no history entry

        # later
        self.router.push("settings")    # adds "home" to history
        self.router.back()              # returns to "home"
    """

    routeChanged = Signal(str)  # emitted with the new current route key

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._routes: dict[str, QWidget] = {}
        self._history: list[str] = []
        self._current: str | None = None

    # ------------------------------------------------------------------
    # Route registration
    # ------------------------------------------------------------------

    def addRoute(self, key: str, widget: QWidget) -> None:
        """Register *key* → *widget*.  Does not navigate."""
        self._routes[key] = widget

    def widget(self, key: str) -> QWidget | None:
        """Return the widget registered under *key*, or ``None``."""
        return self._routes.get(key)

    def keyForWidget(self, widget: QWidget) -> str | None:
        """Return the route key for *widget*, or ``None`` if not registered."""
        for k, w in self._routes.items():
            if w is widget:
                return k
        return None

    def routes(self) -> dict[str, QWidget]:
        """Return a shallow copy of the route registry."""
        return dict(self._routes)

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def push(self, key: str) -> None:
        """Navigate to *key*, saving the current route to the history stack.

        No-op when *key* is already current or not registered.
        """
        if key not in self._routes or key == self._current:
            return
        if self._current is not None:
            self._history.append(self._current)
        self._current = key
        self.routeChanged.emit(key)

    def replace(self, key: str) -> None:
        """Navigate to *key* without modifying the history stack.

        Use for the initial route or redirects that should not be
        reachable via ``back()``.  No-op when *key* is already current
        or not registered.
        """
        if key not in self._routes or key == self._current:
            return
        self._current = key
        self.routeChanged.emit(key)

    def back(self) -> None:
        """Navigate to the previous route.  No-op when history is empty."""
        if not self._history:
            return
        key = self._history.pop()
        self._current = key
        self.routeChanged.emit(key)

    # ------------------------------------------------------------------
    # State queries
    # ------------------------------------------------------------------

    def current(self) -> str | None:
        """Return the current route key, or ``None`` before any navigation."""
        return self._current

    def canGoBack(self) -> bool:
        """Return ``True`` when at least one route exists in the history."""
        return bool(self._history)
