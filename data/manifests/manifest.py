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
        text_fields = {
            "manifest_id": self.manifest_id,
            "name": self.name,
            "version": self.version,
        }

        for field_name, value in text_fields.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")

        if not isinstance(self.description, str):
            raise TypeError("description must be a string")

        if not isinstance(self.created_at, datetime):
            raise TypeError("created_at must be a datetime")

        if not isinstance(self.records, list):
            raise TypeError("records must be a list of DataRecord instances")

        if any(not isinstance(record, DataRecord) for record in self.records):
            raise TypeError("every record must be a DataRecord instance")

        if not isinstance(self.attributes, dict):
            raise TypeError("attributes must be a dictionary")

        record_ids = [record.record_id for record in self.records]

        if len(record_ids) != len(set(record_ids)):
            raise ValueError("manifest contains duplicate record IDs")

    def add_record(self, record: DataRecord) -> None:
        """Add a data record to the manifest."""

        if not isinstance(record, DataRecord):
            raise TypeError("record must be a DataRecord instance")

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