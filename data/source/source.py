"""Data source and provenance definitions."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SourceType(str, Enum):
    """Types of data sources."""

    FILE = "file"
    DATABASE = "database"
    API = "api"
    USER_INPUT = "user_input"
    GENERATED = "generated"
    EXTERNAL_DATASET = "external_dataset"


@dataclass
class DataSource:
    """Describes the origin of a data record."""

    source_id: str
    source_type: SourceType
    name: str
    location: str | None = None
    description: str = ""
    version: str | None = None
    license: str | None = None
    attributes: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.source_id.strip():
            raise ValueError("source_id must not be empty")

        if not self.name.strip():
            raise ValueError("name must not be empty")

        if not isinstance(self.source_type, SourceType):
            self.source_type = SourceType(self.source_type)

    def to_dict(self) -> dict[str, Any]:
        """Convert the source to a serializable dictionary."""

        return {
            "source_id": self.source_id,
            "source_type": self.source_type.value,
            "name": self.name,
            "location": self.location,
            "description": self.description,
            "version": self.version,
            "license": self.license,
            "attributes": dict(self.attributes),
        }