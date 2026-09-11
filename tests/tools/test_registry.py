"""Tests for ToolRegistry."""

import pytest

from core.interfaces import ToolInterface

from self_built.tools.registry import ToolRegistry

class DummyTool(ToolInterface):
    @property
    def name(self) -> str:
        return "dummy"

    @property
    def description(self) -> str:
        return "Dummy test tool."

    def execute(self, inputs: dict[str, object]) -> object:
        return inputs.get("value")

class AnotherTool(ToolInterface):
    @property
    def name(self) -> str:
        return "another"

    @property
    def description(self) -> str:
        return "Another test tool."

    def execute(self, inputs: dict[str, object]) -> object:
        return inputs

def test_register_and_get_tool() -> None:
    registry = ToolRegistry()
    tool = DummyTool()
    registry.register(tool)

    assert registry.has("dummy")
    assert registry.get("dummy") is tool

def test_register_duplicate_tool_fails() -> None:
    registry = ToolRegistry()
    registry.register(DummyTool())

    with pytest.raises(ValueError, match="already registered"):
        registry.register(DummyTool())

def test_register_invalid_object_fails() -> None:
    registry = ToolRegistry()

    with pytest.raises(TypeError, match="ToolInterface"):
        registry.register(object())

def test_get_missing_tool_fails() -> None:
    registry = ToolRegistry()

    with pytest.raises(KeyError, match="missing"):
        registry.get("missing")

def test_unregister_tool() -> None:
    registry = ToolRegistry()
    registry.register(DummyTool())
    registry.unregister("dummy")

    assert registry.has("dummy") is False

def test_unregister_missing_tool_fails() -> None:
    registry = ToolRegistry()

    with pytest.raises(KeyError):
        registry.unregister("missing")

def test_list_tools() -> None:
    registry = ToolRegistry()
    registry.register(DummyTool())
    registry.register(AnotherTool())

    assert registry.list() == ["dummy", "another"]

def test_tool_name_is_normalized() -> None:
    registry = ToolRegistry()
    tool = DummyTool()
    registry.register(tool)

    assert registry.get(" dummy ") is tool

def test_empty_tool_name_lookup_fails() -> None:
    registry = ToolRegistry()

    with pytest.raises(ValueError, match="must not be empty"):
        registry.get("   ")