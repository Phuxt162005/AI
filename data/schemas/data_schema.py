"""Core schemas for ProjectAI data records.

This module defines the common data types used by the data pipeline.
It intentionally relies only on Python's standard library.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DataType(str, Enum):
    """Supported high-level data types."""

    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    STRUCTURED = "structured"
    UNSTRUCTURED = "unstructured"
    CONVERSATION = "conversation"
    DOCUMENT = "document"
    EMBEDDING = "embedding"
    LABEL = "label"


class DataSplit(str, Enum):
    """Dataset split assigned to a data record."""

    TRAIN = "train"
    VALIDATION = "validation"
    TEST = "test"


@dataclass
class DataRecord:
    """A normalized unit of data used by the ProjectAI pipeline."""

    record_id: str
    data_type: DataType
    content: Any

    metadata_id: str | None = None
    source_id: str | None = None
    split: DataSplit | None = None

    version: str = "1.0.0"
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.record_id.strip():
            raise ValueError("record_id must not be empty")

        if not isinstance(self.data_type, DataType):
            self.data_type = DataType(self.data_type)

        if self.split is not None and not isinstance(self.split, DataSplit):
            self.split = DataSplit(self.split)

        if not self.version.strip():
            raise ValueError("version must not be empty")

    def to_dict(self) -> dict[str, Any]:
        """Convert the record into a serializable dictionary."""

        return {
            "record_id": self.record_id,
            "data_type": self.data_type.value,
            "content": self.content,
            "metadata_id": self.metadata_id,
            "source_id": self.source_id,
            "split": self.split.value if self.split else None,
            "version": self.version,
            "tags": list(self.tags),
        }