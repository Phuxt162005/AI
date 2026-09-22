"""Agent and Tool persistence entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

class AgentStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"

class GoalStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ExecutionStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ToolCallStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Agent:
    agent_id: int | None
    name: str
    description: str = ""
    status: AgentStatus = AgentStatus.ACTIVE

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name must not be empty")

        if not isinstance(self.status, AgentStatus):
            self.status = AgentStatus(self.status)

@dataclass
class AgentConfiguration:
    agent_id: int
    model_id: str
    max_steps: int = 10
    temperature: float = 0.7
    timeout: int = 60
    system_prompt: str = ""
    memory_enabled: bool = True

    def __post_init__(self) -> None:
        if self.agent_id <= 0:
            raise ValueError("agent_id must be greater than zero")

        if not self.model_id.strip():
            raise ValueError("model_id must not be empty")

        if self.max_steps <= 0:
            raise ValueError("max_steps must be greater than zero")

        if self.temperature < 0:
            raise ValueError("temperature must not be negative")

        if self.timeout <= 0:
            raise ValueError("timeout must be greater than zero")

@dataclass
class Goal:
    goal_id: int | None
    agent_id: int
    description: str
    status: GoalStatus = GoalStatus.PENDING

    def __post_init__(self) -> None:
        if self.agent_id <= 0:
            raise ValueError("agent_id must be greater than zero")

        if not self.description.strip():
            raise ValueError("description must not be empty")

        if not isinstance(self.status, GoalStatus):
            self.status = GoalStatus(self.status)

@dataclass
class AgentTask:
    task_id: int | None
    agent_id: int
    goal_id: int | None
    conversation_id: int | None
    description: str
    status: TaskStatus = TaskStatus.PENDING

    def __post_init__(self) -> None:
        if self.agent_id <= 0:
            raise ValueError("agent_id must be greater than zero")

        if self.goal_id is not None and self.goal_id <= 0:
            raise ValueError("goal_id must be greater than zero")

        if (
            self.conversation_id is not None
            and self.conversation_id <= 0
        ):
            raise ValueError("conversation_id must be greater than zero")

        if not self.description.strip():
            raise ValueError("description must not be empty")

        if not isinstance(self.status, TaskStatus):
            self.status = TaskStatus(self.status)

@dataclass
class Plan:
    plan_id: int | None
    task_id: int
    name: str
    status: TaskStatus = TaskStatus.PENDING

    def __post_init__(self) -> None:
        if self.task_id <= 0:
            raise ValueError("task_id must be greater than zero")

        if not self.name.strip():
            raise ValueError("name must not be empty")

        if not isinstance(self.status, TaskStatus):
            self.status = TaskStatus(self.status)

@dataclass
class PlanStep:
    plan_step_id: int | None
    plan_id: int
    step_index: int
    description: str
    tool_id: int | None = None
    status: TaskStatus = TaskStatus.PENDING

    def __post_init__(self) -> None:
        if self.plan_id <= 0:
            raise ValueError("plan_id must be greater than zero")

        if self.step_index < 0:
            raise ValueError("step_index must not be negative")

        if not self.description.strip():
            raise ValueError("description must not be empty")

        if self.tool_id is not None and self.tool_id <= 0:
            raise ValueError("tool_id must be greater than zero")

        if not isinstance(self.status, TaskStatus):
            self.status = TaskStatus(self.status)

@dataclass
class AgentExecution:
    execution_id: int | None
    task_id: int
    status: ExecutionStatus = ExecutionStatus.RUNNING
    current_step: int = 0
    error_message: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.task_id <= 0:
            raise ValueError("task_id must be greater than zero")

        if self.current_step < 0:
            raise ValueError("current_step must not be negative")

        if not isinstance(self.status, ExecutionStatus):
            self.status = ExecutionStatus(self.status)

@dataclass
class Tool:
    tool_id: int | None
    name: str
    description: str
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)
    enabled: bool = True

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name must not be empty")

        if not self.description.strip():
            raise ValueError("description must not be empty")

@dataclass
class AgentTool:
    agent_id: int
    tool_id: int
    enabled: bool = True

    def __post_init__(self) -> None:
        if self.agent_id <= 0:
            raise ValueError("agent_id must be greater than zero")

        if self.tool_id <= 0:
            raise ValueError("tool_id must be greater than zero")

@dataclass
class ToolCall:
    tool_call_id: int | None
    execution_id: int
    agent_id: int
    task_id: int
    tool_id: int
    input_data: dict[str, Any] = field(default_factory=dict)
    status: ToolCallStatus = ToolCallStatus.PENDING
    attempt: int = 1
    error_message: str | None = None

    def __post_init__(self) -> None:
        if self.execution_id <= 0:
            raise ValueError("execution_id must be greater than zero")

        if self.agent_id <= 0:
            raise ValueError("agent_id must be greater than zero")

        if self.task_id <= 0:
            raise ValueError("task_id must be greater than zero")

        if self.tool_id <= 0:
            raise ValueError("tool_id must be greater than zero")

        if self.attempt <= 0:
            raise ValueError("attempt must be greater than zero")

        if not isinstance(self.status, ToolCallStatus):
            self.status = ToolCallStatus(self.status)

@dataclass
class ExecutionResult:
    result_id: int | None
    tool_call_id: int
    success: bool
    output_data: dict[str, Any] = field(default_factory=dict)
    error_message: str | None = None
    duration_ms: int | None = None

    def __post_init__(self) -> None:
        if self.tool_call_id <= 0:
            raise ValueError("tool_call_id must be greater than zero")

        if (
            self.duration_ms is not None
            and self.duration_ms < 0
        ):
            raise ValueError("duration_ms must not be negative")