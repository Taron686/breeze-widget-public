"""Basic input — buttons, combos, spin boxes, checkboxes, radios, slider+switch."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QHBoxLayout, QMenu, QVBoxLayout, QWidget

from breezewidget import (
    BodyLabel,
    BreezeIcon,
    CheckBox,
    ClickableSlider,
    ComboBox,
    DoubleSpinBox,
    DropDownPushButton,
    EditableComboBox,
    InfoBar,
    PillPushButton,
    PrimaryPushButton,
    PushButton,
    RadioButton,
    SpinBox,
    SplitPushButton,
    SwitchButton,
    setThemeColor,
)

from ._gallery import GalleryPage, _row


class WidgetDemoPage(GalleryPage):
    def __init__(self):
        self._pillButtons: list[PillPushButton] = []
        super().__init__("Basic input", "breezewidget.widgets", "basic-input")
        self.addExample("A simple button with text content", self._standardButtonPreview())
        self.addExample("Accent style applied to push button", self._accentButtonPreview())
        self.addExample("A button with graphical content", self._iconButtonPreview())
        self.addExample("Buttons with menus and split actions", self._menuButtonPreview())
        self.addExample("Accent pills that change the theme color", self._pillPreview())
        self.addExample("ComboBox and EditableComboBox", self._comboPreview())
        self.addExample("SpinBox and DoubleSpinBox", self._spinPreview())
        self.addExample("CheckBox — 2-state", self._twoStateCheckboxPreview())
        self.addExample("CheckBox — 3-state (tristate)", self._threeStateCheckboxPreview())
        self.addExample("RadioButton — exclusive group", self._radioPreview())
        self.addExample("ClickableSlider", self._sliderPreview())
        self.addExample("SwitchButton", self._switchPreview())
        self.setStatus("Basic input bereit")
        self.finish()

    def _standardButtonPreview(self) -> QWidget:
        return _row(PushButton("Standard push button"))

    def _accentButtonPreview(self) -> QWidget:
        return _row(PrimaryPushButton("Accent style button"))

    def _iconButtonPreview(self) -> QWidget:
        info = PrimaryPushButton("InfoBar anzeigen", icon=BreezeIcon.INFO)
        info.clicked.connect(lambda: InfoBar.info("Basic input", self._statusLabel.text(), self.window()))
        return _row(PushButton("Icon button", icon=BreezeIcon.SAVE), info)

    def _menuButtonPreview(self) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        dropdown_menu = QMenu(container)
        for text in ("Export", "Archivieren", "Zuruecksetzen"):
            action = dropdown_menu.addAction(text)
            action.triggered.connect(lambda checked=False, value=text: self.setStatus(f"DropDown: {value}"))

        dropdown = DropDownPushButton("Aktion waehlen", container, BreezeIcon.MORE, dropdown_menu)
        layout.addWidget(dropdown)

        split_menu = QMenu(container)
        for text in ("Als Entwurf", "Mit Protokoll", "Zeitversetzt"):
            action = split_menu.addAction(text)
            action.triggered.connect(lambda checked=False, value=text: self.setStatus(f"Split-Menue: {value}"))

        split = SplitPushButton("Ausfuehren", container, BreezeIcon.CHECK, split_menu)
        split.clicked.connect(lambda: self.setStatus("Split-Hauptaktion ausgefuehrt"))
        layout.addWidget(split)
        layout.addStretch(1)
        return container

    def _pillPreview(self) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        pill_specs = (
            ("Cyan", "#11d9f3", BreezeIcon.HOME),
            ("Blau", "#0067c0", BreezeIcon.PEOPLE),
            ("Gruen", "#10893e", BreezeIcon.CHECK),
        )
        for index, (label, color, icon) in enumerate(pill_specs):
            button = PillPushButton(icon, label, row)
            button.setChecked(index == 0)
            button.clicked.connect(
                lambda checked=False, value=color, name=label, source=button: self._activatePill(source, name, value)
            )
            self._pillButtons.append(button)
            layout.addWidget(button)
        layout.addStretch(1)
        return row

    def _comboPreview(self) -> QWidget:
        combo = ComboBox()
        combo.addItems(["Compact", "Comfortable", "Spacious"])
        combo.currentTextChanged.connect(lambda text: self.setStatus(f"ComboBox: {text}"))

        editable = EditableComboBox()
        editable.addItems(["Alpha", "Beta", "Gamma"])
        editable.setCurrentText("Editable")
        return _row(combo, editable)

    def _spinPreview(self) -> QWidget:
        spin = SpinBox()
        spin.setRange(0, 100)
        spin.setValue(24)
        spin.valueChanged.connect(lambda value: self.setStatus(f"SpinBox: {value}"))

        double_spin = DoubleSpinBox()
        double_spin.setRange(0.0, 10.0)
        double_spin.setDecimals(2)
        double_spin.setSingleStep(0.25)
        double_spin.setValue(2.5)
        double_spin.valueChanged.connect(lambda value: self.setStatus(f"DoubleSpinBox: {value:.2f}"))
        return _row(spin, double_spin)

    def _twoStateCheckboxPreview(self) -> QWidget:
        cb1 = CheckBox("Enable feature A")
        cb2 = CheckBox("Enable feature B")
        cb2.setChecked(True)
        cb1.toggled.connect(lambda v: self.setStatus(f"Feature A: {'on' if v else 'off'}"))
        cb2.toggled.connect(lambda v: self.setStatus(f"Feature B: {'on' if v else 'off'}"))
        return _row(cb1, cb2)

    def _threeStateCheckboxPreview(self) -> QWidget:
        parent_cb = CheckBox("Select all")
        parent_cb.setTristate(True)
        child_a = CheckBox("Item A")
        child_b = CheckBox("Item B")
        child_c = CheckBox("Item C")
        children = [child_a, child_b, child_c]
        guard = {"sync": False}

        def _sync_parent():
            if guard["sync"]:
                return
            guard["sync"] = True
            checked = sum(1 for c in children if c.isChecked())
            if checked == 0:
                parent_cb.setCheckState(Qt.CheckState.Unchecked)
            elif checked == len(children):
                parent_cb.setCheckState(Qt.CheckState.Checked)
            else:
                parent_cb.setCheckState(Qt.CheckState.PartiallyChecked)
            guard["sync"] = False

        def _sync_children(state):
            if guard["sync"]:
                return
            if state == Qt.CheckState.PartiallyChecked.value:
                return
            guard["sync"] = True
            on = state == Qt.CheckState.Checked.value
            for c in children:
                c.setChecked(on)
            guard["sync"] = False

        parent_cb.stateChanged.connect(_sync_children)
        for c in children:
            c.toggled.connect(_sync_parent)

        container = QWidget()
        v = QVBoxLayout(container)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(4)
        v.addWidget(parent_cb)
        for c in children:
            indent = QWidget()
            h = QHBoxLayout(indent)
            h.setContentsMargins(20, 0, 0, 0)
            h.setSpacing(0)
            h.addWidget(c)
            v.addWidget(indent)
        return container

    def _radioPreview(self) -> QWidget:
        opt_a = RadioButton("Option A")
        opt_b = RadioButton("Option B")
        opt_c = RadioButton("Option C")
        opt_a.setChecked(True)
        for r in (opt_a, opt_b, opt_c):
            r.toggled.connect(
                lambda v, w=r: self.setStatus(f"{w.text()}: {'selected' if v else '—'}")
            )
        return _row(opt_a, opt_b, opt_c)

    def _sliderPreview(self) -> QWidget:
        value_label = BodyLabel("Wert: 40")
        slider = ClickableSlider(Qt.Orientation.Horizontal)
        slider.setFixedWidth(240)
        slider.setRange(0, 100)
        slider.setValue(40)
        slider.valueChanged.connect(lambda value: value_label.setText(f"Wert: {value}"))
        slider.valueChanged.connect(lambda value: self.setStatus(f"ClickableSlider: {value}"))
        return _row(slider, value_label)

    def _switchPreview(self) -> QWidget:
        switch = SwitchButton("Benachrichtigungen")
        switch.toggled.connect(lambda checked: self.setStatus(f"SwitchButton: {'an' if checked else 'aus'}"))

        custom = SwitchButton("Auto-Sync")
        custom.setStateLabelPosition("left")
        custom.setOnText("AN")
        custom.setOffText("AUS")
        custom.toggled.connect(lambda checked: self.setStatus(f"Auto-Sync: {'AN' if checked else 'AUS'}"))
        return _row(switch, custom)

    def _setAccent(self, name: str, color: str) -> None:
        setThemeColor(color, QApplication.instance())
        self.setStatus(f"Akzentfarbe: {name}")

    def _activatePill(self, source: PillPushButton, name: str, color: str) -> None:
        for button in self._pillButtons:
            button.setChecked(button is source)
        self._setAccent(name, color)
        for button in self._pillButtons:
            button.refreshTheme()
