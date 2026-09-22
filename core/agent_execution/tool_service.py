"""Tool execution service."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from time import perf_counter
from typing import Any

from core.agent_permission.permission import (
    AgentPermissionChecker,
)
from database.models.agent import (
    ExecutionResult,
    ToolCall,
    ToolCallStatus,
)
from database.repositories.agent_repository import (
    ExecutionResultRepository,
    ToolCallRepository,
)

ToolFunction = Callable[
    [dict[str, Any]],
    dict[str, Any],
]

@dataclass
class ToolRegistry:
    """Runtime registry of executable tools."""

    tools: dict[int, ToolFunction]

    def register(
        self,
        tool_id: int,
        function: ToolFunction,
    ) -> None:
        if tool_id <= 0:
            raise ValueError("tool_id must be greater than zero")
        self.tools[tool_id] = function

    def get(self, tool_id: int) -> ToolFunction:
        try:
            return self.tools[tool_id]
        except KeyError as exc:
            raise KeyError(f"Tool {tool_id} is not registered") from exc

class ToolExecutionService:
    """
    Execute a Tool after permission validation and record the result.
    """

    def __init__(
        self,
        permission_checker: AgentPermissionChecker,
        registry: ToolRegistry,
        tool_call_repository: ToolCallRepository,
        result_repository: ExecutionResultRepository,
    ) -> None:
        self.permission_checker = permission_checker
        self.registry = registry
        self.tool_call_repository = (tool_call_repository)
        self.result_repository = result_repository

    def execute(
        self,
        *,
        execution_id: int,
        agent_id: int,
        task_id: int,
        tool_id: int,
        input_data: dict[str, Any],
        attempt: int = 1,
    ) -> ExecutionResult:
        self.permission_checker.require(agent_id=agent_id, tool_id=tool_id)
        tool_function = self.registry.get(tool_id)
        call = ToolCall(
            tool_call_id=None,
            execution_id=execution_id,
            agent_id=agent_id,
            task_id=task_id,
            tool_id=tool_id,
            input_data=input_data,
            status=ToolCallStatus.RUNNING,
            attempt=attempt,
        )
        self.tool_call_repository.create(call)
        started = perf_counter()

        try:
            output = tool_function(input_data)
            duration_ms = int((perf_counter() - started) * 1000)
            result = ExecutionResult(
                result_id=None,
                tool_call_id=(
                    call.tool_call_id
                    if call.tool_call_id is not None
                    else 0
                ),
                success=True,
                output_data=output,
                duration_ms=duration_ms,
            )

            return result

        except Exception as exc:
            duration_ms = int((perf_counter() - started) * 1000)

            return ExecutionResult(
                result_id=None,
                tool_call_id=(
                    call.tool_call_id
                    if call.tool_call_id is not None
                    else 0
                ),
                success=False,
                output_data={},
                error_message=str(exc),
                duration_ms=duration_ms,
            )