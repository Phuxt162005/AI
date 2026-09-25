"""Build TrainingDataset from preprocessed records."""

from __future__ import annotations

from typing import Any

from data.dataset.dataset import (
    DatasetRecord,
    TrainingDataset,
)
from data.processing.preprocessor import (
    PreprocessedRecord,
)

class TrainingDatasetBuilder:
    """Build a TrainingDataset from preprocessed records."""

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

    def add(self, record: PreprocessedRecord) -> None:
        """Add one preprocessed record."""

        metadata = dict(record.metadata)
        metadata["tokens"] = list(record.tokens)
        metadata["token_ids"] = list(record.token_ids)
        metadata["token_count"] = (record.token_count)
        self.dataset.add_record(
            DatasetRecord(
                record_id=record.record_id,
                input=record.input,
                output=record.output,
                labels=dict(record.labels),
                metadata=metadata,
            )
        )

    def add_many(self, records: list[PreprocessedRecord]) -> None:
        """Add multiple preprocessed records."""

        for record in records:
            self.add(record)

    def build(self) -> TrainingDataset:
        """Return the completed training dataset."""

        return self.dataset