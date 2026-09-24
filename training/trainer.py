"""Training resource configuration."""

from __future__ import annotations

from training.resource_guard import ResourceLimits


def configure_training_resources(
    limits: ResourceLimits,
) -> None:
    """
    Configure optional PyTorch resource limits.

    The ProjectAI self-built training engine does not
    require PyTorch. PyTorch limits are applied only
    when PyTorch is installed.
    """

    limits.validate()

    try:
        import torch
    except ImportError:
        return

    torch.set_num_threads(
        limits.max_cpu_threads
    )

    if torch.cuda.is_available():
        torch.cuda.set_per_process_memory_fraction(
            limits.max_gpu_memory_percent / 100.0
        )