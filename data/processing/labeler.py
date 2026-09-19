"""Dataset labeling utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from data.processing.cleaner import CleanRecord

@dataclass
class LabeledRecord:
    """A record with training labels."""

    record: CleanRecord
    labels: dict[str, Any]

class DataLabeler:
    """Attach labels to records."""

    def __init__(
        self,
        label_function: Callable[
            [CleanRecord],
            dict[str, Any],
        ] | None = None,
    ) -> None:
        self.label_function = label_function

    def label(
        self,
        record: CleanRecord,
        labels: dict[str, Any] | None = None,
    ) -> LabeledRecord:
        """Attach explicit or generated labels."""

        if labels is not None:
            assigned_labels = dict(labels)
        elif self.label_function is not None:
            assigned_labels = dict(self.label_function(record))
        else:
            assigned_labels = {}

        return LabeledRecord(record=record, labels=assigned_labels)

    def label_many(
        self,
        records: list[CleanRecord],
        labels: list[dict[str, Any]] | None = None,
    ) -> list[LabeledRecord]:
        """Label multiple records."""

        if labels is not None and len(labels) != len(records):
            raise ValueError("labels length must match records length")

        result: list[LabeledRecord] = []

        for index, record in enumerate(records):
            current_labels = (
                labels[index]
                if labels is not None
                else None
            )
            result.append(self.label(record, current_labels))

        return result