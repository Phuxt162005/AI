"""Tests for ToolExecutor."""

import pytest

from core.interfaces import ToolInterface

from self_built.tools.executor import (
    ToolExecutionError,
    ToolExecutor,
)
from self_built.tools.registry import ToolRegistry


class EchoTool(ToolInterface):
    @property
    def name(self) -> str:
        return "echo"

    @property
    def description(self) -> str:
        return "Returns the provided value."

    def execute(self, inputs: dict[str, object]) -> object:
        return inputs.get("value")


class FailingTool(ToolInterface):
    @property
    def name(self) -> str:
        return "failing"

    @property
    def description(self) -> str:
        return "Always fails."

    def execute(self, inputs: dict[str, object]) -> object:
        raise RuntimeError("intentional failure")


def test_execute_registered_tool() -> None:
    registry = ToolRegistry()
    registry.register(EchoTool())

    executor = ToolExecutor(registry)

    result = executor.execute(
        "echo",
        {"value": "hello"},
    )

    assert result == "hello"


def test_execute_unknown_tool_fails() -> None:
    registry = ToolRegistry()
    executor = ToolExecutor(registry)

    with pytest.raises(KeyError, match="unknown"):
        executor.execute(
            "unknown",
            {},
        )


def test_execute_requires_dictionary() -> None:
    registry = ToolRegistry()
    registry.register(EchoTool())

    executor = ToolExecutor(registry)

    with pytest.raises(TypeError, match="dictionary"):
        executor.execute(
            "echo",
            "invalid",  # type: ignore[arg-type]
        )


def test_tool_failure_is_wrapped() -> None:
    registry = ToolRegistry()
    registry.register(FailingTool())

    executor = ToolExecutor(registry)

    with pytest.raises(
        ToolExecutionError,
        match="failed during execution",
    ):
        executor.execute(
            "failing",
            {},
        )


def test_executor_exposes_registry() -> None:
    registry = ToolRegistry()
    executor = ToolExecutor(registry)

    assert executor.registry is registry