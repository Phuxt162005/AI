"""Dataset balancing utilities."""

from __future__ import annotations

from collections import defaultdict

from data.processing.cleaner import CleanRecord

class DatasetBalancer:
    """Limit over-represented groups in a dataset."""

    def __init__(self, max_records_per_group: int) -> None:
        if max_records_per_group <= 0:
            raise ValueError("max_records_per_group must be positive")

        self.max_records_per_group = (max_records_per_group)

    @staticmethod
    def _group_key(record: CleanRecord, group_attribute: str) -> str:
        """Return the group represented by a record."""

        value = record.attributes.get(group_attribute)
        if value is None:
            return "__unknown__"
        return str(value)

    def balance(
        self,
        records: list[CleanRecord],
        group_attribute: str,
    ) -> list[CleanRecord]:
        """Limit the number of records in each group."""

        groups: dict[str, int] = defaultdict(int)
        result: list[CleanRecord] = []

        for record in records:
            key = self._group_key(record, group_attribute)
            if (groups[key] >= self.max_records_per_group):
                continue
            groups[key] += 1
            result.append(record)
        return result

    def distribution(
        self,
        records: list[CleanRecord],
        group_attribute: str,
    ) -> dict[str, int]:
        """Return the current distribution by group."""

        result: dict[str, int] = defaultdict(int)
        for record in records:
            key = self._group_key(record, group_attribute)
            result[key] += 1

        return dict(result)