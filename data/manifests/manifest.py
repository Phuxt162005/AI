"""Dataset manifest definitions."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from data.schemas.data_schema import DataRecord


@dataclass
class DatasetManifest:
    """Describes a collection of data records."""

    manifest_id: str
    name: str
    version: str = "1.0.0"
    records: list[DataRecord] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    description: str = ""
    attributes: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.manifest_id.strip():
            raise ValueError("manifest_id must not be empty")

        if not self.name.strip():
            raise ValueError("name must not be empty")

        if not self.version.strip():
            raise ValueError("version must not be empty")

    def add_record(self, record: DataRecord) -> None:
        """Add a data record to the manifest."""

        if any(
            existing.record_id == record.record_id
            for existing in self.records
        ):
            raise ValueError(f"Record already exists: {record.record_id}")

        self.records.append(record)

    def get_record(self, record_id: str) -> DataRecord | None:
        """Find a record by identifier."""

        for record in self.records:
            if record.record_id == record_id:
                return record

        return None

    def remove_record(self, record_id: str) -> None:
        """Remove a record from the manifest."""

        for index, record in enumerate(self.records):
            if record.record_id == record_id:
                del self.records[index]
                return

        raise KeyError(f"Record not found: {record_id}")

    @property
    def record_count(self) -> int:
        """Return the number of records."""

        return len(self.records)

    def to_dict(self) -> dict[str, Any]:
        """Convert the manifest to a serializable dictionary."""

        return {
            "manifest_id": self.manifest_id,
            "name": self.name,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "description": self.description,
            "record_count": self.record_count,
            "records": [record.to_dict() for record in self.records],
            "attributes": dict(self.attributes),
        }