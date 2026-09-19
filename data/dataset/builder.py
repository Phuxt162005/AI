"""Training dataset builder."""

from __future__ import annotations

from typing import Any

from data.dataset.dataset import (
    DatasetRecord,
    TrainingDataset,
)
from data.processing.formatter import FormattedRecord

class DatasetBuilder:
    """Build a TrainingDataset from formatted records."""

    def __init__(
        self,
        name: str,
        version: str,
        dataset_type: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.dataset = TrainingDataset(
            name=name,
            version=version,
            dataset_type=dataset_type,
            metadata=(
                dict(metadata)
                if metadata is not None
                else {}
            ),
        )

    def add(self, record: FormattedRecord) -> None:
        """Add a formatted record."""

        self.dataset.add_record(
            DatasetRecord(
                record_id=record.record_id,
                input=record.input,
                output=record.output,
                labels=dict(record.labels),
                metadata=dict(record.metadata),
            )
        )

    def add_many(self, records: list[FormattedRecord]) -> None:
        """Add multiple formatted records."""

        for record in records:
            self.add(record)

    def build(self) -> TrainingDataset:
        """Return the constructed dataset."""

        return self.dataset