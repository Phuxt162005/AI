"""Database connection abstraction."""

from __future__ import annotations

from typing import Any, Callable

from database.config import DatabaseConfig

ConnectionFactory = Callable[
    [dict[str, object]],
    Any,
]


class DatabaseConnection:
    """Manage the application database connection."""

    def __init__(
        self,
        config: DatabaseConfig,
        connector: ConnectionFactory | None = None,
    ) -> None:
        self.config = config
        self.connector = connector
        self._connection: Any | None = None

    @property
    def is_connected(self) -> bool:
        """Return whether a connection is currently available."""

        return self._connection is not None

    def connect(self) -> Any:
        """Create and return a database connection."""

        if self._connection is not None:
            return self._connection
        if self.connector is None:
            raise RuntimeError("No database connector configured")
        self._connection = self.connector(self.config.to_connection_dict())

        return self._connection

    def close(self) -> None:
        """Close the current database connection."""

        if self._connection is None:
            return
        close = getattr(self._connection, "close", None)
        if callable(close):
            close()
        self._connection = None

    def cursor(self) -> Any:
        """Return a cursor from the active connection."""

        connection = self.connect()
        cursor = getattr(connection, "cursor", None)

        if not callable(cursor):
            raise RuntimeError("Database connection does not provide cursor()")
        return cursor()

    def commit(self) -> None:
        """Commit the current transaction."""

        if self._connection is None:
            raise RuntimeError("Database is not connected")
        commit = getattr(self._connection, "commit", None)
        if not callable(commit):
            raise RuntimeError("Database connection does not provide commit()")
        commit()

    def rollback(self) -> None:
        """Rollback the current transaction."""

        if self._connection is None:
            raise RuntimeError("Database is not connected")
        rollback = getattr(self._connection, "rollback", None)
        if not callable(rollback):
            raise RuntimeError("Database connection does not provide rollback()")
        rollback()