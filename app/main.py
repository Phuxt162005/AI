"""ProjectAI application entry point."""

from typing import Any

from core.config import AppConfig
from core.interfaces import (
    AgentInterface,
    MemoryInterface,
    ModelInterface,
    ToolInterface,
)
from core.logger import configure_logging
from core.types import InputData, InputType, OutputData, OutputType


class EchoModel(ModelInterface):
    """Temporary model used to test the foundation."""

    def __init__(self) -> None:
        self.loaded = False

    def load(self, source: str | None = None) -> None:
        self.loaded = True

    def save(self, destination: str) -> None:
        with open(destination, "w", encoding="utf-8") as file:
            file.write("foundation-placeholder")

    def predict(self, inputs: Any) -> Any:
        if not self.loaded:
            self.load()

        return inputs

    def metadata(self) -> dict[str, Any]:
        return {
            "name": "EchoModel",
            "purpose": "Foundation integration test",
        }


class InMemoryMemory(MemoryInterface):
    """Temporary in-memory storage for foundation testing."""

    def __init__(self) -> None:
        self._storage: dict[str, Any] = {}

    def store(self, key: str, value: Any) -> None:
        self._storage[key] = value

    def retrieve(self, key: str) -> Any:
        return self._storage.get(key)

    def update(self, key: str, value: Any) -> None:
        if key not in self._storage:
            raise KeyError(key)

        self._storage[key] = value

    def delete(self, key: str) -> None:
        self._storage.pop(key, None)


class EchoTool(ToolInterface):
    """Temporary tool used to test Agent-tool communication."""

    @property
    def name(self) -> str:
        return "echo"

    @property
    def description(self) -> str:
        return "Returns the provided value."

    def execute(self, inputs: dict[str, Any]) -> Any:
        return inputs.get("value")


class FoundationAgent(AgentInterface):
    """Temporary Agent for testing the initial architecture."""

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


def build_application() -> FoundationAgent:
    """Build the temporary foundation application."""

    config = AppConfig.load("config.json")

    configure_logging(config.log_level)

    model = EchoModel()
    memory = InMemoryMemory()
    tool = EchoTool()

    return FoundationAgent(
        model=model,
        memory=memory,
        tool=tool,
    )


def main() -> None:
    """Run the foundation application."""

    agent = build_application()

    input_data = InputData(
        type=InputType.TEXT,
        content="Hello ProjectAI",
    )

    output = agent.process(input_data)

    print(output.content)


if __name__ == "__main__":
    main()