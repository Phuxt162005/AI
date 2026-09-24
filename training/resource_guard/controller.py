"""Training resource controller."""

from __future__ import annotations

from dataclasses import dataclass

from training.resource_guard.limits import ResourceLimits
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
        self.limits.validate()

        self.monitor = ResourceMonitor(
            disk_path=disk_path
        )

        self.policy = ResourcePolicy(
            self.limits
        )

    def check(self) -> ResourceDecision:
        """Check current resource usage."""

        snapshot = self.monitor.snapshot()

        state, action = self.policy.evaluate(
            snapshot
        )

        return ResourceDecision(
            state=state,
            action=action,
            snapshot=snapshot,
        )

    def preflight(self) -> ResourceDecision:
        """
        Check resources before training starts.

        Training is allowed only when the initial
        resource state is SAFE.
        """

        decision = self.check()

        if decision.state != ResourceState.SAFE:
            raise RuntimeError(
                self._format_block_message(
                    decision
                )
            )

        return decision

    @staticmethod
    def _format_block_message(
        decision: ResourceDecision,
    ) -> str:
        snapshot = decision.snapshot

        return (
            "Training blocked by Resource Guard. "
            f"state={decision.state.value}, "
            f"process_ram={snapshot.process_ram_gb:.2f}GB, "
            f"system_used={snapshot.system_ram_used_gb:.2f}GB, "
            f"available_ram={snapshot.system_ram_available_gb:.2f}GB, "
            f"disk_free={snapshot.disk_free_gb:.2f}GB"
        )