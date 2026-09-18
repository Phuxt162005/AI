"""Records describing a single data collection operation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

class CollectionMethod(str, Enum):
    """Methods that can be used to collect data."""

    MANUAL = "manual"
    DATASET_IMPORT = "dataset_import"
    DATASET_DOWNLOAD = "dataset_download"
    API = "api"
    WEB_CRAWLING = "web_crawling"
    INTERNAL = "internal"
    SYNTHETIC = "synthetic"

class ProcessingState(str, Enum):
    """Current state of collected data."""

    COLLECTED = "collected"
    VALIDATED = "validated"
    PROCESSING = "processing"
    PROCESSED = "processed"
    REJECTED = "rejected"

@dataclass
class CollectionRecord:
    """Describe the provenance of a collected raw-data item."""

    collection_id: str
    source_id: str
    collection_method: CollectionMethod
    raw_path: str
    dataset_name: str | None = None
    dataset_version: str = "1.0.0"
    batch_id: str | None = None
    collected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    format: str | None = None
    size_bytes: int | None = None
    processing_state: ProcessingState = ProcessingState.COLLECTED
    attributes: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.collection_id.strip():
            raise ValueError("collection_id must not be empty")

        if not self.source_id.strip():
            raise ValueError("source_id must not be empty")

        if not self.raw_path.strip():
            raise ValueError("raw_path must not be empty")

        if not self.dataset_version.strip():
            raise ValueError("dataset_version must not be empty")

        if not isinstance(
            self.collection_method,
            CollectionMethod,
        ):
            self.collection_method = CollectionMethod(self.collection_method)

        if not isinstance(
            self.processing_state,
            ProcessingState,
        ):
            self.processing_state = ProcessingState(self.processing_state)

        if self.size_bytes is not None and self.size_bytes < 0:
            raise ValueError("size_bytes must not be negative")

    def mark_validated(self) -> None:
        """Mark the collected data as initially validated."""

        self.processing_state = ProcessingState.VALIDATED

    def mark_processing(self) -> None:
        """Mark the data as entering processing."""

        self.processing_state = ProcessingState.PROCESSING

    def mark_processed(self) -> None:
        """Mark the data as processed."""

        self.processing_state = ProcessingState.PROCESSED

    def mark_rejected(self) -> None:
        """Mark the data as rejected."""

        self.processing_state = ProcessingState.REJECTED

    def to_dict(self) -> dict[str, Any]:
        """Convert the collection record into a dictionary."""

        return {
            "collection_id": self.collection_id,
            "source_id": self.source_id,
            "collection_method": self.collection_method.value,
            "raw_path": self.raw_path,
            "dataset_name": self.dataset_name,
            "dataset_version": self.dataset_version,
            "batch_id": self.batch_id,
            "collected_at": self.collected_at.isoformat(),
            "format": self.format,
            "size_bytes": self.size_bytes,
            "processing_state": self.processing_state.value,
            "attributes": dict(self.attributes),
        }