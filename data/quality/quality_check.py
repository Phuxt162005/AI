"""Quality checks for processed data."""

from __future__ import annotations

from dataclasses import dataclass, field

from data.processing.cleaner import CleanRecord

@dataclass
class QualityResult:
    """Result of a dataset quality check."""

    valid: bool
    record_count: int
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    duplicate_count: int = 0
    empty_count: int = 0

    def add_error(self, message: str) -> None:
        """Add a quality error."""

        self.errors.append(message)
        self.valid = False

    def add_warning(self, message: str) -> None:
        """Add a quality warning."""

        self.warnings.append(message)

class DataQualityChecker:
    """Validate processed dataset quality."""

    def check(self, records: list[CleanRecord]) -> QualityResult:
        """Run quality checks."""

        result = QualityResult(
            valid=True,
            record_count=len(records),
        )
        seen: set[str] = set()

        for record in records:
            content = record.content.strip()

            if not content:
                result.empty_count += 1
                result.add_error(f"Empty content: {record.record_id}")

            normalized = " ".join(content.casefold().split())

            if normalized in seen:
                result.duplicate_count += 1
                result.add_error(
                    f"Duplicate content: "
                    f"{record.record_id}"
                )
            else:
                seen.add(normalized)

            if not record.source_id:
                result.add_warning(
                    f"Missing source_id: "
                    f"{record.record_id}"
                )

            if not record.metadata_id:
                result.add_warning(
                    f"Missing metadata_id: "
                    f"{record.record_id}"
                )
        return result