"""Batch management for data collection."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from data.collection.collection_record import CollectionRecord

@dataclass
class CollectionBatch:
    """Group collection records belonging to one collection batch."""

    batch_id: str
    dataset_name: str
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    records: list[CollectionRecord] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.batch_id.strip():
            raise ValueError("batch_id must not be empty")

        if not self.dataset_name.strip():
            raise ValueError("dataset_name must not be empty")

        if not self.version.strip():
            raise ValueError("version must not be empty")

    def add_record(self, record: CollectionRecord) -> None:
        """Add a collection record to the batch."""

        if any(
            existing.collection_id == record.collection_id
            for existing in self.records
        ):
            raise ValueError(
                f"Collection record already exists: "
                f"{record.collection_id}"
            )

        if record.batch_id is None:
            record.batch_id = self.batch_id

        elif record.batch_id != self.batch_id:
            raise ValueError("Collection record belongs to another batch")

        self.records.append(record)

    def get_record(self, collection_id: str) -> CollectionRecord | None:
        """Return a collection record by ID."""

        for record in self.records:
            if record.collection_id == collection_id:
                return record
        return None

    @property
    def record_count(self) -> int:
        """Return the number of collected records."""

        return len(self.records)

    def to_dict(self) -> dict[str, Any]:
        """Convert the batch into a dictionary."""

        return {
            "batch_id": self.batch_id,
            "dataset_name": self.dataset_name,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "record_count": self.record_count,
            "records": [record.to_dict() for record in self.records],
            "attributes": dict(self.attributes),
        }