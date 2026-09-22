from database.models.agent import (
    Agent,
    AgentStatus,
    Goal,
    Tool,
)
from database.repositories.agent_repository import (
    AgentRepository,
    GoalRepository,
    ToolRepository,
)


class FakeDataAccess:
    def __init__(self):
        self.executed = []
        self.rows = []

    def execute(self, sql, parameters=None):
        self.executed.append(
            (sql, parameters)
        )

    def query(
        self,
        sql,
        parameters=None,
    ):
        return self.rows

    def query_one(
        self,
        sql,
        parameters=None,
    ):
        return self.rows[0] if self.rows else None


def test_agent_repository_table_name():
    repository = AgentRepository(
        FakeDataAccess()
    )

    assert repository.table_name == "agents"


def test_agent_mapping():
    repository = AgentRepository(
        FakeDataAccess()
    )

    entity = repository.mapper.map_from_row(
        {
            "agent_id": 1,
            "name": "Assistant",
            "description": "AI Assistant",
            "status": "active",
        }
    )

    assert isinstance(entity, Agent)
    assert entity.agent_id == 1
    assert entity.status == AgentStatus.ACTIVE


def test_goal_repository():
    repository = GoalRepository(
        FakeDataAccess()
    )

    entity = repository.mapper.map_from_row(
        {
            "goal_id": 1,
            "agent_id": 2,
            "description": "Answer",
            "status": "pending",
        }
    )

    assert isinstance(entity, Goal)
    assert entity.agent_id == 2


def test_tool_repository():
    repository = ToolRepository(
        FakeDataAccess()
    )

    entity = repository.mapper.map_from_row(
        {
            "tool_id": 1,
            "name": "search",
            "description": "Search tool",
            "input_schema": "{}",
            "output_schema": "{}",
            "enabled": True,
        }
    )

    assert isinstance(entity, Tool)
    assert entity.name == "search"