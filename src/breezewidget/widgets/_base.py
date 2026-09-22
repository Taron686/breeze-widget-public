from __future__ import annotations

from PySide6.QtCore import QSize, Qt


class _BreezeWidgetMixin:
    def _finish(self) -> None:
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(34)
        if hasattr(self, "setIconSize"):
            self.setIconSize(QSize(20, 20))
