from pathlib import Path

from training.checkpoint import (
    CheckpointManager,
)
from training.configuration import (
    TrainingConfiguration,
)
from training.loop import (
    TrainingLoop,
)
from training.resource_guard import (
    ResourceAction,
    ResourceDecision,
    ResourceSnapshot,
    ResourceState,
)


class FakeResourceController:
    def __init__(self, decisions):
        self.decisions = iter(decisions)

    def preflight(self):
        return next(self.decisions)

    def check(self):
        return next(self.decisions)


def safe_decision():
    return ResourceDecision(
        state=ResourceState.SAFE,
        action=ResourceAction.CONTINUE,
        snapshot=ResourceSnapshot(
            process_ram_gb=1.0,
            system_ram_used_gb=6.0,
            system_ram_available_gb=6.0,
            gpu_memory_used_gb=None,
            gpu_memory_total_gb=None,
            disk_free_gb=100.0,
        ),
    )