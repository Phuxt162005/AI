"""Database schema definitions."""

from database.schema.base_schema import (
    DATABASE_NAME,
    create_database_sql,
)

from database.schema.memory_schema import (
    MEMORY_TABLE,
    MEMORY_TABLE_DROP_SQL,
    MEMORY_TABLE_SQL,
)

__all__ = [
    "DATABASE_NAME",
    "create_database_sql",
    "MEMORY_TABLE",
    "MEMORY_TABLE_SQL",
    "MEMORY_TABLE_DROP_SQL",
]