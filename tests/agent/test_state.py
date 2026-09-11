"""Tests for Agent state."""

from core.types import InputData, InputType

from self_built.agent.state import (
    AgentState,
    AgentTermination,
    Observation,
    ObservationStatus,
)


def create_input() -> InputData:
    return InputData(
        type=InputType.TEXT,
        content="Hello",
    )


def test_observation_success() -> None:
    observation = Observation(
        action="tool",
        status=ObservationStatus.SUCCESS,
        result=42,
        step_id=0,
    )

    assert observation.action == "tool"
    assert observation.status == ObservationStatus.SUCCESS
    assert observation.result == 42
    assert observation.error is None


def test_observation_error() -> None:
    observation = Observation(
        action="math",
        status=ObservationStatus.ERROR,
        error="Division by zero",
    )

    assert observation.status == ObservationStatus.ERROR
    assert observation.error == "Division by zero"


def test_state_add_observation() -> None:
    state = AgentState(input_data=create_input())

    observation = Observation(
        action="tool",
        status=ObservationStatus.SUCCESS,
        result=10,
    )

    state.add_observation(observation)

    assert len(state.observations) == 1
    assert state.observations[0] is observation


def test_state_add_history() -> None:
    state = AgentState(input_data=create_input())

    state.add_history(
        {
            "event": "test",
        }
    )

    assert state.history == [
        {
            "event": "test",
        }
    ]


def test_state_can_continue() -> None:
    state = AgentState(input_data=create_input())

    assert state.can_continue(10) is True

    state.step_count = 10

    assert state.can_continue(10) is False


def test_state_complete() -> None:
    state = AgentState(input_data=create_input())

    state.complete(result="done")

    assert state.completed is True
    assert state.failed is False
    assert state.termination == AgentTermination.COMPLETED
    assert state.result == "done"


def test_state_fail() -> None:
    state = AgentState(input_data=create_input())

    state.fail(
        result="failed",
        termination=AgentTermination.ERROR,
    )

    assert state.completed is False
    assert state.failed is True
    assert state.termination == AgentTermination.ERROR
    assert state.result == "failed"