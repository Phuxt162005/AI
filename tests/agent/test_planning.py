"""Tests for ProjectAI Agent Understanding & Planning."""

from core.types import InputData, InputType

from self_built.agent_planning import (
    ActionType,
    AgentPlanner,
    Complexity,
    DecisionEngine,
    Intent,
    Plan,
    RequestUnderstanding,
    StepStatus,
    TaskDecomposer,
)


def text_input(content: str) -> InputData:
    return InputData(
        type=InputType.TEXT,
        content=content,
    )


def test_understanding_chat() -> None:
    understanding = RequestUnderstanding().understand(
        text_input("Hello, how are you?")
    )

    assert understanding.intent == Intent.CHAT
    assert understanding.complexity == Complexity.SIMPLE
    assert understanding.requires_ai_core is True
    assert understanding.requires_tool is False


def test_understanding_question() -> None:
    understanding = RequestUnderstanding().understand(
        text_input("What is machine learning?")
    )

    assert understanding.intent == Intent.QUESTION
    assert understanding.requires_ai_core is True


def test_understanding_calculation() -> None:
    understanding = RequestUnderstanding().understand(
        text_input("Calculate 25 * 4")
    )

    assert understanding.intent == Intent.CALCULATION
    assert understanding.requires_tool is True
    assert understanding.requires_ai_core is False
    assert understanding.complexity == Complexity.MODERATE


def test_understanding_search() -> None:
    understanding = RequestUnderstanding().understand(
        text_input("Search for information about MQTT")
    )

    assert understanding.intent == Intent.SEARCH
    assert understanding.requires_tool is True
    assert understanding.complexity == Complexity.MODERATE


def test_understanding_multi_step() -> None:
    understanding = RequestUnderstanding().understand(
        text_input("Search for MQTT and then calculate the result")
    )

    assert understanding.intent == Intent.MULTI_STEP
    assert understanding.complexity == Complexity.COMPLEX
    assert understanding.requires_tool is True
    assert understanding.requires_ai_core is True


def test_understanding_memory_requirement() -> None:
    understanding = RequestUnderstanding().understand(
        text_input("Do you remember what we discussed last time?")
    )

    assert understanding.requires_memory is True


def test_empty_input_becomes_unknown() -> None:
    understanding = RequestUnderstanding().understand(
        text_input("   ")
    )

    assert understanding.intent == Intent.UNKNOWN
    assert understanding.complexity == Complexity.SIMPLE
    assert understanding.metadata["reason"] == "empty_request"


def test_text_input_requires_string_content() -> None:
    invalid_input = InputData(
        type=InputType.TEXT,
        content=123,
    )

    try:
        RequestUnderstanding().understand(invalid_input)
    except TypeError as exc:
        assert "TEXT input content must be a string" in str(exc)
    else:
        raise AssertionError("Expected TypeError for invalid TEXT input.")


def test_chat_plan() -> None:
    understanding = RequestUnderstanding().understand(
        text_input("Hello")
    )

    plan = TaskDecomposer().decompose(understanding)

    assert len(plan.steps) == 1
    assert plan.steps[0].action == ActionType.AI_CORE
    assert plan.steps[0].status == StepStatus.PENDING


def test_question_plan_with_memory() -> None:
    understanding = RequestUnderstanding().understand(
        text_input("Do you remember the previous discussion?")
    )

    plan = TaskDecomposer().decompose(understanding)

    assert len(plan.steps) == 2
    assert plan.steps[0].action == ActionType.DIRECT
    assert plan.steps[0].metadata["resource"] == "memory"
    assert plan.steps[1].action == ActionType.AI_CORE


def test_calculation_plan() -> None:
    understanding = RequestUnderstanding().understand(
        text_input("Calculate 10 + 20")
    )

    plan = TaskDecomposer().decompose(understanding)

    assert len(plan.steps) == 2
    assert plan.steps[0].action == ActionType.TOOL
    assert plan.steps[0].tool_name == "math"
    assert plan.steps[1].action == ActionType.AI_CORE


def test_search_plan() -> None:
    understanding = RequestUnderstanding().understand(
        text_input("Search for MQTT")
    )

    plan = TaskDecomposer().decompose(understanding)

    assert len(plan.steps) == 2
    assert plan.steps[0].action == ActionType.TOOL
    assert plan.steps[0].tool_name == "search"
    assert plan.steps[1].action == ActionType.AI_CORE


def test_multi_step_plan() -> None:
    understanding = RequestUnderstanding().understand(
        text_input("Search for MQTT and then calculate the result")
    )

    plan = TaskDecomposer().decompose(understanding)

    assert len(plan.steps) == 3
    assert plan.steps[0].tool_name == "search"
    assert plan.steps[1].tool_name == "math"
    assert plan.steps[2].action == ActionType.AI_CORE


def test_unknown_plan_requests_clarification() -> None:
    understanding = RequestUnderstanding().understand(
        text_input("")
    )

    plan = TaskDecomposer().decompose(understanding)

    assert len(plan.steps) == 1
    assert plan.steps[0].action == ActionType.CLARIFY


def test_plan_add_step() -> None:
    plan = Plan(goal="Test task")

    step = plan.add_step(
        description="Test step",
        action=ActionType.AI_CORE,
    )

    assert step.step_id == 0
    assert plan.steps[0] is step
    assert plan.is_empty is False
    assert plan.is_finished is False


def test_plan_progression() -> None:
    plan = Plan(goal="Test task")
    plan.add_step("Step 1", ActionType.AI_CORE)
    plan.add_step("Step 2", ActionType.DIRECT)

    assert plan.current_step == 0
    assert plan.completed is False

    plan.mark_current_completed()

    assert plan.steps[0].status == StepStatus.COMPLETED
    assert plan.current_step == 1
    assert plan.completed is False

    plan.mark_current_completed()

    assert plan.steps[1].status == StepStatus.COMPLETED
    assert plan.current_step == 2
    assert plan.completed is True
    assert plan.is_finished is True


def test_decision_engine_selects_current_step() -> None:
    understanding = RequestUnderstanding().understand(
        text_input("Calculate 2 + 2")
    )
    plan = TaskDecomposer().decompose(understanding)

    decision = DecisionEngine().decide(
        understanding,
        plan,
    )

    assert decision["action"] == ActionType.TOOL.value
    assert decision["tool_name"] == "math"
    assert decision["step_id"] == 0


def test_decision_for_unknown_request() -> None:
    understanding = RequestUnderstanding().understand(
        text_input("")
    )
    plan = TaskDecomposer().decompose(understanding)

    decision = DecisionEngine().decide(
        understanding,
        plan,
    )

    assert decision["action"] == ActionType.CLARIFY.value


def test_decision_after_plan_completion() -> None:
    understanding = RequestUnderstanding().understand(
        text_input("Hello")
    )
    plan = TaskDecomposer().decompose(understanding)

    plan.mark_current_completed()

    decision = DecisionEngine().decide(
        understanding,
        plan,
    )

    assert decision["action"] == ActionType.DIRECT.value


def test_agent_planner_facade() -> None:
    planner = AgentPlanner()

    result = planner.process(
        text_input("Calculate 5 * 6")
    )

    assert result["understanding"].intent == Intent.CALCULATION
    assert result["plan"].steps[0].tool_name == "math"
    assert result["decision"]["action"] == ActionType.TOOL.value


def test_agent_planner_is_deterministic() -> None:
    planner = AgentPlanner()

    first = planner.process(
        text_input("Search for MQTT")
    )
    second = planner.process(
        text_input("Search for MQTT")
    )

    assert first["understanding"] == second["understanding"]
    assert first["plan"].steps[0].action == second["plan"].steps[0].action
    assert first["decision"] == second["decision"]