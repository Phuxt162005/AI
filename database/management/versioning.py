"""Data versioning utilities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

@dataclass(frozen=True)
class DataVersion:
    """Represent one version of a managed data object."""

    object_id: str
    version: int
    checksum: str
    created_at: datetime
    metadata: dict[str, Any]

class VersionManager:
    """Manage immutable version metadata for data objects."""

    def __init__(self) -> None:
        self._versions: dict[str, list[DataVersion]] = {}

    def create_version(
        self,
        object_id: str,
        checksum: str,
        metadata: dict[str, Any] | None = None,
    ) -> DataVersion:
        """Create the next version for an object."""

        object_id = object_id.strip()
        checksum = checksum.strip()

        if not object_id:
            raise ValueError("object_id must not be empty")

        if not checksum:
            raise ValueError("checksum must not be empty")

        history = self._versions.setdefault(object_id, [])
        version = len(history) + 1

        record = DataVersion(
            object_id=object_id,
            version=version,
            checksum=checksum,
            created_at=datetime.now(timezone.utc),
            metadata=dict(metadata or {}),
        )

        history.append(record)
        return record

    def current(self, object_id: str) -> DataVersion | None:
        """Return the current version."""

        history = self._versions.get(object_id, [])
        return history[-1] if history else None

    def history(self, object_id: str) -> list[DataVersion]:
        """Return all versions of an object."""

        return list(self._versions.get(object_id, []))