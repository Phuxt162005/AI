"""Migration for Knowledge Database."""

from database.schema.knowledge_schema import (
    KNOWLEDGE_TABLES_DOWN_SQL,
    KNOWLEDGE_TABLES_UP_SQL,
)

V004_VERSION = 4
V004_NAME = "knowledge"

UP_SQL = KNOWLEDGE_TABLES_UP_SQL

DOWN_SQL = KNOWLEDGE_TABLES_DOWN_SQL