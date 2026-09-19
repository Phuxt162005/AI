"""Training dataset definitions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

@dataclass
class DatasetRecord:
    """A training-ready dataset record."""

    record_id: str
    input: str
    output: str | None = None
    labels: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class TrainingDataset:
    """A versioned collection of training records."""

    name: str
    version: str
    dataset_type: str
    records: list[DatasetRecord] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    SUPPORTED_TYPES = {
        "pre_training",
        "instruction",
        "conversation",
        "personality",
        "emotion",
        "multimodal",
        "preference",
    }

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name must not be empty")

        if not self.version.strip():
            raise ValueError("version must not be empty")

        if (
            self.dataset_type
            not in self.SUPPORTED_TYPES
        ):
            raise ValueError(
                f"Unsupported dataset type: "
                f"{self.dataset_type}"
            )

    def add_record(self, record: DatasetRecord) -> None:
        """Add one record."""

        self.records.append(record)

    def add_records(self, records: list[DatasetRecord]) -> None:
        """Add multiple records."""

        self.records.extend(records)

    def __len__(self) -> int:
        return len(self.records)

    def record_ids(self) -> set[str]:
        """Return all record IDs."""

        return {
            record.record_id
            for record in self.records
        }

    def to_dict(self) -> dict[str, Any]:
        """Convert dataset to a serializable structure."""

        return {
            "name": self.name,
            "version": self.version,
            "dataset_type": self.dataset_type,
            "record_count": len(self.records),
            "records": [
                {
                    "record_id": record.record_id,
                    "input": record.input,
                    "output": record.output,
                    "labels": dict(record.labels),
                    "metadata": dict(record.metadata),
                }
                for record in self.records
            ],
            "metadata": dict(self.metadata),
        }