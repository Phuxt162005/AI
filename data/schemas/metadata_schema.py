"""Schemas used for describing data metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class MetadataSchema:
    """Metadata associated with a data record."""

    metadata_id: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
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
        if not isinstance(self.metadata_id, str) or not self.metadata_id.strip():
            raise ValueError("metadata_id must be a non-empty string")

        if not isinstance(self.data_version, str) or not self.data_version.strip():
            raise ValueError("data_version must be a non-empty string")

        if not isinstance(self.created_at, datetime):
            raise TypeError("created_at must be a datetime")

        if self.updated_at is not None and not isinstance(
            self.updated_at, datetime
        ):
            raise TypeError("updated_at must be a datetime or None")

        optional_text_fields = (
            "source_id",
            "format",
            "language",
            "license",
            "checksum",
        )

        for field_name in optional_text_fields:
            value = getattr(self, field_name)

            if value is not None and not isinstance(value, str):
                raise TypeError(f"{field_name} must be a string or None")

        if self.size_bytes is not None:
            if isinstance(self.size_bytes, bool) or not isinstance(
                self.size_bytes, int
            ):
                raise TypeError("size_bytes must be an integer or None")

            if self.size_bytes < 0:
                raise ValueError("size_bytes must not be negative")

        if not isinstance(self.attributes, dict):
            raise TypeError("attributes must be a dictionary")

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