"""Text normalization utilities."""

from __future__ import annotations

import re
import unicodedata

from data.processing.cleaner import CleanRecord

class TextNormalizer:
    """Normalize textual data into a consistent representation."""

    _WHITESPACE_PATTERN = re.compile(r"[ \t]+")
    _MULTI_NEWLINE_PATTERN = re.compile(r"\n{3,}")

    def normalize_text(self, text: str) -> str:
        """Normalize Unicode, whitespace and special characters."""

        # Unicode normalization.
        text = unicodedata.normalize("NFC", text)
        # Normalize line endings.
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Normalize spaces and tabs.
        text = self._WHITESPACE_PATTERN.sub(" ", text)
        # Limit excessive empty lines.
        text = self._MULTI_NEWLINE_PATTERN.sub("\n\n", text)

        return text.strip()

    def normalize(self, record: CleanRecord) -> CleanRecord:
        """Normalize a clean record."""

        content = self.normalize_text(record.content)

        attributes = dict(record.attributes)
        attributes["normalized"] = True
        attributes["normalization_form"] = "NFC"

        return CleanRecord(
            record_id=record.record_id,
            content=content,
            source_id=record.source_id,
            metadata_id=record.metadata_id,
            version=record.version,
            attributes=attributes,
        )

    def normalize_many(self, records: list[CleanRecord]) -> list[CleanRecord]:
        """Normalize multiple records."""

        return [
            self.normalize(record)
            for record in records
        ]