"""Metadata management for ProjectAI data."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from data.schemas.metadata_schema import MetadataSchema


class MetadataManager:
    """Manage metadata objects in memory.

    Persistence is intentionally left to later database/storage phases.
    """

    _UPDATABLE_FIELDS = {
        "source_id",
        "data_version",
        "format",
        "language",
        "license",
        "checksum",
        "size_bytes",
        "attributes",
    }

    def __init__(self) -> None:
        self._items: dict[str, MetadataSchema] = {}

    def add(self, metadata: MetadataSchema) -> None:
        """Add metadata to the manager."""

        if not isinstance(metadata, MetadataSchema):
            raise TypeError("metadata must be a MetadataSchema instance")

        if metadata.metadata_id in self._items:
            raise ValueError(f"Metadata already exists: {metadata.metadata_id}")

        self._items[metadata.metadata_id] = metadata

    def get(self, metadata_id: str) -> MetadataSchema | None:
        """Return metadata by identifier."""

        return self._items.get(metadata_id)

    def update(self, metadata_id: str, **attributes: Any) -> MetadataSchema:
        """Update metadata attributes after validating the proposed changes."""

        metadata = self._items.get(metadata_id)

        if metadata is None:
            raise KeyError(f"Metadata not found: {metadata_id}")

        if not attributes:
            raise ValueError("At least one metadata field must be provided")

        unknown_fields = set(attributes) - self._UPDATABLE_FIELDS

        if unknown_fields:
            field_names = ", ".join(sorted(unknown_fields))
            raise AttributeError(f"Fields cannot be updated: {field_names}")

        # Constructing a candidate invokes MetadataSchema validation.
        # The stored object is not changed if validation fails.
        candidate = replace(metadata, **attributes)

        for field_name in attributes:
            setattr(metadata, field_name, getattr(candidate, field_name))

        metadata.touch()
        return metadata

    def remove(self, metadata_id: str) -> None:
        """Remove metadata from the in-memory manager."""

        if metadata_id not in self._items:
            raise KeyError(f"Metadata not found: {metadata_id}")

        del self._items[metadata_id]

    def all(self) -> list[MetadataSchema]:
        """Return all metadata entries."""

        return list(self._items.values())

    def count(self) -> int:
        """Return the number of metadata entries."""

        return len(self._items)