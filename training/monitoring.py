"""Training and validation metric monitoring."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EpochMetrics:
    epoch: int
    training_loss: float
    validation_loss: float | None
    generalization_gap: float | None
    possible_overfitting: bool


class TrainingMonitor:
    """Collect epoch-level training and validation metrics."""

    def __init__(self) -> None:
        self.history: list[EpochMetrics] = []

    def record_epoch(
        self,
        epoch: int,
        training_loss: float,
        validation_loss: float | None = None,
    ) -> EpochMetrics:
        if epoch < 1:
            raise ValueError("epoch must be at least 1.")

        if training_loss < 0:
            raise ValueError("training_loss must not be negative.")

        if validation_loss is not None and validation_loss < 0:
            raise ValueError("validation_loss must not be negative.")

        gap = (
            validation_loss - training_loss
            if validation_loss is not None
            else None
        )

        metrics = EpochMetrics(
            epoch=epoch,
            training_loss=training_loss,
            validation_loss=validation_loss,
            generalization_gap=gap,
            possible_overfitting=gap is not None and gap > 0,
        )
        self.history.append(metrics)
        return metrics