"""Database foundation for ProjectAI."""

from database.config import DatabaseConfig
from database.connection import DatabaseConnection

__all__ = [
    "DatabaseConfig",
    "DatabaseConnection",
]