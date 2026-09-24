"""Resource limits for safe local training."""

from dataclasses import dataclass

@dataclass(frozen=True)
class ResourceLimits:
    """Limits used to protect the host system during training."""

    # RAM used by the training process.
    max_training_ram_gb: float = 5.5

    # Total RAM used by the whole system.
    max_system_ram_gb: float = 12.5

    # Minimum RAM that should remain available.
    min_available_ram_gb: float = 2.0

    # Maximum percentage of GPU VRAM that training may use.
    max_gpu_memory_percent: float = 90.0

    # Minimum free disk space.
    min_free_disk_gb: float = 10.0

    # Number of CPU threads allowed for PyTorch CPU operations.
    max_cpu_threads: int = 4

    def validate(self) -> None:
        if self.max_training_ram_gb <= 0:
            raise ValueError("max_training_ram_gb must be greater than 0")

        if self.max_system_ram_gb <= 0:
            raise ValueError("max_system_ram_gb must be greater than 0")

        if self.min_available_ram_gb < 0:
            raise ValueError("min_available_ram_gb must not be negative")

        if not 0 < self.max_gpu_memory_percent <= 100:
            raise ValueError("max_gpu_memory_percent must be in (0, 100]")

        if self.min_free_disk_gb < 0:
            raise ValueError("min_free_disk_gb must not be negative")

        if self.max_cpu_threads < 1:
            raise ValueError("max_cpu_threads must be at least 1")