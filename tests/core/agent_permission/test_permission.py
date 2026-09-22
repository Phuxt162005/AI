import pytest

from core.agent_permission.permission import (
    AgentPermissionChecker,
    ToolPermissionDenied,
)


class FakePermissionRepository:
    def __init__(self):
        self.allowed = set()

    def is_allowed(
        self,
        agent_id,
        tool_id,
    ):
        return (
            agent_id,
            tool_id,
        ) in self.allowed


def test_permission_allowed():
    repository = FakePermissionRepository()

    repository.allowed.add((1, 10))

    checker = AgentPermissionChecker(
        repository=repository,
    )

    assert checker.check(
        agent_id=1,
        tool_id=10,
    )


def test_permission_denied():
    repository = FakePermissionRepository()

    checker = AgentPermissionChecker(
        repository=repository,
    )

    assert not checker.check(
        agent_id=1,
        tool_id=10,
    )


def test_require_denied():
    repository = FakePermissionRepository()

    checker = AgentPermissionChecker(
        repository=repository,
    )

    with pytest.raises(ToolPermissionDenied):
        checker.require(
            agent_id=1,
            tool_id=10,
        )


def test_invalid_agent():
    repository = FakePermissionRepository()

    checker = AgentPermissionChecker(
        repository=repository,
    )

    with pytest.raises(ValueError):
        checker.check(
            agent_id=0,
            tool_id=10,
        )