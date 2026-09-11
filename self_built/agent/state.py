"""State and observation structures for ProjectAI Agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from core.types import InputData, OutputData

from self_built.agent_planning import Plan, Understanding

class ObservationStatus(str, Enum):
    """Status of an Agent observation."""

    SUCCESS = "success"
    ERROR = "error"

class AgentTermination(str, Enum):
    """Reason why an Agent run terminated."""

    NOT_FINISHED = "not_finished"
    COMPLETED = "completed"
    MAX_STEPS = "max_steps"
    ERROR = "error"
    NO_VALID_ACTION = "no_valid_action"

@dataclass
class Observation:
    """Result observed after executing an Agent action."""

    action: str
    status: ObservationStatus
    result: Any = None
    error: str | None = None
    step_id: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentState:
    """Mutable state of one Agent execution."""

    input_data: InputData
    understanding: Understanding | None = None
    plan: Plan | None = None
    observations: list[Observation] = field(default_factory=list)
    history: list[dict[str, Any]] = field(default_factory=list)
    step_count: int = 0
    completed: bool = False
    failed: bool = False
    termination: AgentTermination = AgentTermination.NOT_FINISHED
    result: Any = None
    output: OutputData | None = None

    def add_observation(self, observation: Observation) -> None:
        """Add an observation to the execution state."""

        self.observations.append(observation)

    def add_history(self, event: dict[str, Any]) -> None:
        """Add an event to the Agent execution history."""

        self.history.append(dict(event))

    def complete(self, result: Any = None) -> None:
        """Mark the Agent execution as completed."""

        self.completed = True
        self.failed = False
        self.termination = AgentTermination.COMPLETED
        self.result = result

    def fail(
        self,
        result: Any = None,
        termination: AgentTermination = AgentTermination.ERROR,
    ) -> None:
        """Mark the Agent execution as failed."""

        self.completed = False
        self.failed = True
        self.termination = termination
        self.result = result

    def can_continue(self, max_steps: int) -> bool:
        """Return whether another Agent step may be executed."""

        if self.completed or self.failed:
            return False

        return self.step_count < max_steps

    @property
    def current_step(self) -> int | None:
        """Return the current plan step index."""

        if self.plan is None:
            return None
        if self.plan.current_step >= len(self.plan.steps):
            return None

        return self.plan.current_step