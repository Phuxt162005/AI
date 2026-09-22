"""Agent and Tool permission checking."""

from __future__ import annotations

from dataclasses import dataclass

from database.repositories.agent_repository import (
    AgentToolRepository,
)


class ToolPermissionDenied(PermissionError):
    """Raised when an Agent is not allowed to invoke a Tool."""


@dataclass
class AgentPermissionChecker:
    """Check whether an Agent may invoke a Tool."""

    repository: AgentToolRepository

    def check(
        self,
        agent_id: int,
        tool_id: int,
    ) -> bool:
        if agent_id <= 0:
            raise ValueError(
                "agent_id must be greater than zero"
            )

        if tool_id <= 0:
            raise ValueError(
                "tool_id must be greater than zero"
            )

        return self.repository.is_allowed(
            agent_id=agent_id,
            tool_id=tool_id,
        )

    def require(
        self,
        agent_id: int,
        tool_id: int,
    ) -> None:
        if not self.check(
            agent_id=agent_id,
            tool_id=tool_id,
        ):
            raise ToolPermissionDenied(
                "Agent is not allowed to use this Tool"
            )