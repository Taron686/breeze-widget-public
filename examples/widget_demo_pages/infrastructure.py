"""Infrastructure (7) — BreezeConfig, ExceptionHandler, Translator, OSThemeListener."""
from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from breezewidget import (
    BodyLabel,
    BoolValidator,
    BreezeConfig,
    BreezeIcon,
    ColorConfigItem,
    ComboBox,
    ConfigItem,
    ExceptionHandler,
    OptionsConfigItem,
    OptionsValidator,
    OSThemeListener,
    PushButton,
    RangeConfigItem,
    RangeValidator,
    SpinBox,
    SwitchButton,
    Translator,
)

from ._gallery import GalleryPage


class _DemoConfig(BreezeConfig):
    """Sample BreezeConfig used by the Infrastructure demo."""

    enableTelemetry = ConfigItem("App", "EnableTelemetry", True, BoolValidator())
    volume = RangeConfigItem("App", "Volume", 50, RangeValidator(0, 100))
    quality = OptionsConfigItem("App", "Quality", "medium", OptionsValidator(["low", "medium", "high"]))
    accent = ColorConfigItem("App", "Accent", "#11d9f3")


class InfrastructureDemoPage(GalleryPage):
    """Phase 7a-d — BreezeConfig, ExceptionHandler, Translator, OSThemeListener."""

    def __init__(self):
        super().__init__("Infrastructure", "breezewidget.core + breezewidget.theme.listener", "infrastructure")

        # --- Phase 7a: BreezeConfig ---------------------------------------
        from pathlib import Path
        import tempfile

        self._cfg_file = Path(tempfile.gettempdir()) / "breeze_demo_settings.json"
        self._cfg = _DemoConfig(self._cfg_file)
        self._cfg.load()

        cfg_row = QWidget()
        cfg_layout = QVBoxLayout(cfg_row)
        cfg_layout.setContentsMargins(0, 0, 0, 0)
        cfg_layout.setSpacing(8)

        controls = QHBoxLayout()
        controls.setSpacing(8)
        telemetry_switch = SwitchButton("Enable telemetry")
        telemetry_switch.setChecked(self._cfg.get(_DemoConfig.enableTelemetry))
        telemetry_switch.toggled.connect(
            lambda v: self._cfg.set(_DemoConfig.enableTelemetry, v)
        )
        quality_combo = ComboBox()
        quality_combo.addItems(["low", "medium", "high"])
        quality_combo.setCurrentText(self._cfg.get(_DemoConfig.quality))
        quality_combo.currentTextChanged.connect(
            lambda v: self._cfg.set(_DemoConfig.quality, v)
        )
        volume_spin = SpinBox()
        volume_spin.setRange(0, 100)
        volume_spin.setValue(self._cfg.get(_DemoConfig.volume))
        volume_spin.valueChanged.connect(
            lambda v: self._cfg.set(_DemoConfig.volume, v)
        )
        controls.addWidget(telemetry_switch)
        controls.addWidget(BodyLabel("Quality"))
        controls.addWidget(quality_combo)
        controls.addWidget(BodyLabel("Volume"))
        controls.addWidget(volume_spin)
        controls.addStretch(1)

        button_row = QHBoxLayout()
        save_button = PushButton("Save", icon=BreezeIcon.DOWNLOAD)
        load_button = PushButton("Reload")
        reset_button = PushButton("Reset")
        self._cfg_status = BodyLabel(f"File: {self._cfg_file}")
        save_button.clicked.connect(lambda: (self._cfg.save(), self._cfg_status.setText(f"Saved → {self._cfg_file}")))
        load_button.clicked.connect(
            lambda: (
                self._cfg.load(),
                telemetry_switch.setChecked(self._cfg.get(_DemoConfig.enableTelemetry)),
                quality_combo.setCurrentText(self._cfg.get(_DemoConfig.quality)),
                volume_spin.setValue(self._cfg.get(_DemoConfig.volume)),
                self._cfg_status.setText(f"Loaded ← {self._cfg_file}"),
            )
        )
        reset_button.clicked.connect(
            lambda: (
                self._cfg.reset(),
                telemetry_switch.setChecked(self._cfg.get(_DemoConfig.enableTelemetry)),
                quality_combo.setCurrentText(self._cfg.get(_DemoConfig.quality)),
                volume_spin.setValue(self._cfg.get(_DemoConfig.volume)),
                self._cfg_status.setText("Reset to defaults"),
            )
        )
        button_row.addWidget(save_button)
        button_row.addWidget(load_button)
        button_row.addWidget(reset_button)
        button_row.addStretch(1)

        cfg_layout.addLayout(controls)
        cfg_layout.addLayout(button_row)
        cfg_layout.addWidget(self._cfg_status)
        self.addExample("BreezeConfig — JSON-backed app settings with validators", cfg_row, "breezewidget.core.config")

        # --- Phase 7b: ExceptionHandler -----------------------------------
        self._handler = ExceptionHandler()
        self._exc_log = BodyLabel("No exceptions yet.")
        self._handler.exceptionRaised.connect(
            lambda et, e, tb: self._exc_log.setText(f"Caught: {et.__name__}: {e}")
        )

        exc_row = QWidget()
        exc_layout = QHBoxLayout(exc_row)
        exc_layout.setContentsMargins(0, 0, 0, 0)
        exc_layout.setSpacing(8)
        raise_button = PushButton("Trigger ValueError", icon=BreezeIcon.WARNING)

        def _trigger():
            try:
                raise ValueError("Demo exception from button click")
            except ValueError as e:
                self._handler.handle(type(e), e, e.__traceback__)

        raise_button.clicked.connect(_trigger)
        exc_layout.addWidget(raise_button)
        exc_layout.addWidget(self._exc_log, 1)
        self.addExample("ExceptionHandler — catches and reports unhandled exceptions", exc_row, "breezewidget.core.exception_handler")

        # --- Phase 7c: Translator ----------------------------------------
        self._translator = Translator()
        tr_row = QWidget()
        tr_layout = QVBoxLayout(tr_row)
        tr_layout.setContentsMargins(0, 0, 0, 0)
        tr_layout.setSpacing(6)
        tr_status = BodyLabel("Locale: (none)")
        self._translator.languageChanged.connect(
            lambda loc: tr_status.setText(f"Locale changed → {loc!r}")
        )
        tr_button_row = QHBoxLayout()
        sys_btn = PushButton("Use system locale")
        sys_btn.clicked.connect(self._translator.useSystemLocale)
        clear_btn = PushButton("Clear")
        clear_btn.clicked.connect(self._translator.clear)
        tr_button_row.addWidget(sys_btn)
        tr_button_row.addWidget(clear_btn)
        tr_button_row.addStretch(1)
        tr_layout.addLayout(tr_button_row)
        tr_layout.addWidget(tr_status)
        self.addExample("Translator — QTranslator wrapper, OS-locale detection", tr_row, "breezewidget.core.translator")

        # --- Phase 7d: OSThemeListener -----------------------------------
        self._listener = OSThemeListener(interval_ms=1000)
        os_row = QWidget()
        os_layout = QHBoxLayout(os_row)
        os_layout.setContentsMargins(0, 0, 0, 0)
        os_layout.setSpacing(8)
        os_status = BodyLabel(f"OS dark right now: {self._listener.isOSDark()}")
        self._listener.osThemeChanged.connect(
            lambda dark: os_status.setText(f"OS theme changed → {'dark' if dark else 'light'}")
        )
        start_btn = PushButton("Start polling")
        stop_btn = PushButton("Stop")
        start_btn.clicked.connect(self._listener.start)
        stop_btn.clicked.connect(self._listener.stop)
        os_layout.addWidget(start_btn)
        os_layout.addWidget(stop_btn)
        os_layout.addWidget(os_status, 1)
        self.addExample("OSThemeListener — polls OS dark/light state", os_row, "breezewidget.theme.listener")

        self.finish()
