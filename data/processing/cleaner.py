"""Data cleaning utilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

@dataclass
class CleanRecord:
    """A data record produced by the cleaning pipeline."""

    record_id: str
    content: str
    source_id: str | None = None
    metadata_id: str | None = None
    version: str = "1.0.0"
    attributes: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.record_id.strip():
            raise ValueError("record_id must not be empty")

        if not isinstance(self.content, str):
            raise TypeError("content must be a string")

        if not self.version.strip():
            raise ValueError("version must not be empty")

    def to_dict(self) -> dict[str, Any]:
        """Convert the clean record to a dictionary."""

        return {
            "record_id": self.record_id,
            "content": self.content,
            "source_id": self.source_id,
            "metadata_id": self.metadata_id,
            "version": self.version,
            "attributes": dict(self.attributes),
        }

class DataCleaner:
    """Remove obviously invalid or unusable textual data."""

    def clean(self, record: CleanRecord) -> CleanRecord:
        """Clean a record without changing its identity."""

        content = record.content
        # Remove null bytes and other control characters that
        # cannot be useful in normal textual training data.
        content = content.replace("\x00", "")
        cleaned_characters: list[str] = []

        for character in content:
            if character in "\n\r\t":
                cleaned_characters.append(character)
            elif character.isprintable():
                cleaned_characters.append(character)

        content = "".join(cleaned_characters)
        # Remove empty lines at the beginning/end while keeping
        # internal line structure.
        content = content.strip()
        attributes = dict(record.attributes)
        attributes["cleaned"] = True

        return CleanRecord(
            record_id=record.record_id,
            content=content,
            source_id=record.source_id,
            metadata_id=record.metadata_id,
            version=record.version,
            attributes=attributes,
        )

    def clean_many(self, records: list[CleanRecord]) -> list[CleanRecord]:
        """Clean multiple records."""

        return [self.clean(record) for record in records]