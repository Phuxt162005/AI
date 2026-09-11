"""Tests for ProjectAI Agent Loop."""

import pytest

from core.ai_core import AICoreService
from core.interfaces import MemoryInterface
from core.types import InputData, InputType, OutputData

from self_built.agent import (
    AgentState,
    AgentTermination,
    ObservationStatus,
    ProjectAgent,
)
from self_built.agent_planning import AgentPlanner
from self_built.tools import ToolExecutor, ToolRegistry


class FakeRuntime:
    """Minimal AI Core runtime for tests."""

    def __init__(self) -> None:
        self.is_ready = True
        self.calls: list[str] = []

    def load(self, source: str | None = None) -> None:
        self.is_ready = True

    def save(self, destination: str) -> None:
        pass

    def predict(self, inputs: object) -> object:
        self.calls.append(str(inputs))
        return f"AI:{inputs}"

    def metadata(self) -> dict[str, object]:
        return {
            "name": "fake",
        }


class FakeMemory(MemoryInterface):
    """Simple memory implementation for Agent tests."""

    def __init__(self) -> None:
        self.values: dict[str, object] = {
            "last_input": "previous context"
        }

    def store(self, key: str, value: object) -> None:
        self.values[key] = value

    def retrieve(self, key: str) -> object:
        return self.values[key]

    def update(self, key: str, value: object) -> None:
        self.values[key] = value

    def delete(self, key: str) -> None:
        del self.values[key]


class FailingMemory(MemoryInterface):
    """Memory implementation that always fails."""

    def store(self, key: str, value: object) -> None:
        raise RuntimeError("memory failure")

    def retrieve(self, key: str) -> object:
        raise RuntimeError("memory failure")

    def update(self, key: str, value: object) -> None:
        raise RuntimeError("memory failure")

    def delete(self, key: str) -> None:
        raise RuntimeError("memory failure")


def build_ai_core() -> AICoreService:
    from core.ai_core import ModelManager, ModelRuntime

    manager = ModelManager()
    runtime = ModelRuntime(
        model=FakeRuntime(),
        name="fake",
    )
    manager.register("fake", runtime)

    return AICoreService(manager)


def build_agent(
    *,
    memory: MemoryInterface | None = None,
    max_steps: int = 10,
) -> ProjectAgent:
    registry = ToolRegistry()
    executor = ToolExecutor(registry)

    return ProjectAgent(
        planner=AgentPlanner(),
        tool_executor=executor,
        ai_core=build_ai_core(),
        memory=memory,
        model_name="fake",
        max_steps=max_steps,
    )


def text_input(text: str) -> InputData:
    return InputData(
        type=InputType.TEXT,
        content=text,
    )


def test_agent_implements_interface() -> None:
    from core.interfaces import AgentInterface

    agent = build_agent()

    assert isinstance(agent, AgentInterface)


def test_agent_process_chat_uses_ai_core() -> None:
    agent = build_agent()

    output = agent.process(
        text_input("Hello")
    )

    assert isinstance(output, OutputData)
    assert output.content.startswith("AI:")
    assert agent.last_state is not None
    assert agent.last_state.completed is True
    assert agent.last_state.termination == AgentTermination.COMPLETED


def test_agent_decide_delegates_to_planner() -> None:
    agent = build_agent()

    understanding = agent.planner.analyze(
        text_input("Hello")
    )
    plan = agent.planner.create_plan(
        understanding
    )

    decision = agent.decide(
        {
            "understanding": understanding,
            "plan": plan,
        }
    )

    assert decision["action"] == "ai_core"


def test_agent_uses_memory() -> None:
    memory = FakeMemory()
    agent = build_agent(memory=memory)

    output = agent.process(
        text_input(
            "Do you remember what we discussed last time?"
        )
    )

    assert isinstance(output, OutputData)
    assert agent.last_state is not None
    assert len(agent.last_state.observations) == 2

    first = agent.last_state.observations[0]

    assert first.status == ObservationStatus.SUCCESS
    assert first.result == "previous context"


def test_agent_memory_failure_is_handled() -> None:
    agent = build_agent(
        memory=FailingMemory(),
    )

    output = agent.process(
        text_input(
            "Do you remember what we discussed last time?"
        )
    )

    assert isinstance(output, OutputData)
    assert agent.last_state is not None
    assert agent.last_state.failed is True
    assert agent.last_state.termination == AgentTermination.ERROR


def test_agent_calculation_uses_math_tool() -> None:
    from self_built.tools import MathTool

    registry = ToolRegistry()
    registry.register(MathTool())

    agent = ProjectAgent(
        planner=AgentPlanner(),
        tool_executor=ToolExecutor(registry),
        ai_core=build_ai_core(),
        model_name="fake",
    )

    output = agent.process(
        text_input("Calculate 25 * 4")
    )

    assert isinstance(output, OutputData)
    assert output.content.startswith("AI:")
    assert agent.last_state is not None
    assert agent.last_state.completed is True

    observations = agent.last_state.observations

    assert len(observations) == 2
    assert observations[0].action == "tool"
    assert observations[0].result == 100
    assert observations[1].action == "ai_core"


def test_agent_unknown_tool_is_handled() -> None:
    agent = build_agent()

    output = agent.process(
        text_input("Search for MQTT")
    )

    assert isinstance(output, OutputData)
    assert agent.last_state is not None
    assert agent.last_state.failed is True
    assert agent.last_state.termination == AgentTermination.ERROR


def test_agent_tool_failure_is_handled() -> None:
    from core.interfaces import ToolInterface

    class FailingTool(ToolInterface):
        @property
        def name(self) -> str:
            return "math"

        @property
        def description(self) -> str:
            return "Failing math tool."

        def execute(
            self,
            inputs: dict[str, object],
        ) -> object:
            raise RuntimeError("tool failure")

    registry = ToolRegistry()
    registry.register(FailingTool())

    agent = ProjectAgent(
        planner=AgentPlanner(),
        tool_executor=ToolExecutor(registry),
        ai_core=build_ai_core(),
        model_name="fake",
    )

    output = agent.process(
        text_input("Calculate 2 + 2")
    )

    assert isinstance(output, OutputData)
    assert agent.last_state is not None
    assert agent.last_state.failed is True
    assert agent.last_state.termination == AgentTermination.ERROR


def test_agent_requires_ai_core_for_ai_action() -> None:
    registry = ToolRegistry()

    agent = ProjectAgent(
        planner=AgentPlanner(),
        tool_executor=ToolExecutor(registry),
    )

    output = agent.process(
        text_input("Hello")
    )

    assert isinstance(output, OutputData)
    assert agent.last_state is not None
    assert agent.last_state.failed is True


def test_agent_requires_model_name_for_ai_core() -> None:
    registry = ToolRegistry()

    agent = ProjectAgent(
        planner=AgentPlanner(),
        tool_executor=ToolExecutor(registry),
        ai_core=build_ai_core(),
    )

    output = agent.process(
        text_input("Hello")
    )

    assert isinstance(output, OutputData)
    assert agent.last_state is not None
    assert agent.last_state.failed is True


def test_agent_max_steps_terminates() -> None:
    from self_built.tools import MathTool

    registry = ToolRegistry()
    registry.register(MathTool())

    agent = ProjectAgent(
        planner=AgentPlanner(),
        tool_executor=ToolExecutor(registry),
        ai_core=build_ai_core(),
        model_name="fake",
        max_steps=1,
    )

    output = agent.process(
        text_input("Calculate 25 * 4")
    )

    assert isinstance(output, OutputData)
    assert agent.last_state is not None
    assert agent.last_state.failed is True
    assert (
        agent.last_state.termination
        == AgentTermination.MAX_STEPS
    )
    assert agent.last_state.step_count == 1


def test_agent_observations_are_recorded() -> None:
    from self_built.tools import MathTool

    registry = ToolRegistry()
    registry.register(MathTool())

    agent = ProjectAgent(
        planner=AgentPlanner(),
        tool_executor=ToolExecutor(registry),
        ai_core=build_ai_core(),
        model_name="fake",
    )

    agent.process(
        text_input("Calculate 10 + 20")
    )

    assert agent.last_state is not None
    assert len(agent.last_state.observations) == 2

    assert (
        agent.last_state.observations[0].status
        == ObservationStatus.SUCCESS
    )

    assert (
        agent.last_state.observations[1].status
        == ObservationStatus.SUCCESS
    )


def test_agent_history_is_recorded() -> None:
    agent = build_agent()

    agent.process(
        text_input("Hello")
    )

    assert agent.last_state is not None

    events = [
        item["event"]
        for item in agent.last_state.history
    ]

    assert "understanding" in events
    assert "plan_created" in events
    assert "decision" in events
    assert "ai_core_execution" in events


def test_agent_invalid_max_steps() -> None:
    registry = ToolRegistry()

    with pytest.raises(ValueError):
        ProjectAgent(
            planner=AgentPlanner(),
            tool_executor=ToolExecutor(registry),
            max_steps=0,
        )


def test_agent_invalid_input() -> None:
    agent = build_agent()

    with pytest.raises(TypeError):
        agent.process("Hello")  # type: ignore[arg-type]


def test_agent_respond_wraps_result() -> None:
    agent = build_agent()

    output = agent.respond("hello")

    assert isinstance(output, OutputData)
    assert output.content == "hello"
    assert output.type.value == "text"