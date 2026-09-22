"""Phase 7a — BreezeConfig / ConfigItem / Validators / Serializers."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from PySide6.QtGui import QColor

from breezewidget import (
    BoolValidator,
    BreezeConfig,
    ColorConfigItem,
    ColorSerializer,
    ConfigItem,
    EnumSerializer,
    FolderListValidator,
    FolderValidator,
    OptionsConfigItem,
    OptionsValidator,
    RangeConfigItem,
    RangeValidator,
)


# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------

def test_range_validator_accepts_in_range():
    v = RangeValidator(0, 10)
    assert v.validate(5)
    assert v.validate(0)
    assert v.validate(10)
    assert not v.validate(-1)
    assert not v.validate(11)
    assert not v.validate("x")


def test_range_validator_correct_clamps():
    v = RangeValidator(0, 10)
    assert v.correct(-5) == 0
    assert v.correct(15) == 10
    assert v.correct(5) == 5
    assert v.correct("x") == 0


def test_range_validator_rejects_inverted_bounds():
    with pytest.raises(ValueError):
        RangeValidator(10, 0)


def test_options_validator_whitelist():
    v = OptionsValidator(["a", "b", "c"])
    assert v.validate("a")
    assert not v.validate("z")
    assert v.correct("z") == "a"


def test_options_validator_rejects_empty():
    with pytest.raises(ValueError):
        OptionsValidator([])


def test_bool_validator():
    v = BoolValidator()
    assert v.validate(True) and v.validate(False)
    assert not v.validate(1)
    assert v.correct(1) is True
    assert v.correct(0) is False


def test_folder_validator(tmp_path):
    v = FolderValidator()
    assert v.validate(str(tmp_path))
    assert not v.validate(str(tmp_path / "missing"))
    assert not v.validate(123)


def test_folder_list_validator(tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    v = FolderListValidator()
    assert v.validate([str(tmp_path), str(sub)])
    assert not v.validate([str(tmp_path), str(tmp_path / "missing")])
    corrected = v.correct([str(tmp_path), str(tmp_path / "missing")])
    assert corrected == [str(tmp_path)]


# ---------------------------------------------------------------------------
# ConfigItem
# ---------------------------------------------------------------------------

def test_config_item_default_and_value(qapp):
    item = ConfigItem("App", "Name", "Hello")
    assert item.value == "Hello"
    assert item.qualifiedKey == "App.Name"


def test_config_item_set_value_emits_signal(qapp):
    item = ConfigItem("App", "Name", "old")
    seen = []
    item.valueChanged.connect(seen.append)
    item.setValue("new")
    assert item.value == "new"
    assert seen == ["new"]


def test_config_item_no_signal_on_same_value(qapp):
    item = ConfigItem("App", "Name", "x")
    seen = []
    item.valueChanged.connect(seen.append)
    item.setValue("x")
    assert seen == []


def test_config_item_validator_corrects_invalid(qapp):
    item = ConfigItem("App", "Volume", 50, RangeValidator(0, 100))
    item.setValue(150)
    assert item.value == 100
    item.setValue(-5)
    assert item.value == 0


def test_config_item_reset(qapp):
    item = ConfigItem("App", "Name", "default")
    item.setValue("changed")
    item.reset()
    assert item.value == "default"


def test_range_config_item_exposes_range(qapp):
    item = RangeConfigItem("App", "Volume", 50, RangeValidator(0, 100))
    assert item.range == (0, 100)


def test_range_config_item_rejects_wrong_validator():
    with pytest.raises(TypeError):
        RangeConfigItem("App", "X", 0, OptionsValidator([0, 1]))  # type: ignore[arg-type]


def test_options_config_item_exposes_options(qapp):
    item = OptionsConfigItem("App", "Theme", "auto", OptionsValidator(["auto", "light", "dark"]))
    assert item.options == ["auto", "light", "dark"]


def test_color_config_item_default_str_to_qcolor(qapp):
    item = ColorConfigItem("App", "Accent", "#11d9f3")
    assert isinstance(item.value, QColor)
    assert item.value.name() == "#11d9f3"


# ---------------------------------------------------------------------------
# Serializers
# ---------------------------------------------------------------------------

def test_color_serializer_roundtrip():
    s = ColorSerializer()
    c = QColor("#11d9f3")
    raw = s.serialize(c)
    assert raw == "#11d9f3"
    back = s.deserialize(raw)
    assert isinstance(back, QColor) and back.name() == "#11d9f3"


def test_color_serializer_invalid_falls_back():
    s = ColorSerializer()
    back = s.deserialize("not-a-color")
    assert isinstance(back, QColor) and back.name() == "#000000"


def test_enum_serializer():
    import enum

    class Mood(enum.Enum):
        HAPPY = 1
        SAD = 2

    s = EnumSerializer(Mood)
    assert s.serialize(Mood.HAPPY) == "HAPPY"
    assert s.deserialize("SAD") is Mood.SAD
    assert s.deserialize("BOGUS") is Mood.HAPPY  # fallback first


# ---------------------------------------------------------------------------
# BreezeConfig
# ---------------------------------------------------------------------------

class _AppConfig(BreezeConfig):
    theme = OptionsConfigItem("App", "Theme", "auto", OptionsValidator(["auto", "light", "dark"]))
    volume = RangeConfigItem("App", "Volume", 50, RangeValidator(0, 100))
    fullscreen = ConfigItem("App", "Fullscreen", False, BoolValidator())
    accent = ColorConfigItem("App", "Accent", "#11d9f3")


def test_config_collects_class_items(qapp, tmp_path):
    cfg = _AppConfig(tmp_path / "settings.json")
    items = cfg.items()
    assert set(items.keys()) == {"App.Theme", "App.Volume", "App.Fullscreen", "App.Accent"}


def test_config_instances_are_independent(qapp, tmp_path):
    cfg_a = _AppConfig(tmp_path / "a.json")
    cfg_b = _AppConfig(tmp_path / "b.json")
    cfg_a.set(_AppConfig.theme, "dark")
    assert cfg_a.get(_AppConfig.theme) == "dark"
    assert cfg_b.get(_AppConfig.theme) == "auto"


def test_config_value_changed_signal(qapp, tmp_path):
    cfg = _AppConfig(tmp_path / "s.json")
    seen: list[tuple[str, str, object]] = []
    cfg.valueChanged.connect(lambda g, k, v: seen.append((g, k, v)))
    cfg.set(_AppConfig.volume, 80)
    assert seen == [("App", "Volume", 80)]


def test_config_save_and_load_roundtrip(qapp, tmp_path):
    path = tmp_path / "settings.json"
    cfg = _AppConfig(path)
    cfg.set(_AppConfig.theme, "dark")
    cfg.set(_AppConfig.volume, 80)
    cfg.set(_AppConfig.fullscreen, True)
    cfg.set(_AppConfig.accent, QColor("#ff8800"))
    assert cfg.save() is True

    raw = json.loads(path.read_text(encoding="utf-8"))
    assert raw["App"]["Theme"] == "dark"
    assert raw["App"]["Volume"] == 80
    assert raw["App"]["Fullscreen"] is True
    assert raw["App"]["Accent"] == "#ff8800"

    cfg2 = _AppConfig(path)
    assert cfg2.load() is True
    assert cfg2.get(_AppConfig.theme) == "dark"
    assert cfg2.get(_AppConfig.volume) == 80
    assert cfg2.get(_AppConfig.fullscreen) is True
    assert cfg2.get(_AppConfig.accent).name() == "#ff8800"


def test_config_load_missing_file_keeps_defaults(qapp, tmp_path):
    cfg = _AppConfig(tmp_path / "nope.json")
    assert cfg.load() is False
    assert cfg.get(_AppConfig.theme) == "auto"


def test_config_load_invalid_json_returns_false(qapp, tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("not json", encoding="utf-8")
    cfg = _AppConfig(path)
    assert cfg.load() is False


def test_config_load_ignores_unknown_keys(qapp, tmp_path):
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({"App": {"Theme": "dark", "Bogus": 1}, "Other": {"X": 1}}), encoding="utf-8")
    cfg = _AppConfig(path)
    assert cfg.load() is True
    assert cfg.get(_AppConfig.theme) == "dark"


def test_config_load_validator_corrects(qapp, tmp_path):
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({"App": {"Volume": 9999, "Theme": "neon"}}), encoding="utf-8")
    cfg = _AppConfig(path)
    assert cfg.load() is True
    assert cfg.get(_AppConfig.volume) == 100
    assert cfg.get(_AppConfig.theme) == "auto"  # first option


def test_config_save_creates_parent_dirs(qapp, tmp_path):
    nested = tmp_path / "deep" / "nest" / "settings.json"
    cfg = _AppConfig(nested)
    assert cfg.save() is True
    assert nested.is_file()


def test_config_reset_returns_to_defaults(qapp, tmp_path):
    cfg = _AppConfig(tmp_path / "s.json")
    cfg.set(_AppConfig.theme, "dark")
    cfg.set(_AppConfig.volume, 80)
    cfg.reset()
    assert cfg.get(_AppConfig.theme) == "auto"
    assert cfg.get(_AppConfig.volume) == 50


def test_config_set_unknown_item_raises(qapp, tmp_path):
    cfg = _AppConfig(tmp_path / "s.json")
    foreign = ConfigItem("Other", "X", 1)
    with pytest.raises(KeyError):
        cfg.set(foreign, 2)


def test_config_save_without_file_returns_false(qapp):
    cfg = _AppConfig(None)
    assert cfg.save() is False


def test_config_set_file_then_save(qapp, tmp_path):
    cfg = _AppConfig(None)
    cfg.setFile(tmp_path / "s.json")
    assert cfg.file() == tmp_path / "s.json"
    assert cfg.save() is True
