"""Resource safety policy."""

from enum import Enum

from training.resource_guard.limits import (
    ResourceLimits,
)
from training.resource_guard.monitor import (
    ResourceSnapshot,
)


class ResourceState(Enum):
    SAFE = "safe"
    WARNING = "warning"
    CRITICAL = "critical"


class ResourceAction(Enum):
    CONTINUE = "continue"
    WARNING = "warning"
    CHECKPOINT = "checkpoint"
    STOP = "stop"


class ResourcePolicy:
    """Convert resource usage into a safety state."""

    def __init__(
        self,
        limits: ResourceLimits,
    ) -> None:
        limits.validate()
        self.limits = limits

    def evaluate(
        self,
        snapshot: ResourceSnapshot,
    ) -> tuple[
        ResourceState,
        ResourceAction,
    ]:
        critical = (
            snapshot.process_ram_gb
            >= self.limits.max_training_ram_gb
            or
            snapshot.system_ram_used_gb
            >= self.limits.max_system_ram_gb
            or
            snapshot.system_ram_available_gb
            <= self.limits.min_available_ram_gb
            or
            snapshot.disk_free_gb
            <= self.limits.min_free_disk_gb
        )

        if (
            snapshot.gpu_memory_used_gb is not None
            and snapshot.gpu_memory_total_gb is not None
        ):
            gpu_percent = (
                snapshot.gpu_memory_used_gb
                / snapshot.gpu_memory_total_gb
                * 100
            )

            if gpu_percent >= (
                self.limits.max_gpu_memory_percent
            ):
                critical = True

        if critical:
            return (
                ResourceState.CRITICAL,
                ResourceAction.CHECKPOINT,
            )

        warning = (
            snapshot.process_ram_gb
            >= self.limits.max_training_ram_gb * 0.82
            or
            snapshot.system_ram_used_gb
            >= self.limits.max_system_ram_gb * 0.90
            or
            snapshot.system_ram_available_gb
            <= self.limits.min_available_ram_gb * 2
        )

        if (
            snapshot.gpu_memory_used_gb is not None
            and snapshot.gpu_memory_total_gb is not None
        ):
            gpu_percent = (
                snapshot.gpu_memory_used_gb
                / snapshot.gpu_memory_total_gb
                * 100
            )

            if gpu_percent >= 80:
                warning = True

        if warning:
            return (
                ResourceState.WARNING,
                ResourceAction.WARNING,
            )

        return (
            ResourceState.SAFE,
            ResourceAction.CONTINUE,
        )