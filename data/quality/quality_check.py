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
    
    def check_distribution(
        self,
        records: list[CleanRecord],
        attribute: str,
    ) -> dict[str, int]:
        """Check record distribution by an attribute."""

        distribution: dict[str, int] = {}

        for record in records:
            value = record.attributes.get(
                attribute,
                "__unknown__",
            )
            key = str(value)

            distribution[key] = (
                distribution.get(key, 0) + 1
            )

        return distribution

    def check_split_distribution(
        self,
        splits: dict[
            str,
            list[CleanRecord],
        ],
        attribute: str,
    ) -> dict[
        str,
        dict[str, int],
    ]:
        """Return attribute distribution for each split."""

        return {
            split_name: self.check_distribution(
                records,
                attribute,
            )
            for split_name, records in splits.items()
        }

    def check_bias(
        self,
        records: list[CleanRecord],
        attribute: str,
        minimum_ratio: float = 0.05,
    ) -> list[str]:
        """
        Identify groups whose representation is below
        the configured minimum ratio.
        """

        if not 0.0 <= minimum_ratio <= 1.0:
            raise ValueError(
                "minimum_ratio must be between 0 and 1"
            )

        distribution = self.check_distribution(
            records,
            attribute,
        )

        total = len(records)

        if total == 0:
            return []

        warnings: list[str] = []

        for group, count in distribution.items():
            ratio = count / total

            if ratio < minimum_ratio:
                warnings.append(
                    f"Underrepresented group: "
                    f"{group} ({ratio:.2%})"
                )

        return warnings