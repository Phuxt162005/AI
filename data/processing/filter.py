"""Data filtering utilities."""

from __future__ import annotations

from collections.abc import Callable

from data.processing.cleaner import CleanRecord

class DataFilter:
    """Filter records according to dataset requirements."""

    def __init__(
        self,
        min_length: int = 1,
        max_length: int | None = None,
        predicate: Callable[[CleanRecord], bool] | None = None,
    ) -> None:
        if min_length < 0:
            raise ValueError("min_length must not be negative")

        if (
            max_length is not None
            and max_length < min_length
        ):
            raise ValueError(
                "max_length must be greater than "
                "or equal to min_length"
            )

        self.min_length = min_length
        self.max_length = max_length
        self.predicate = predicate

    def accept(self, record: CleanRecord) -> bool:
        """Return whether a record satisfies the filter."""

        length = len(record.content)

        if length < self.min_length:
            return False

        if (
            self.max_length is not None
            and length > self.max_length
        ):
            return False

        if (
            self.predicate is not None
            and not self.predicate(record)
        ):
            return False
        return True

    def filter(self, records: list[CleanRecord]) -> list[CleanRecord]:
        """Return only records accepted by the filter."""

        return [
            record
            for record in records
            if self.accept(record)
        ]