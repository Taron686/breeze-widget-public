"""Persisted application config — :class:`BreezeConfig` plus :class:`ConfigItem`.

Subclass :class:`BreezeConfig`, declare :class:`ConfigItem` class attributes,
construct with a JSON file path, and call ``load()`` / ``save()``::

    class AppConfig(BreezeConfig):
        theme = OptionsConfigItem("App", "Theme", "auto", OptionsValidator(["auto", "light", "dark"]))
        windowSize = ConfigItem("App", "WindowSize", [800, 600])
        accent = ColorConfigItem("App", "Accent", "#11d9f3")

    cfg = AppConfig(Path("settings.json"))
    cfg.load()
    cfg.set(AppConfig.theme, "dark")
    cfg.save()

Each :class:`ConfigItem` emits ``valueChanged`` whenever its stored value
changes; :class:`BreezeConfig` re-emits as ``valueChanged(group, key, value)``.
"""
from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QColor


# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------

class ConfigValidator:
    """Base validator. Override :meth:`validate` and :meth:`correct`."""

    def validate(self, value: Any) -> bool:
        return True

    def correct(self, value: Any) -> Any:
        return value


class RangeValidator(ConfigValidator):
    """Numeric range, inclusive ``[min, max]``."""

    def __init__(self, min_value: float, max_value: float) -> None:
        if min_value > max_value:
            raise ValueError("min_value must be <= max_value")
        self.min = min_value
        self.max = max_value

    def validate(self, value: Any) -> bool:
        return isinstance(value, (int, float)) and self.min <= value <= self.max

    def correct(self, value: Any) -> Any:
        if not isinstance(value, (int, float)):
            return self.min
        return max(self.min, min(self.max, value))


class OptionsValidator(ConfigValidator):
    """Whitelist of permitted values."""

    def __init__(self, options: Iterable[Any]) -> None:
        self.options = list(options)
        if not self.options:
            raise ValueError("OptionsValidator requires at least one option")

    def validate(self, value: Any) -> bool:
        return value in self.options

    def correct(self, value: Any) -> Any:
        return value if value in self.options else self.options[0]


class BoolValidator(ConfigValidator):
    def validate(self, value: Any) -> bool:
        return isinstance(value, bool)

    def correct(self, value: Any) -> Any:
        return bool(value)


class FolderValidator(ConfigValidator):
    """Existing-directory validator."""

    def validate(self, value: Any) -> bool:
        if not isinstance(value, (str, Path)):
            return False
        return Path(value).is_dir()

    def correct(self, value: Any) -> Any:
        return str(value) if isinstance(value, (str, Path)) else ""


class FolderListValidator(ConfigValidator):
    """List of existing directories."""

    def validate(self, value: Any) -> bool:
        if not isinstance(value, list):
            return False
        return all(isinstance(p, (str, Path)) and Path(p).is_dir() for p in value)

    def correct(self, value: Any) -> Any:
        if not isinstance(value, list):
            return []
        return [str(p) for p in value if isinstance(p, (str, Path)) and Path(p).is_dir()]


# ---------------------------------------------------------------------------
# Serializers
# ---------------------------------------------------------------------------

class ConfigSerializer:
    """Identity serializer. Override for non-JSON-native values."""

    def serialize(self, value: Any) -> Any:
        return value

    def deserialize(self, raw: Any) -> Any:
        return raw


class ColorSerializer(ConfigSerializer):
    """Serialize ``QColor`` as ``#rrggbb`` / ``#rrggbbaa`` hex string."""

    def serialize(self, value: Any) -> Any:
        if isinstance(value, QColor):
            return value.name(QColor.NameFormat.HexArgb if value.alpha() != 255 else QColor.NameFormat.HexRgb)
        return str(value)

    def deserialize(self, raw: Any) -> Any:
        if isinstance(raw, QColor):
            return raw
        color = QColor(str(raw))
        return color if color.isValid() else QColor("#000000")


class EnumSerializer(ConfigSerializer):
    """Serialize :class:`enum.Enum` members by ``.name``."""

    def __init__(self, enum_cls: type) -> None:
        self.enum_cls = enum_cls

    def serialize(self, value: Any) -> Any:
        if isinstance(value, self.enum_cls):
            return value.name
        return value

    def deserialize(self, raw: Any) -> Any:
        if isinstance(raw, self.enum_cls):
            return raw
        try:
            return self.enum_cls[raw]
        except (KeyError, TypeError):
            return next(iter(self.enum_cls))


# ---------------------------------------------------------------------------
# ConfigItem
# ---------------------------------------------------------------------------

def _copy_config_value(value: Any, memo: dict[int, Any] | None = None) -> Any:
    """Copy built-in containers and QColor, preserving aliases within the copy.

    Other values (including user resources, QObjects and enums) keep their
    identity. Validators and serializers are shared strategies, not value data.
    """
    memo = {} if memo is None else memo
    identity = id(value)
    if identity in memo:
        return memo[identity]
    if isinstance(value, QColor):
        result = QColor(value)
    elif type(value) is list:
        result = []
        memo[identity] = result
        result.extend(_copy_config_value(item, memo) for item in value)
    elif type(value) is dict:
        result = {}
        memo[identity] = result
        for key, item in value.items():
            result[_copy_config_value(key, memo)] = _copy_config_value(item, memo)
    elif type(value) is tuple:
        items = [_copy_config_value(item, memo) for item in value]
        # A recursive tuple/list graph may have completed this tuple already.
        if identity in memo:
            return memo[identity]
        result = tuple(items)
    else:
        return value
    memo[identity] = result
    return result


class ConfigItem(QObject):
    """Single persisted setting.

    Identified by ``(group, key)``.  Holds a single value plus optional
    :class:`ConfigValidator` and :class:`ConfigSerializer`.  ``valueChanged``
    fires only when the stored value actually changes.
    """

    valueChanged = Signal(object)

    def __init__(
        self,
        group: str,
        key: str,
        default: Any,
        validator: ConfigValidator | None = None,
        serializer: ConfigSerializer | None = None,
    ) -> None:
        super().__init__()
        self.group = group
        self.key = key
        self.validator = validator or ConfigValidator()
        self.serializer = serializer or ConfigSerializer()
        self.default = _copy_config_value(self.validator.correct(_copy_config_value(default)))
        self._value = _copy_config_value(self.default)

    # -- accessors ----------------------------------------------------------

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, new_value: Any) -> None:
        self.setValue(new_value)

    def setValue(self, new_value: Any) -> None:
        if not self.validator.validate(new_value):
            new_value = self.validator.correct(new_value)
        if new_value == self._value:
            return
        self._value = new_value
        self.valueChanged.emit(new_value)

    def reset(self) -> None:
        self.setValue(_copy_config_value(self.default))

    # -- serialization ------------------------------------------------------

    def toRaw(self) -> Any:
        return self.serializer.serialize(self._value)

    def fromRaw(self, raw: Any) -> None:
        self.setValue(self.serializer.deserialize(raw))

    # -- identity -----------------------------------------------------------

    @property
    def qualifiedKey(self) -> str:
        return f"{self.group}.{self.key}"

    def __repr__(self) -> str:  # pragma: no cover - debug only
        return f"ConfigItem({self.group}.{self.key}={self._value!r})"


class RangeConfigItem(ConfigItem):
    """Convenience: numeric :class:`ConfigItem` backed by :class:`RangeValidator`."""

    def __init__(self, group: str, key: str, default: float, validator: RangeValidator,
                 serializer: ConfigSerializer | None = None) -> None:
        if not isinstance(validator, RangeValidator):
            raise TypeError("RangeConfigItem requires RangeValidator")
        super().__init__(group, key, default, validator, serializer)

    @property
    def range(self) -> tuple[float, float]:
        v: RangeValidator = self.validator  # type: ignore[assignment]
        return (v.min, v.max)


class OptionsConfigItem(ConfigItem):
    """Convenience: :class:`ConfigItem` backed by :class:`OptionsValidator`."""

    def __init__(self, group: str, key: str, default: Any, validator: OptionsValidator,
                 serializer: ConfigSerializer | None = None) -> None:
        if not isinstance(validator, OptionsValidator):
            raise TypeError("OptionsConfigItem requires OptionsValidator")
        super().__init__(group, key, default, validator, serializer)

    @property
    def options(self) -> Sequence[Any]:
        v: OptionsValidator = self.validator  # type: ignore[assignment]
        return list(v.options)


class ColorConfigItem(ConfigItem):
    """Convenience: ``QColor`` :class:`ConfigItem` with :class:`ColorSerializer`."""

    def __init__(self, group: str, key: str, default: Any) -> None:
        if isinstance(default, str):
            default = QColor(default)
        super().__init__(group, key, default, validator=ConfigValidator(), serializer=ColorSerializer())


# ---------------------------------------------------------------------------
# BreezeConfig
# ---------------------------------------------------------------------------

class BreezeConfig(QObject):
    """Container for :class:`ConfigItem` declarations with JSON persistence.

    Subclass and declare :class:`ConfigItem` instances as class attributes.
    The first instance constructed walks the class hierarchy, collects them,
    and keeps per-instance copies so two ``BreezeConfig`` instances with
    different files do not share value state.

    JSON layout: ``{group: {key: serialized_value}}``.

    ``valueChanged(group, key, value)`` is emitted for every change.
    """

    valueChanged = Signal(str, str, object)

    def __init__(self, file: Path | str | None = None, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._file: Path | None = Path(file) if file else None
        self._items: dict[str, ConfigItem] = {}
        self._collect_items()

    # -- item discovery -----------------------------------------------------

    def _collect_items(self) -> None:
        seen: dict[str, ConfigItem] = {}
        for cls in type(self).mro():
            for attr_name, attr in cls.__dict__.items():
                if isinstance(attr, ConfigItem) and attr_name not in seen:
                    instance_item = self._clone_item(attr)
                    seen[attr_name] = instance_item
                    setattr(self, attr_name, instance_item)
                    self._items[instance_item.qualifiedKey] = instance_item
                    instance_item.valueChanged.connect(
                        lambda v, item=instance_item: self.valueChanged.emit(item.group, item.key, v)
                    )

    @staticmethod
    def _clone_item(template: ConfigItem) -> ConfigItem:
        clone = ConfigItem.__new__(type(template))
        ConfigItem.__init__(
            clone,
            template.group,
            template.key,
            template.default,
            template.validator,
            template.serializer,
        )
        return clone

    # -- public API ---------------------------------------------------------

    def items(self) -> dict[str, ConfigItem]:
        return dict(self._items)

    def get(self, item: ConfigItem) -> Any:
        return self._lookup(item).value

    def set(self, item: ConfigItem, value: Any) -> None:
        self._lookup(item).setValue(value)

    def reset(self) -> None:
        for it in self._items.values():
            it.reset()

    def file(self) -> Path | None:
        return self._file

    def setFile(self, file: Path | str | None) -> None:
        self._file = Path(file) if file else None

    def load(self, file: Path | str | None = None) -> bool:
        """Load values from JSON file. Returns ``True`` on success.

        Missing file is not an error — existing defaults remain.
        Unknown groups/keys in the file are ignored.
        """
        target = Path(file) if file else self._file
        if target is None or not target.is_file():
            return False
        try:
            data = json.loads(target.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return False
        if not isinstance(data, dict):
            return False
        for group, entries in data.items():
            if not isinstance(entries, dict):
                continue
            for key, raw in entries.items():
                qkey = f"{group}.{key}"
                item = self._items.get(qkey)
                if item is not None:
                    item.fromRaw(raw)
        return True

    def save(self, file: Path | str | None = None) -> bool:
        """Write values to JSON file. Returns ``True`` on success."""
        target = Path(file) if file else self._file
        if target is None:
            return False
        payload: dict[str, dict[str, Any]] = {}
        for it in self._items.values():
            payload.setdefault(it.group, {})[it.key] = it.toRaw()
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        except OSError:
            return False
        return True

    # -- internals ----------------------------------------------------------

    def _lookup(self, item: ConfigItem) -> ConfigItem:
        own = self._items.get(item.qualifiedKey)
        if own is None:
            raise KeyError(f"ConfigItem {item.qualifiedKey!r} not registered on {type(self).__name__}")
        return own


__all__ = [
    "BreezeConfig",
    "ConfigItem",
    "RangeConfigItem",
    "OptionsConfigItem",
    "ColorConfigItem",
    "ConfigValidator",
    "RangeValidator",
    "OptionsValidator",
    "BoolValidator",
    "FolderValidator",
    "FolderListValidator",
    "ConfigSerializer",
    "ColorSerializer",
    "EnumSerializer",
]
