"""Metadata management for ProjectAI data."""

from __future__ import annotations

from typing import Any

from data.schemas.metadata_schema import MetadataSchema


class MetadataManager:
    """Manage metadata objects in memory.

    Persistence is intentionally left to later database/storage phases.
    """

    def __init__(self) -> None:
        self._items: dict[str, MetadataSchema] = {}

    def add(self, metadata: MetadataSchema) -> None:
        """Add metadata to the manager."""

        if metadata.metadata_id in self._items:
            raise ValueError(f"Metadata already exists: {metadata.metadata_id}")

        self._items[metadata.metadata_id] = metadata

    def get(self, metadata_id: str) -> MetadataSchema | None:
        """Return metadata by identifier."""

        return self._items.get(metadata_id)

    def update(self, metadata_id: str, **attributes: Any) -> MetadataSchema:
        """Update metadata attributes."""

        metadata = self._items.get(metadata_id)

        if metadata is None:
            raise KeyError(f"Metadata not found: {metadata_id}")

        for key, value in attributes.items():
            if not hasattr(metadata, key):
                raise AttributeError(f"Unknown metadata field: {key}")

            setattr(metadata, key, value)

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