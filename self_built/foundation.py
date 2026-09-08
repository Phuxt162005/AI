"""Temporary self-built components for ProjectAI foundation testing."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.interfaces import (
    AgentInterface,
    MemoryInterface,
    ModelInterface,
    ToolInterface,
)
from core.types import InputData, OutputData, OutputType


class EchoModel(ModelInterface):
    """Temporary model used only for foundation integration testing."""

    def __init__(self) -> None:
        self.loaded = False

    def load(self, source: str | None = None) -> None:
        self.loaded = True

    def save(self, destination: str) -> None:
        Path(destination).write_text(
            "foundation-placeholder",
            encoding="utf-8",
        )

    def predict(self, inputs: Any) -> Any:
        if not self.loaded:
            raise RuntimeError("Model must be loaded before prediction.")
        return inputs

    def metadata(self) -> dict[str, Any]:
        return {
            "name": "EchoModel",
            "purpose": "Foundation integration test",
        }

class InMemoryMemory(MemoryInterface):
    """Temporary in-memory storage used for foundation testing."""

    def __init__(self) -> None:
        self._storage: dict[str, Any] = {}

    def store(self, key: str, value: Any) -> None:
        self._storage[key] = value

    def retrieve(self, key: str) -> Any | None:
        return self._storage.get(key)

    def update(self, key: str, value: Any) -> None:
        if key not in self._storage:
            raise KeyError(key)

        self._storage[key] = value

    def delete(self, key: str) -> None:
        self._storage.pop(key, None)

class EchoTool(ToolInterface):
    """Temporary tool used only for foundation testing."""

    @property
    def name(self) -> str:
        return "echo"

    @property
    def description(self) -> str:
        return "Returns the provided value."

    def execute(self, inputs: dict[str, Any]) -> Any:
        return inputs.get("value")

class FoundationAgent(AgentInterface):
    """Temporary Agent used to test the initial integration pipeline."""

    def __init__(
        self,
        model: ModelInterface,
        memory: MemoryInterface,
        tool: ToolInterface,
    ) -> None:
        self.model = model
        self.memory = memory
        self.tool = tool

    def process(self, input_data: InputData) -> OutputData:
        context = {
            "input": input_data.content,
            "input_type": input_data.type.value,
        }

        decision = self.decide(context)

        if decision["action"] == "model":
            result = self.model.predict(input_data.content)
        elif decision["action"] == "tool":
            result = self.tool.execute(
                {"value": input_data.content}
            )
        else:
            result = input_data.content

        self.memory.store("last_input", input_data.content)
        return self.respond(result)

    def decide(self, context: dict[str, Any]) -> dict[str, Any]:
        return {
            "action": "model",
            "reason": "Foundation placeholder decision",
        }

    def respond(self, result: Any) -> OutputData:
        return OutputData(
            type=OutputType.TEXT,
            content=str(result),
        )