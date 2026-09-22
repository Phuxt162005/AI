import pytest

from database.models.agent import (
    Agent,
    AgentConfiguration,
    AgentExecution,
    AgentStatus,
    AgentTask,
    AgentTool,
    ExecutionResult,
    ExecutionStatus,
    Goal,
    Plan,
    PlanStep,
    Tool,
    ToolCall,
)

def test_agent():
    agent = Agent(agent_id=1, name="Assistant")
    assert agent.agent_id == 1
    assert agent.status == AgentStatus.ACTIVE

def test_agent_configuration():
    config = AgentConfiguration(
        agent_id=1,
        model_id="model-v1",
        max_steps=20,
        temperature=0.5,
        timeout=120,
    )
    assert config.max_steps == 20
    assert config.memory_enabled is True

def test_goal():
    goal = Goal(
        goal_id=1,
        agent_id=1,
        description="Answer user",
    )
    assert goal.agent_id == 1

def test_task():
    task = AgentTask(
        task_id=1,
        agent_id=1,
        goal_id=1,
        conversation_id=10,
        description="Find information",
    )
    assert task.goal_id == 1
    assert task.conversation_id == 10

def test_plan_and_step():
    plan = Plan(plan_id=1, task_id=1, name="Research plan")
    step = PlanStep(
        plan_step_id=1,
        plan_id=plan.plan_id or 1,
        step_index=0,
        description="Search data",
    )
    assert step.plan_id == 1

def test_execution():
    execution = AgentExecution(
        execution_id=1,
        task_id=1,
        status=ExecutionStatus.RUNNING,
    )
    assert execution.status == ExecutionStatus.RUNNING

def test_tool():
    tool = Tool(
        tool_id=1,
        name="search",
        description="Search information",
        input_schema={
            "type": "object",
        },
    )
    assert tool.enabled is True

def test_agent_tool():
    relation = AgentTool(agent_id=1, tool_id=1)
    assert relation.enabled is True

def test_tool_call():
    call = ToolCall(
        tool_call_id=1,
        execution_id=1,
        agent_id=1,
        task_id=1,
        tool_id=1,
    )
    assert call.attempt == 1

def test_execution_result():
    result = ExecutionResult(
        result_id=1,
        tool_call_id=1,
        success=True,
        output_data={
            "value": 42,
        },
    )
    assert result.success is True

def test_invalid_agent():
    with pytest.raises(ValueError):
        Agent(
            agent_id=1,
            name="",
        )


def test_invalid_configuration():
    with pytest.raises(ValueError):
        AgentConfiguration(
            agent_id=1,
            model_id="model",
            max_steps=0,
        )