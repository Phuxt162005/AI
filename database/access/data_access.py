"""Generic data access layer."""

from __future__ import annotations

from typing import Any, Iterable

from database.connection import DatabaseConnection

class DataAccess:
    """
    Data Access Layer between application code
    and the database connection.
    """

    def __init__(self, connection: DatabaseConnection) -> None:
        self.connection = connection

    def execute(
        self,
        sql: str,
        parameters: Iterable[Any] | None = None,
    ) -> Any:
        """Execute an INSERT, UPDATE, DELETE or DDL statement."""

        cursor = self.connection.cursor()
        try:
            if parameters is None:
                result = cursor.execute(sql)
            else:
                result = cursor.execute(sql, tuple(parameters))

            self.connection.commit()
            return result

        except Exception:
            self.connection.rollback()
            raise

    def query(
        self,
        sql: str,
        parameters: Iterable[Any] | None = None,
    ) -> list[Any]:
        """Execute a SELECT query and return all rows."""

        cursor = self.connection.cursor()

        if parameters is None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, tuple(parameters))

        fetchall = getattr(cursor, "fetchall", None)

        if not callable(fetchall):
            raise RuntimeError("Database cursor does not provide fetchall()")

        return list(fetchall())

    def query_one(
        self,
        sql: str,
        parameters: Iterable[Any] | None = None,
    ) -> Any | None:
        """Execute a SELECT query and return one row."""

        cursor = self.connection.cursor()

        if parameters is None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, tuple(parameters))

        fetchone = getattr(cursor, "fetchone", None)
        if not callable(fetchone):
            raise RuntimeError("Database cursor does not provide fetchone()")
        return fetchone()

    def commit(self) -> None:
        """Commit the current transaction."""

        self.connection.commit()

    def rollback(self) -> None:
        """Rollback the current transaction."""

        self.connection.rollback()