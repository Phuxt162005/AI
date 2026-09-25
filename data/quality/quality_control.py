"""Quality control for ProjectAI datasets."""

from __future__ import annotations

from dataclasses import dataclass

from data.processing.cleaner import CleanRecord
from data.quality.quality_check import (
    DataQualityChecker,
    QualityResult,
)
from data.validation.record_validator import (RecordValidationResult)

@dataclass
class QualityControlResult:
    """Final quality-control result."""

    valid: bool
    input_count: int
    valid_count: int
    rejected_count: int
    quality_result: QualityResult
    validation_result: RecordValidationResult | None = None
    errors: list[str] | None = None

    @property
    def valid_ratio(self) -> float:
        """Return the ratio of valid records."""

        if self.input_count == 0:
            return 0.0
        return self.valid_count / self.input_count

class QualityController:
    """Apply quality thresholds to a processed dataset."""

    def __init__(self, minimum_valid_ratio: float = 0.95) -> None:
        if not 0.0 <= minimum_valid_ratio <= 1.0:
            raise ValueError(
                "minimum_valid_ratio must be "
                "between 0 and 1"
            )

        self.minimum_valid_ratio = (minimum_valid_ratio)
        self.checker = DataQualityChecker()

    def check(
        self,
        records: list[CleanRecord],
        *,
        validation_result: RecordValidationResult | None = None,
    ) -> QualityControlResult:
        """Run quality checks and apply the quality threshold."""

        quality_result = self.checker.check(records)
        input_count = (
            validation_result.input_count
            if validation_result is not None
            else len(records)
        )
        rejected_count = (
            validation_result.rejected_count
            if validation_result is not None
            else 0
        )
        valid_count = (input_count - rejected_count)
        errors = list(quality_result.errors)
        if (
            validation_result is not None
            and validation_result.errors
        ):
            errors.extend(validation_result.errors)
        valid_ratio = (
            valid_count / input_count
            if input_count > 0
            else 0.0
        )
        if valid_ratio < self.minimum_valid_ratio:
            errors.append(
                "Dataset valid ratio "
                f"{valid_ratio:.2%} is below "
                f"the required "
                f"{self.minimum_valid_ratio:.2%}"
            )
        valid = (
            not errors
            and quality_result.valid
            and valid_ratio >= self.minimum_valid_ratio
        )

        return QualityControlResult(
            valid=valid,
            input_count=input_count,
            valid_count=valid_count,
            rejected_count=rejected_count,
            quality_result=quality_result,
            validation_result=validation_result,
            errors=errors,
        )