"""Tests for ProjectAI System Integration."""

from core.ai_core import AICoreService, ModelManager, ModelRuntime
from core.interfaces import ModelInterface
from core.types import InputData, InputType, OutputData

from self_built.agent import ProjectAgent
from self_built.agent_planning import AgentPlanner
from self_built.integration import SystemIntegration
from self_built.tools import ToolExecutor, ToolRegistry


class FakeModel(ModelInterface):
    """Minimal model implementation for integration tests."""

    def load(self, source: str | None = None) -> None:
        pass

    def save(self, destination: str) -> None:
        pass

    def predict(self, inputs: object) -> object:
        return f"AI:{inputs}"

    def metadata(self) -> dict[str, object]:
        return {
            "name": "fake",
        }


def build_ai_core() -> AICoreService:
    """Build a minimal AI Core for integration tests."""

    manager = ModelManager()

    runtime = ModelRuntime(
        model=FakeModel(),
    )

    runtime.load()

    manager.register(
        "fake",
        runtime,
    )

    return AICoreService(manager)


def build_agent() -> ProjectAgent:
    """Build a minimal ProjectAI Agent."""

    registry = ToolRegistry()

    return ProjectAgent(
        planner=AgentPlanner(),
        tool_executor=ToolExecutor(registry),
        ai_core=build_ai_core(),
        model_name="fake",
    )


def create_input(text: str) -> InputData:
    """Create a text input."""

    return InputData(
        type=InputType.TEXT,
        content=text,
    )


def test_system_integration_requires_agent() -> None:
    """SystemIntegration must require a ProjectAgent."""

    try:
        SystemIntegration(None)  # type: ignore[arg-type]
    except TypeError:
        return

    raise AssertionError(
        "SystemIntegration must reject an invalid Agent."
    )


def test_system_integration_exposes_agent() -> None:
    """SystemIntegration must expose the configured Agent."""

    agent = build_agent()
    system = SystemIntegration(agent)

    assert system.agent is agent


def test_system_integration_processes_input() -> None:
    """Input must flow through Agent and return OutputData."""

    system = SystemIntegration(
        build_agent(),
    )

    output = system.process(
        create_input("Hello"),
    )

    assert isinstance(output, OutputData)
    assert output.content.startswith("AI:")


def test_system_integration_rejects_invalid_input() -> None:
    """SystemIntegration must reject non-InputData values."""

    system = SystemIntegration(
        build_agent(),
    )

    try:
        system.process("Hello")  # type: ignore[arg-type]
    except TypeError:
        return

    raise AssertionError(
        "SystemIntegration must reject invalid input."
    )


def test_system_integration_preserves_agent_result() -> None:
    """Integration must return the Agent's output unchanged."""

    agent = build_agent()
    system = SystemIntegration(agent)

    input_data = create_input("Hello")
    output = system.process(input_data)

    assert agent.last_state is not None
    assert agent.last_state.completed is True
    assert isinstance(output, OutputData)