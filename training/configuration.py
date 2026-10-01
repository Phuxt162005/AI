"""Training configuration."""

from __future__ import annotations

from dataclasses import asdict, dataclass

@dataclass(frozen=True)
class TrainingConfiguration:
    """Configuration for a ProjectAI training run."""

    # Training schedule
    epochs: int = 1
    learning_rate: float = 0.001
    seed: int = 42
    
    # Data loading
    batch_size: int = 1
    shuffle: bool = True
    drop_last: bool = False
    num_workers: int = 0

    # Model input
    sequence_length: int = 128

    # Optimization
    gradient_accumulation_steps: int = 1
    mixed_precision: bool = False

    # Resource monitoring
    resource_check_interval: int = 20

    # Dataset provenance
    dataset_name: str | None = None
    dataset_version: str | None = None
    dataset_type: str | None = None

    def validate(self) -> None:
        """Validate all configuration values."""

        if self.epochs < 1:
            raise ValueError("epochs must be at least 1.")

        if self.learning_rate <= 0:
            raise ValueError("learning_rate must be positive.")

        if self.batch_size < 1:
            raise ValueError("batch_size must be at least 1.")

        if self.gradient_accumulation_steps < 1:
            raise ValueError(
                "gradient_accumulation_steps "
                "must be at least 1."
            )

        if self.sequence_length < 1:
            raise ValueError("sequence_length must be at least 1.")

        if self.num_workers < 0:
            raise ValueError("num_workers must not be negative.")

        if self.resource_check_interval < 1:
            raise ValueError(
                "resource_check_interval "
                "must be at least 1."
            )

        if self.dataset_type is not None:
            supported_types = {
                "pre_training",
                "instruction",
                "conversation",
                "personality",
                "emotion",
                "multimodal",
                "preference",
            }

            if self.dataset_type not in supported_types:
                raise ValueError("Unsupported dataset_type: " f"{self.dataset_type}")

        if (
            self.dataset_name is not None
            and not self.dataset_name.strip()
        ):
            raise ValueError("dataset_name must not be empty.")

        if (
            self.dataset_version is not None
            and not self.dataset_version.strip()
        ):
            raise ValueError("dataset_version must not be empty.")
        
        if self.gradient_accumulation_steps != 1:
            raise NotImplementedError(
                "Gradient accumulation is not supported yet. "
                "Set gradient_accumulation_steps=1."
            )

        if self.mixed_precision:
            raise NotImplementedError("Mixed precision is not supported by the self-built Tensor engine.")

        if self.num_workers != 0:
            raise NotImplementedError(
                "Parallel DataLoader workers are not supported yet. "
                "Set num_workers=0."
            )

    def to_dict(self) -> dict:
        """Convert configuration to a serializable dictionary."""

        return asdict(self)