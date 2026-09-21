"""Database transaction support."""

from __future__ import annotations

from database.access.data_access import DataAccess


class Transaction:
    """Explicit database transaction."""

    def __init__(
        self,
        data_access: DataAccess,
    ) -> None:
        self.data_access = data_access

    @property
    def active(self) -> bool:
        """Return whether the transaction is active."""

        return self.data_access.transaction_active

    def begin(self) -> None:
        """Begin a transaction."""

        self.data_access.begin_transaction()

    def commit(self) -> None:
        """Commit the transaction."""

        if not self.active:
            raise RuntimeError(
                "No active transaction"
            )

        self.data_access.commit()

    def rollback(self) -> None:
        """Rollback the transaction."""

        if not self.active:
            raise RuntimeError(
                "No active transaction"
            )

        self.data_access.rollback()

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