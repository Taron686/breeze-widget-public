from enum import Enum

from PySide6.QtCore import QObject

from breezewidget import BreezeConfig, ColorConfigItem, ConfigItem, EnumSerializer


def test_nested_defaults_are_independent(qapp):
    original = {"paths": []}

    class Settings(BreezeConfig):
        paths = ConfigItem("App", "Paths", original)

    first, second = Settings(), Settings()
    first.paths.value["paths"].append("first")
    assert second.paths.value == {"paths": []}
    assert first.paths.default == {"paths": []}
    assert Settings.paths.default == {"paths": []}
    assert original == {"paths": []}


def test_reset_creates_a_fresh_value_each_time(qapp):
    item = ConfigItem("App", "Paths", [])
    seen = []
    item.valueChanged.connect(lambda value: seen.append(list(value)))
    for _ in range(2):
        item.value.append("changed")
        item.reset()
        assert item.value == []
        assert item.default == []
        assert item.value is not item.default
    assert seen == [[], []]
    item.reset()
    assert seen == [[], []]


def test_color_default_is_independent(qapp):
    class Settings(BreezeConfig):
        accent = ColorConfigItem("App", "Accent", "#0067c0")

    first, second = Settings(), Settings()
    first.accent.value.setRgb(255, 0, 0)
    assert second.accent.value.name() == "#0067c0"
    assert first.accent.default.name() == "#0067c0"
    first.accent.reset()
    assert first.accent.value.name() == "#0067c0"


def test_tuple_keeps_shared_children_without_sharing_default(qapp):
    child = []
    item = ConfigItem("App", "Tuple", (child, child))
    item.value[0].append("value")
    assert item.value[0] is item.value[1]
    assert item.default == ([], [])
    assert child == []


def test_recursive_container_can_be_copied(qapp):
    child = []
    original = (child,)
    child.append(original)
    item = ConfigItem("App", "Recursive", original)
    assert item.value is not original
    assert item.value[0][0] is item.value
    assert item.default[0][0] is item.default


def test_enum_and_resource_defaults_keep_identity(qapp):
    class Mode(Enum):
        LIGHT = "light"

    resource = QObject()
    item = ConfigItem("App", "Resource", {"resource": resource})
    assert item.value["resource"] is resource
    mode = ConfigItem("App", "Mode", Mode.LIGHT, serializer=EnumSerializer(Mode))
    assert mode.value is Mode.LIGHT
    assert mode.toRaw() == "LIGHT"
