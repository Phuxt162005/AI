"""Training configuration."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TrainingConfiguration:
    """Configuration for safe local training."""

    batch_size: int = 1

    gradient_accumulation_steps: int = 8

    sequence_length: int = 128

    num_workers: int = 0

    mixed_precision: bool = True

    resource_check_interval: int = 20

    def validate(self) -> None:
        if self.batch_size < 1:
            raise ValueError(
                "batch_size must be at least 1."
            )

        if self.gradient_accumulation_steps < 1:
            raise ValueError(
                "gradient_accumulation_steps "
                "must be at least 1."
            )

        if self.sequence_length < 1:
            raise ValueError(
                "sequence_length must be at least 1."
            )

        if self.num_workers < 0:
            raise ValueError(
                "num_workers must not be negative."
            )

        if self.resource_check_interval < 1:
            raise ValueError(
                "resource_check_interval "
                "must be at least 1."
            )