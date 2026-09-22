"""Repositories for Agent and Tool data."""

from __future__ import annotations

import json
from typing import Any

from database.access.data_access import DataAccess
from database.access.repository import (
    BaseRepository,
    EntityMapper,
)
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
    GoalStatus,
    Plan,
    PlanStep,
    TaskStatus,
    Tool,
    ToolCall,
    ToolCallStatus,
)

def _agent_from_row(row: Any) -> Agent:
    return Agent(
        agent_id=row.get("agent_id"),
        name=row["name"],
        description=row.get("description", ""),
        status=AgentStatus(
            row.get("status", "active")
        ),
    )

def _agent_to_row(entity: Agent) -> dict[str, Any]:
    row = {
        "name": entity.name,
        "description": entity.description,
        "status": entity.status.value,
    }

    if entity.agent_id is not None:
        row["agent_id"] = entity.agent_id

    return row

class AgentRepository(BaseRepository[Agent]):
    def __init__(self, data_access: DataAccess) -> None:
        mapper = EntityMapper[Agent](
            from_row=_agent_from_row,
            to_row=_agent_to_row,
        )

        super().__init__(
            data_access=data_access,
            table_name="agents",
            mapper=mapper,
            primary_key="agent_id",
        )

    def list_active(self) -> list[Agent]:
        rows = self.data_access.query(
            "SELECT * FROM `agents` "
            "WHERE `status` = %s "
            "ORDER BY `agent_id`",
            [AgentStatus.ACTIVE.value],
        )

        return [
            self.mapper.map_from_row(row)
            for row in rows
        ]

def _configuration_from_row(row: Any) -> AgentConfiguration:
    return AgentConfiguration(
        agent_id=row["agent_id"],
        model_id=row["model_id"],
        max_steps=row.get("max_steps", 10),
        temperature=row.get("temperature", 0.7),
        timeout=row.get("timeout", 60),
        system_prompt=row.get("system_prompt", ""),
        memory_enabled=bool(
            row.get("memory_enabled", True)
        ),
    )

def _configuration_to_row(entity: AgentConfiguration) -> dict[str, Any]:
    return {
        "agent_id": entity.agent_id,
        "model_id": entity.model_id,
        "max_steps": entity.max_steps,
        "temperature": entity.temperature,
        "timeout": entity.timeout,
        "system_prompt": entity.system_prompt,
        "memory_enabled": entity.memory_enabled,
    }


class AgentConfigurationRepository(BaseRepository[AgentConfiguration]):
    def __init__(self, data_access: DataAccess) -> None:
        mapper = EntityMapper[AgentConfiguration](
            from_row=_configuration_from_row,
            to_row=_configuration_to_row,
        )

        super().__init__(
            data_access=data_access,
            table_name="agent_configurations",
            mapper=mapper,
            primary_key="agent_id",
        )

def _goal_from_row(row: Any) -> Goal:
    return Goal(
        goal_id=row.get("goal_id"),
        agent_id=row["agent_id"],
        description=row["description"],
        status=GoalStatus(
            row.get("status", "pending")
        ),
    )

def _goal_to_row(entity: Goal) -> dict[str, Any]:
    row = {
        "agent_id": entity.agent_id,
        "description": entity.description,
        "status": entity.status.value,
    }

    if entity.goal_id is not None:
        row["goal_id"] = entity.goal_id

    return row

class GoalRepository(BaseRepository[Goal]):
    def __init__(self, data_access: DataAccess) -> None:
        mapper = EntityMapper[Goal](
            from_row=_goal_from_row,
            to_row=_goal_to_row,
        )

        super().__init__(
            data_access=data_access,
            table_name="agent_goals",
            mapper=mapper,
            primary_key="goal_id",
        )

    def list_by_agent(self, agent_id: int) -> list[Goal]:
        rows = self.data_access.query(
            "SELECT * FROM `agent_goals` "
            "WHERE `agent_id` = %s "
            "ORDER BY `goal_id`",
            [agent_id],
        )

        return [
            self.mapper.map_from_row(row)
            for row in rows
        ]

def _task_from_row(row: Any) -> AgentTask:
    return AgentTask(
        task_id=row.get("task_id"),
        agent_id=row["agent_id"],
        goal_id=row.get("goal_id"),
        conversation_id=row.get("conversation_id"),
        description=row["description"],
        status=TaskStatus(
            row.get("status", "pending")
        ),
    )

def _task_to_row(entity: AgentTask) -> dict[str, Any]:
    row = {
        "agent_id": entity.agent_id,
        "goal_id": entity.goal_id,
        "conversation_id": entity.conversation_id,
        "description": entity.description,
        "status": entity.status.value,
    }

    if entity.task_id is not None:
        row["task_id"] = entity.task_id

    return row

class AgentTaskRepository(BaseRepository[AgentTask]):
    def __init__(self, data_access: DataAccess) -> None:
        mapper = EntityMapper[AgentTask](
            from_row=_task_from_row,
            to_row=_task_to_row,
        )

        super().__init__(
            data_access=data_access,
            table_name="agent_tasks",
            mapper=mapper,
            primary_key="task_id",
        )

    def list_by_agent(self, agent_id: int) -> list[AgentTask]:
        rows = self.data_access.query(
            "SELECT * FROM `agent_tasks` "
            "WHERE `agent_id` = %s "
            "ORDER BY `task_id`",
            [agent_id],
        )

        return [
            self.mapper.map_from_row(row)
            for row in rows
        ]

    def list_by_conversation(self, conversation_id: int) -> list[AgentTask]:
        rows = self.data_access.query(
            "SELECT * FROM `agent_tasks` "
            "WHERE `conversation_id` = %s "
            "ORDER BY `task_id`",
            [conversation_id],
        )

        return [
            self.mapper.map_from_row(row)
            for row in rows
        ]

def _plan_from_row(row: Any) -> Plan:
    return Plan(
        plan_id=row.get("plan_id"),
        task_id=row["task_id"],
        name=row["name"],
        status=TaskStatus(
            row.get("status", "pending")
        ),
    )

def _plan_to_row(entity: Plan) -> dict[str, Any]:
    row = {
        "task_id": entity.task_id,
        "name": entity.name,
        "status": entity.status.value,
    }

    if entity.plan_id is not None:
        row["plan_id"] = entity.plan_id

    return row

class PlanRepository(BaseRepository[Plan]):
    def __init__(self, data_access: DataAccess) -> None:
        mapper = EntityMapper[Plan](
            from_row=_plan_from_row,
            to_row=_plan_to_row,
        )

        super().__init__(
            data_access=data_access,
            table_name="agent_plans",
            mapper=mapper,
            primary_key="plan_id",
        )

    def list_by_task(self, task_id: int) -> list[Plan]:
        rows = self.data_access.query(
            "SELECT * FROM `agent_plans` "
            "WHERE `task_id` = %s "
            "ORDER BY `plan_id`",
            [task_id],
        )

        return [
            self.mapper.map_from_row(row)
            for row in rows
        ]

def _plan_step_from_row(row: Any) -> PlanStep:
    return PlanStep(
        plan_step_id=row.get("plan_step_id"),
        plan_id=row["plan_id"],
        step_index=row["step_index"],
        description=row["description"],
        tool_id=row.get("tool_id"),
        status=TaskStatus(
            row.get("status", "pending")
        ),
    )

def _plan_step_to_row(entity: PlanStep) -> dict[str, Any]:
    row = {
        "plan_id": entity.plan_id,
        "step_index": entity.step_index,
        "description": entity.description,
        "tool_id": entity.tool_id,
        "status": entity.status.value,
    }

    if entity.plan_step_id is not None:
        row["plan_step_id"] = entity.plan_step_id

    return row

class PlanStepRepository(BaseRepository[PlanStep]):
    def __init__(self, data_access: DataAccess) -> None:
        mapper = EntityMapper[PlanStep](
            from_row=_plan_step_from_row,
            to_row=_plan_step_to_row,
        )

        super().__init__(
            data_access=data_access,
            table_name="agent_plan_steps",
            mapper=mapper,
            primary_key="plan_step_id",
        )

    def list_by_plan(self, plan_id: int) -> list[PlanStep]:
        rows = self.data_access.query(
            "SELECT * FROM `agent_plan_steps` "
            "WHERE `plan_id` = %s "
            "ORDER BY `step_index`",
            [plan_id],
        )

        return [
            self.mapper.map_from_row(row)
            for row in rows
        ]


def _execution_from_row(row: Any) -> AgentExecution:
    return AgentExecution(
        execution_id=row.get("execution_id"),
        task_id=row["task_id"],
        status=ExecutionStatus(
            row.get("status", "running")
        ),
        current_step=row.get("current_step", 0),
        error_message=row.get("error_message"),
        started_at=row.get("started_at"),
        finished_at=row.get("finished_at"),
    )


def _execution_to_row(entity: AgentExecution) -> dict[str, Any]:
    row = {
        "task_id": entity.task_id,
        "status": entity.status.value,
        "current_step": entity.current_step,
        "error_message": entity.error_message,
        "started_at": entity.started_at,
        "finished_at": entity.finished_at,
    }

    if entity.execution_id is not None:
        row["execution_id"] = entity.execution_id

    return row


class AgentExecutionRepository(BaseRepository[AgentExecution]):
    def __init__(self, data_access: DataAccess) -> None:
        mapper = EntityMapper[AgentExecution](
            from_row=_execution_from_row,
            to_row=_execution_to_row,
        )

        super().__init__(
            data_access=data_access,
            table_name="agent_executions",
            mapper=mapper,
            primary_key="execution_id",
        )

    def list_by_task(self, task_id: int) -> list[AgentExecution]:
        rows = self.data_access.query(
            "SELECT * FROM `agent_executions` "
            "WHERE `task_id` = %s "
            "ORDER BY `execution_id`",
            [task_id],
        )

        return [
            self.mapper.map_from_row(row)
            for row in rows
        ]

def _tool_from_row(row: Any) -> Tool:
    def decode(value: Any) -> dict[str, Any]:
        if value is None:
            return {}

        if isinstance(value, dict):
            return value

        if isinstance(value, str):
            return json.loads(value)

        return dict(value)

    return Tool(
        tool_id=row.get("tool_id"),
        name=row["name"],
        description=row["description"],
        input_schema=decode(row.get("input_schema")),
        output_schema=decode(row.get("output_schema")),
        enabled=bool(row.get("enabled", True)),
    )

def _tool_to_row(entity: Tool) -> dict[str, Any]:
    row = {
        "name": entity.name,
        "description": entity.description,
        "input_schema": json.dumps(entity.input_schema),
        "output_schema": json.dumps(entity.output_schema),
        "enabled": entity.enabled,
    }

    if entity.tool_id is not None:
        row["tool_id"] = entity.tool_id

    return row

class ToolRepository(BaseRepository[Tool]):
    def __init__(self, data_access: DataAccess) -> None:
        mapper = EntityMapper[Tool](
            from_row=_tool_from_row,
            to_row=_tool_to_row,
        )

        super().__init__(
            data_access=data_access,
            table_name="tools",
            mapper=mapper,
            primary_key="tool_id",
        )

    def list_enabled(self) -> list[Tool]:
        rows = self.data_access.query(
            "SELECT * FROM `tools` "
            "WHERE `enabled` = %s "
            "ORDER BY `tool_id`",
            [True],
        )

        return [
            self.mapper.map_from_row(row)
            for row in rows
        ]

def _tool_call_from_row(row: Any) -> ToolCall:
    def decode(value: Any) -> dict[str, Any]:
        if value is None:
            return {}

        if isinstance(value, dict):
            return value

        if isinstance(value, str):
            return json.loads(value)

        return dict(value)

    return ToolCall(
        tool_call_id=row.get("tool_call_id"),
        execution_id=row["execution_id"],
        agent_id=row["agent_id"],
        task_id=row["task_id"],
        tool_id=row["tool_id"],
        input_data=decode(row.get("input_data")),
        status=ToolCallStatus(
            row.get("status", "pending")
        ),
        attempt=row.get("attempt", 1),
        error_message=row.get("error_message"),
    )


def _tool_call_to_row(entity: ToolCall) -> dict[str, Any]:
    row = {
        "execution_id": entity.execution_id,
        "agent_id": entity.agent_id,
        "task_id": entity.task_id,
        "tool_id": entity.tool_id,
        "input_data": json.dumps(entity.input_data),
        "status": entity.status.value,
        "attempt": entity.attempt,
        "error_message": entity.error_message,
    }

    if entity.tool_call_id is not None:
        row["tool_call_id"] = entity.tool_call_id

    return row

class ToolCallRepository(BaseRepository[ToolCall]):
    def __init__(self, data_access: DataAccess) -> None:
        mapper = EntityMapper[ToolCall](
            from_row=_tool_call_from_row,
            to_row=_tool_call_to_row,
        )

        super().__init__(
            data_access=data_access,
            table_name="tool_calls",
            mapper=mapper,
            primary_key="tool_call_id",
        )

    def list_by_execution(self, execution_id: int) -> list[ToolCall]:
        rows = self.data_access.query(
            "SELECT * FROM `tool_calls` "
            "WHERE `execution_id` = %s "
            "ORDER BY `tool_call_id`",
            [execution_id],
        )

        return [
            self.mapper.map_from_row(row)
            for row in rows
        ]

def _execution_result_from_row(row: Any) -> ExecutionResult:
    def decode(value: Any) -> dict[str, Any]:
        if value is None:
            return {}

        if isinstance(value, dict):
            return value

        if isinstance(value, str):
            return json.loads(value)

        return dict(value)

    return ExecutionResult(
        result_id=row.get("result_id"),
        tool_call_id=row["tool_call_id"],
        success=bool(row["success"]),
        output_data=decode(row.get("output_data")),
        error_message=row.get("error_message"),
        duration_ms=row.get("duration_ms"),
    )

def _execution_result_to_row(entity: ExecutionResult) -> dict[str, Any]:
    row = {
        "tool_call_id": entity.tool_call_id,
        "success": entity.success,
        "output_data": json.dumps(
            entity.output_data
        ),
        "error_message": entity.error_message,
        "duration_ms": entity.duration_ms,
    }

    if entity.result_id is not None:
        row["result_id"] = entity.result_id

    return row


class ExecutionResultRepository(BaseRepository[ExecutionResult]):
    def __init__(self, data_access: DataAccess) -> None:
        mapper = EntityMapper[ExecutionResult](
            from_row=_execution_result_from_row,
            to_row=_execution_result_to_row,
        )

        super().__init__(
            data_access=data_access,
            table_name="execution_results",
            mapper=mapper,
            primary_key="result_id",
        )

    def list_by_tool_call(self, tool_call_id: int) -> list[ExecutionResult]:
        rows = self.data_access.query(
            "SELECT * FROM `execution_results` "
            "WHERE `tool_call_id` = %s "
            "ORDER BY `result_id`",
            [tool_call_id],
        )

        return [
            self.mapper.map_from_row(row)
            for row in rows
        ]

class AgentToolRepository:
    """Repository for Agent -> Tool permissions."""

    table_name = "agent_tools"

    def __init__(self, data_access: DataAccess) -> None:
        self.data_access = data_access

    def grant(
        self,
        agent_id: int,
        tool_id: int,
    ) -> None:
        self.data_access.execute(
            "INSERT INTO `agent_tools` "
            "(`agent_id`, `tool_id`, `enabled`) "
            "VALUES (%s, %s, %s)",
            [agent_id, tool_id, True],
        )

    def revoke(
        self,
        agent_id: int,
        tool_id: int,
    ) -> None:
        self.data_access.execute(
            "DELETE FROM `agent_tools` "
            "WHERE `agent_id` = %s "
            "AND `tool_id` = %s",
            [agent_id, tool_id],
        )

    def set_enabled(
        self,
        agent_id: int,
        tool_id: int,
        enabled: bool,
    ) -> None:
        self.data_access.execute(
            "UPDATE `agent_tools` "
            "SET `enabled` = %s "
            "WHERE `agent_id` = %s "
            "AND `tool_id` = %s",
            [enabled, agent_id, tool_id],
        )

    def is_allowed(
        self,
        agent_id: int,
        tool_id: int,
    ) -> bool:
        row = self.data_access.query_one(
            "SELECT `enabled` "
            "FROM `agent_tools` "
            "WHERE `agent_id` = %s "
            "AND `tool_id` = %s",
            [agent_id, tool_id],
        )

        return bool(
            row is not None
            and row.get("enabled", False)
        )

    def list_tool_ids(self, agent_id: int) -> list[int]:
        rows = self.data_access.query(
            "SELECT `tool_id` "
            "FROM `agent_tools` "
            "WHERE `agent_id` = %s "
            "AND `enabled` = %s "
            "ORDER BY `tool_id`",
            [agent_id, True],
        )

        return [
            int(row["tool_id"])
            for row in rows
        ]