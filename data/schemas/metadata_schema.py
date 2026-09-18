"""Schemas used for describing data metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class MetadataSchema:
    """Metadata associated with a data record."""

    metadata_id: str
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime | None = None
    source_id: str | None = None
    data_version: str = "1.0.0"
    format: str | None = None
    language: str | None = None
    license: str | None = None
    checksum: str | None = None
    size_bytes: int | None = None
    attributes: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.metadata_id.strip():
            raise ValueError("metadata_id must not be empty")

        if not self.data_version.strip():
            raise ValueError("data_version must not be empty")

        if self.size_bytes is not None and self.size_bytes < 0:
            raise ValueError("size_bytes must not be negative")

    def touch(self) -> None:
        """Update the metadata modification timestamp."""

        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict[str, Any]:
        """Convert metadata into a serializable dictionary."""

        return {
            "metadata_id": self.metadata_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": (
                self.updated_at.isoformat()
                if self.updated_at
                else None
            ),
            "source_id": self.source_id,
            "data_version": self.data_version,
            "format": self.format,
            "language": self.language,
            "license": self.license,
            "checksum": self.checksum,
            "size_bytes": self.size_bytes,
            "attributes": dict(self.attributes),
        }