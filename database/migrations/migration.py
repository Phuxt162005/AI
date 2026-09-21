"""Migration definitions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

SQLExecutor = Callable[[str], Any]

@dataclass(frozen=True)
class Migration:
    """A single versioned database migration."""

    version: int
    name: str
    up_sql: str
    down_sql: str

    def __post_init__(self) -> None:
        if self.version < 1:
            raise ValueError("version must be positive")

        if not self.name.strip():
            raise ValueError("name must not be empty")

        if not self.up_sql.strip():
            raise ValueError("up_sql must not be empty")

        if not self.down_sql.strip():
            raise ValueError("down_sql must not be empty")

    def apply(self, execute: SQLExecutor) -> Any:
        """Apply the migration."""

        return execute(self.up_sql)

    def rollback(self, execute: SQLExecutor) -> Any:
        """Rollback the migration."""

        return execute(self.down_sql)