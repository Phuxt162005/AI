"""Generic data access layer."""

from __future__ import annotations

from typing import Any, Iterable

from database.connection import DatabaseConnection


class DataAccess:
    """
    Data Access Layer between application code
    and the database connection.
    """

    def __init__(
        self,
        connection: DatabaseConnection,
    ) -> None:
        self.connection = connection
        self._transaction_active = False

    @property
    def transaction_active(self) -> bool:
        """Return whether a transaction is active."""

        return self._transaction_active

    def begin_transaction(self) -> None:
        """Begin a database transaction."""

        if self._transaction_active:
            raise RuntimeError(
                "Transaction is already active"
            )

        self.connection.connect()
        self._transaction_active = True

    def execute(
        self,
        sql: str,
        parameters: Iterable[Any] | None = None,
    ) -> Any:
        """
        Execute an INSERT, UPDATE, DELETE or DDL statement.

        When no explicit transaction is active, the
        operation is committed automatically.

        When an explicit transaction is active, commit
        is deferred to Transaction.commit().
        """

        cursor = self.connection.cursor()

        try:
            if parameters is None:
                result = cursor.execute(sql)
            else:
                result = cursor.execute(
                    sql,
                    tuple(parameters),
                )

            if not self._transaction_active:
                self.connection.commit()

            return result

        except Exception:
            if not self._transaction_active:
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
            cursor.execute(
                sql,
                tuple(parameters),
            )

        fetchall = getattr(
            cursor,
            "fetchall",
            None,
        )

        if not callable(fetchall):
            raise RuntimeError(
                "Database cursor does not provide fetchall()"
            )

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
            cursor.execute(
                sql,
                tuple(parameters),
            )

        fetchone = getattr(
            cursor,
            "fetchone",
            None,
        )

        if not callable(fetchone):
            raise RuntimeError(
                "Database cursor does not provide fetchone()"
            )

        return fetchone()

    def commit(self) -> None:
        """Commit the current transaction."""

        self.connection.commit()
        self._transaction_active = False

    def rollback(self) -> None:
        """Rollback the current transaction."""

        self.connection.rollback()
        self._transaction_active = False