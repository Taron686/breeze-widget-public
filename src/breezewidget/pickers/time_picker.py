"""TimePicker — combo boxes for hour and minute (with optional AM/PM)."""
from __future__ import annotations

from PySide6.QtCore import QTime, Signal
from PySide6.QtWidgets import QHBoxLayout, QWidget

from ..constants import PROP_TIME_PICKER
from ..widgets.combo_box import ComboBox


class TimePicker(QWidget):
    """Hour/minute (and optional AM/PM) selection widget.

    Construct with ``use_24h=False`` to switch to 12-hour mode with a
    third combo box for AM/PM.  Minute granularity is configurable via
    ``minute_step`` (default 1).  Always exposes a valid
    :class:`QTime`; ``timeChanged`` fires on user edits and on
    :meth:`setTime` when the value actually changes.
    """

    timeChanged = Signal(QTime)

    def __init__(
        self,
        time: QTime | None = None,
        use_24h: bool = True,
        minute_step: int = 1,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setProperty(PROP_TIME_PICKER, True)
        self._use_24h = use_24h
        self._minute_step = max(1, minute_step)
        self._suspend = False

        self._hourCombo = ComboBox(self)
        self._minuteCombo = ComboBox(self)
        self._periodCombo: ComboBox | None = None

        if use_24h:
            self._hourCombo.addItems([f"{h:02d}" for h in range(24)])
        else:
            self._hourCombo.addItems([f"{h:02d}" for h in range(1, 13)])
            self._periodCombo = ComboBox(self)
            self._periodCombo.addItems(["AM", "PM"])

        self._minuteCombo.addItems(
            [f"{m:02d}" for m in range(0, 60, self._minute_step)]
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(self._hourCombo, 1)
        layout.addWidget(self._minuteCombo, 1)
        if self._periodCombo is not None:
            layout.addWidget(self._periodCombo, 1)

        self._hourCombo.currentIndexChanged.connect(self._onChanged)
        self._minuteCombo.currentIndexChanged.connect(self._onChanged)
        if self._periodCombo is not None:
            self._periodCombo.currentIndexChanged.connect(self._onChanged)

        self.setTime(time or QTime.currentTime())

    # --- public API -----------------------------------------------------

    def time(self) -> QTime:
        minute = self._minuteCombo.currentIndex() * self._minute_step
        if self._use_24h:
            hour = self._hourCombo.currentIndex()
        else:
            display_hour = self._hourCombo.currentIndex() + 1  # 1..12
            is_pm = self._periodCombo is not None and self._periodCombo.currentIndex() == 1
            if display_hour == 12:
                hour = 12 if is_pm else 0
            else:
                hour = display_hour + (12 if is_pm else 0)
        return QTime(hour, minute)

    def setTime(self, time: QTime) -> None:
        if not time.isValid():
            return
        self._suspend = True
        try:
            if self._use_24h:
                self._hourCombo.setCurrentIndex(time.hour())
            else:
                hour = time.hour()
                is_pm = hour >= 12
                display_hour = hour % 12
                if display_hour == 0:
                    display_hour = 12
                self._hourCombo.setCurrentIndex(display_hour - 1)
                if self._periodCombo is not None:
                    self._periodCombo.setCurrentIndex(1 if is_pm else 0)
            minute_idx = min(
                self._minuteCombo.count() - 1,
                time.minute() // self._minute_step,
            )
            self._minuteCombo.setCurrentIndex(minute_idx)
        finally:
            self._suspend = False
        self.timeChanged.emit(self.time())

    # --- internal -------------------------------------------------------

    def _onChanged(self, *_) -> None:
        if self._suspend:
            return
        self.timeChanged.emit(self.time())
