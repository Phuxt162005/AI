"""Migration for Agent and Tool database."""

from database.schema.agent_schema import (
    AGENT_TABLES_DOWN_SQL,
    AGENT_TABLES_UP_SQL,
)

V005_VERSION = 5
V005_NAME = "agent_and_tool"

UP_SQL = AGENT_TABLES_UP_SQL

DOWN_SQL = AGENT_TABLES_DOWN_SQL