"""Database schema definitions."""

from database.schema.base_schema import (
    DATABASE_NAME,
    create_database_sql,
)

__all__ = [
    "DATABASE_NAME",
    "create_database_sql",
]