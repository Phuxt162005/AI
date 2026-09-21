"""Migration for Memory database."""

from database.schema.memory_schema import (
    MEMORY_TABLE_DROP_SQL,
    MEMORY_TABLE_SQL,
)

V003_VERSION = 3
V003_NAME = "memory"

UP_SQL = MEMORY_TABLE_SQL

DOWN_SQL = MEMORY_TABLE_DROP_SQL