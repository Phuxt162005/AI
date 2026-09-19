"""Training data formatting utilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from data.processing.cleaner import CleanRecord
from data.processing.labeler import LabeledRecord

@dataclass
class FormattedRecord:
    """Training-ready structured record."""

    record_id: str
    input: str
    output: str | None = None
    labels: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

class DataFormatter:
    """
    Convert processed records into a consistent
    training-ready structure.
    """

    def format(
        self,
        record: CleanRecord | LabeledRecord,
        output: str | None = None,
    ) -> FormattedRecord:
        """Format one record."""

        if isinstance(record, LabeledRecord):
            base_record = record.record
            labels = dict(record.labels)
        else:
            base_record = record
            labels = {}

        metadata = {
            "source_id": base_record.source_id,
            "metadata_id": base_record.metadata_id,
            "version": base_record.version,
            **dict(base_record.attributes),
        }

        return FormattedRecord(
            record_id=base_record.record_id,
            input=base_record.content,
            output=output,
            labels=labels,
            metadata=metadata,
        )

    def format_many(
        self,
        records: list[
            CleanRecord | LabeledRecord
        ],
    ) -> list[FormattedRecord]:
        """Format multiple records."""

        return [
            self.format(record)
            for record in records
        ]