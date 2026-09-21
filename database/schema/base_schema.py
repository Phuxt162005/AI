"""Base MySQL schema definition."""

from __future__ import annotations


DATABASE_NAME = "projectai"

def create_database_sql(database_name: str = DATABASE_NAME) -> str:
    """Return SQL for creating the ProjectAI database."""

    if not database_name.strip():
        raise ValueError("database_name must not be empty")

    return (
        f"CREATE DATABASE IF NOT EXISTS "
        f"`{database_name}` "
        "CHARACTER SET utf8mb4 "
        "COLLATE utf8mb4_unicode_ci;"
    )