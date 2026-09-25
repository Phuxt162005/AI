"""Dataset record validation utilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

@dataclass
class RecordValidationResult:
    """Validation result for a collection of dataset records."""

    valid_records: list[dict[str, Any]] = field(default_factory=list)
    rejected_records: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def input_count(self) -> int:
        """Return the number of input records."""

        return (len(self.valid_records) + len(self.rejected_records))

    @property
    def valid_count(self) -> int:
        """Return the number of valid records."""

        return len(self.valid_records)

    @property
    def rejected_count(self) -> int:
        """Return the number of rejected records."""

        return len(self.rejected_records)

    @property
    def valid_ratio(self) -> float:
        """Return the ratio of valid records."""

        if self.input_count == 0:
            return 0.0
        return self.valid_count / self.input_count


class DatasetRecordValidator:
    """Validate records according to ProjectAI dataset types."""

    REQUIRED_FIELDS = {
        "instruction": {"instruction", "expected_output"},
        "conversation": {"messages"},
        "personality": {
            "situation",
            "context",
            "desired_behavior",
            "expected_response",
        },
        "emotion": {
            "input",
            "emotion",
            "expected_response",
        },
        "preference": {
            "input",
            "chosen",
            "rejected",
        },
    }

    def validate(
        self,
        records: list[dict[str, Any]],
        dataset_type: str,
    ) -> RecordValidationResult:
        """Validate a list of dataset records."""

        if dataset_type not in self.REQUIRED_FIELDS:
            raise ValueError(f"Unsupported dataset type: {dataset_type}")

        result = RecordValidationResult()
        required_fields = self.REQUIRED_FIELDS[dataset_type]

        for index, record in enumerate(records):
            errors = self._validate_record(
                record,
                required_fields,
                dataset_type,
            )

            if errors:
                result.rejected_records.append(record)
                result.errors.extend(f"record {index}: {error}" for error in errors)
            else:
                result.valid_records.append(record)
        return result

    @staticmethod
    def _validate_record(
        record: dict[str, Any],
        required_fields: set[str],
        dataset_type: str,
    ) -> list[str]:
        """Validate one dataset record."""

        errors: list[str] = []

        if not isinstance(record, dict):
            return ["record must be a dictionary"]

        for field_name in required_fields:
            if field_name not in record:
                errors.append(f"missing required field: {field_name}")
                continue

            value = record[field_name]
            if value is None:
                errors.append(f"required field is null: {field_name}")
                continue

            if isinstance(value, str) and not value.strip():
                errors.append(f"required field is empty: {field_name}")

        if (
            dataset_type == "conversation"
            and "messages" in record
        ):
            messages = record["messages"]
            if not isinstance(messages, list):
                errors.append("messages must be a list")
            elif not messages:
                errors.append("messages must not be empty")
            else:
                for message_index, message in enumerate(messages):
                    if not isinstance(message, dict):
                        errors.append(
                            "message "
                            f"{message_index} must be a dictionary"
                        )
                        continue

                    if not message.get("role"):
                        errors.append(
                            "message "
                            f"{message_index} is missing role"
                        )

                    if not message.get("content"):
                        errors.append(
                            "message "
                            f"{message_index} is missing content"
                        )
        return errors