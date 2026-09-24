"""Training resource controller."""

from __future__ import annotations

from dataclasses import dataclass

from training.resource_guard.limits import (
    ResourceLimits,
)
from training.resource_guard.monitor import (
    ResourceMonitor,
    ResourceSnapshot,
)
from training.resource_guard.policy import (
    ResourceAction,
    ResourcePolicy,
    ResourceState,
)


@dataclass(frozen=True)
class ResourceDecision:
    state: ResourceState
    action: ResourceAction
    snapshot: ResourceSnapshot


class ResourceController:
    """Control training according to resource usage."""

    def __init__(
        self,
        limits: ResourceLimits | None = None,
        disk_path: str = ".",
    ) -> None:
        self.limits = limits or ResourceLimits()

        self.monitor = ResourceMonitor(
            disk_path=disk_path
        )

        self.policy = ResourcePolicy(
            self.limits
        )

    def check(self) -> ResourceDecision:
        snapshot = self.monitor.snapshot()

        state, action = (
            self.policy.evaluate(snapshot)
        )

        return ResourceDecision(
            state=state,
            action=action,
            snapshot=snapshot,
        )