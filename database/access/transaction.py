"""Database transaction support."""

from __future__ import annotations

from database.connection import DatabaseConnection

class Transaction:
    """Explicit database transaction."""

    def __init__(self, connection: DatabaseConnection) -> None:
        self.connection = connection
        self._active = False

    @property
    def active(self) -> bool:
        """Return whether the transaction is active."""

        return self._active

    def begin(self) -> None:
        """Begin a transaction."""

        if self._active:
            raise RuntimeError("Transaction is already active")

        self.connection.connect()
        self._active = True

    def commit(self) -> None:
        """Commit the transaction."""

        if not self._active:
            raise RuntimeError("No active transaction")

        try:
            self.connection.commit()
        finally:
            self._active = False

    def rollback(self) -> None:
        """Rollback the transaction."""

        if not self._active:
            raise RuntimeError("No active transaction")

        try:
            self.connection.rollback()
        finally:
            self._active = False

    def __enter__(self) -> "Transaction":
        """Start a transaction context."""

        self.begin()
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> bool:
        """Commit on success and rollback on failure."""

        if exc_type is None:
            self.commit()
        else:
            self.rollback()

        return False