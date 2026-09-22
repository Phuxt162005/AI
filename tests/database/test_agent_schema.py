from database.schema.agent_schema import (
    AGENT_TABLES_DOWN_SQL,
    AGENT_TABLES_UP_SQL,
)


def test_agent_schema_contains_required_tables():
    required_tables = [
        "agents",
        "agent_configurations",
        "agent_goals",
        "agent_tasks",
        "agent_plans",
        "agent_plan_steps",
        "tools",
        "agent_tools",
        "agent_executions",
        "tool_calls",
        "execution_results",
    ]

    for table in required_tables:
        assert f"`{table}`" in AGENT_TABLES_UP_SQL


def test_agent_schema_contains_relationships():
    assert "FOREIGN KEY" in AGENT_TABLES_UP_SQL
    assert "fk_agent_tasks_agent" in AGENT_TABLES_UP_SQL
    assert "fk_agent_executions_task" in AGENT_TABLES_UP_SQL
    assert "fk_tool_calls_tool" in AGENT_TABLES_UP_SQL
    assert (
        "fk_execution_results_tool_call"
        in AGENT_TABLES_UP_SQL
    )


def test_agent_schema_down_order():
    assert (
        AGENT_TABLES_DOWN_SQL.index(
            "execution_results"
        )
        < AGENT_TABLES_DOWN_SQL.index(
            "tool_calls"
        )
    )

    assert (
        AGENT_TABLES_DOWN_SQL.index(
            "tool_calls"
        )
        < AGENT_TABLES_DOWN_SQL.index(
            "agents"
        )
    )