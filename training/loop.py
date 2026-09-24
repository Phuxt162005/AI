"""Training loop."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from self_built.model import Model
from self_built.tensor import Tensor

from training.checkpoint import CheckpointManager
from training.configuration import TrainingConfiguration
from training.resource_guard import (
    ResourceAction,
    ResourceController,
    ResourceLimits,
)


@dataclass
class TrainingHistory:
    """Training metrics collected during model training."""

    losses: list[float]

    stopped_safely: bool = False

    stop_reason: str | None = None

    checkpoint_path: str | None = None


class TrainingLoop:
    """Controls iterative training with resource protection."""

    def __init__(
        self,
        model: Model,
        resource_controller: ResourceController | None = None,
        checkpoint_manager: CheckpointManager | None = None,
        configuration: TrainingConfiguration | None = None,
    ) -> None:
        self.model = model

        self.configuration = (
            configuration
            or TrainingConfiguration()
        )

        self.configuration.validate()

        self.resource_controller = (
            resource_controller
            or ResourceController(
                limits=ResourceLimits()
            )
        )

        self.checkpoint_manager = (
            checkpoint_manager
            or CheckpointManager()
        )

    def train_batch(
        self,
        inputs: Tensor,
        targets: Tensor,
    ) -> float:
        self.model.train()

        predictions = self.model.forward(
            inputs
        )

        loss_value = (
            self.model.loss.forward(
                predictions,
                targets,
            )
        )

        gradient = self.model.loss.backward()

        self.model.network.backward(
            gradient
        )

        self.model.optimizer.step(
            self.model.network.gradients()
        )

        return loss_value

    def fit(
        self,
        inputs: Tensor,
        targets: Tensor,
        epochs: int = 1,
    ) -> TrainingHistory:
        if epochs <= 0:
            raise ValueError(
                "Number of epochs must be positive."
            )

        # -------------------------------------------------
        # PRE-FLIGHT
        # -------------------------------------------------

        self.resource_controller.preflight()

        losses: list[float] = []

        global_step = 0

        for epoch in range(epochs):

            # Check before every epoch.
            decision = (
                self.resource_controller.check()
            )

            if (
                decision.action
                == ResourceAction.CHECKPOINT
            ):
                checkpoint = self._save_emergency_checkpoint(
                    epoch=epoch,
                    step=global_step,
                    reason="resource_limit_before_epoch",
                )

                return TrainingHistory(
                    losses=losses,
                    stopped_safely=True,
                    stop_reason=(
                        "Resource limit exceeded "
                        "before epoch."
                    ),
                    checkpoint_path=str(
                        checkpoint
                    ),
                )

            loss = self.train_batch(
                inputs,
                targets,
            )

            losses.append(loss)

            global_step += 1

            # Periodic resource check.
            if (
                global_step
                % self.configuration.resource_check_interval
                == 0
            ):
                decision = (
                    self.resource_controller.check()
                )

                if (
                    decision.action
                    == ResourceAction.WARNING
                ):
                    print(
                        "[ResourceGuard] WARNING: "
                        "resource usage is approaching "
                        "the configured limit."
                    )

                elif (
                    decision.action
                    == ResourceAction.CHECKPOINT
                ):
                    checkpoint = (
                        self._save_emergency_checkpoint(
                            epoch=epoch,
                            step=global_step,
                            reason=(
                                "resource_limit_exceeded"
                            ),
                        )
                    )

                    return TrainingHistory(
                        losses=losses,
                        stopped_safely=True,
                        stop_reason=(
                            "Resource limit exceeded "
                            "during training."
                        ),
                        checkpoint_path=str(
                            checkpoint
                        ),
                    )

            # Mandatory check at epoch end.
            decision = (
                self.resource_controller.check()
            )

            if (
                decision.action
                == ResourceAction.CHECKPOINT
            ):
                checkpoint = (
                    self._save_emergency_checkpoint(
                        epoch=epoch,
                        step=global_step,
                        reason=(
                            "resource_limit_at_epoch_end"
                        ),
                    )
                )

                return TrainingHistory(
                    losses=losses,
                    stopped_safely=True,
                    stop_reason=(
                        "Resource limit exceeded "
                        "at epoch end."
                    ),
                    checkpoint_path=str(
                        checkpoint
                    ),
                )

        return TrainingHistory(
            losses=losses,
            stopped_safely=False,
        )

    def _save_emergency_checkpoint(
        self,
        epoch: int,
        step: int,
        reason: str,
    ):
        """
        Save a generic emergency checkpoint.

        The self-built model currently does not expose
        a dedicated state_dict API, so the model,
        optimizer and training metadata are persisted
        together.
        """

        state: dict[str, Any] = {
            "model": self.model,
            "optimizer": self.model.optimizer,
            "epoch": epoch,
            "step": step,
            "reason": reason,
            "configuration": (
                self.configuration
            ),
        }

        return self.checkpoint_manager.save(
            state,
            filename="emergency.pkl",
        )