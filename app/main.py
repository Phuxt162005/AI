"""ProjectAI application entry point."""

from __future__ import annotations

from core.config import AppConfig
from core.logger import configure_logging
from core.types import InputData, InputType
from self_built.foundation import (
    EchoModel,
    EchoTool,
    FoundationAgent,
    InMemoryMemory,
)

def build_application() -> FoundationAgent:
    """Build the temporary foundation application."""

    config = AppConfig.load("config.json")
    configure_logging(config.log_level)
    model = EchoModel()
    model.load()
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