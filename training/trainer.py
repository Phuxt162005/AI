import torch

from training.resource_guard import (
    ResourceLimits,
)


def configure_training_resources(
    limits: ResourceLimits,
) -> None:
    limits.validate()

    torch.set_num_threads(
        limits.max_cpu_threads
    )

    if torch.cuda.is_available():
        torch.cuda.set_per_process_memory_fraction(
            limits.max_gpu_memory_percent / 100.0
        )