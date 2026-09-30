"""Dataset-driven training execution."""

from __future__ import annotations

from collections.abc import Callable

from data.dataset.dataloader import DataBatch, DataLoader
from data.dataset.dataset import TrainingDataset
from self_built.tensor import Tensor
from training.loop import TrainingHistory, TrainingLoop
from training.resource_guard import ResourceAction, ResourceState

BatchEncoder = Callable[[DataBatch], tuple[Tensor, Tensor]]

class TrainingExecutor:
    """Execute training over dataset batches."""

    def __init__(
        self,
        training_loop: TrainingLoop,
        dataset: TrainingDataset,
        batch_encoder: BatchEncoder,
    ) -> None:
        if not callable(batch_encoder):
            raise TypeError("batch_encoder must be callable.")

        self.training_loop = training_loop
        self.dataset = dataset
        self.batch_encoder = batch_encoder
        config = training_loop.configuration

        if config.dataset_type is not None:
            if config.dataset_type != dataset.dataset_type:
                raise ValueError(
                    "Configured dataset_type does not match "
                    "the supplied dataset."
                )

        if config.dataset_name is not None:
            if config.dataset_name != dataset.name:
                raise ValueError(
                    "Configured dataset_name does not match "
                    "the supplied dataset."
                )

        if config.dataset_version is not None:
            if config.dataset_version != dataset.version:
                raise ValueError(
                    "Configured dataset_version does not match "
                    "the supplied dataset."
                )

    def run(self) -> TrainingHistory:
        """Train the model using every batch in the dataset."""

        config = self.training_loop.configuration
        config.validate()

        if len(self.dataset) == 0:
            raise ValueError("Cannot train on an empty dataset.")

        if config.gradient_accumulation_steps != 1:
            raise NotImplementedError(
                "Gradient accumulation is not supported by the "
                "current optimizer/training loop. Set "
                "gradient_accumulation_steps=1."
            )

        loader = DataLoader(
            dataset=self.dataset,
            batch_size=config.batch_size,
            shuffle=config.shuffle,
            seed=config.seed,
            drop_last=config.drop_last,
        )

        if len(loader) == 0:
            raise ValueError(
                "DataLoader produced no batches. "
                "Check batch_size and drop_last."
            )

        controller = self.training_loop.resource_controller

        preflight = controller.preflight()
        if preflight.state != ResourceState.SAFE:
            raise RuntimeError(
                "Training blocked by Resource Guard before "
                f"training: state={preflight.state.value}"
            )

        losses: list[float] = []
        global_step = 0

        for epoch in range(config.epochs):
            for batch in loader:
                decision = controller.check()

                if decision.action == ResourceAction.CHECKPOINT:
                    checkpoint = (
                        self.training_loop._save_emergency_checkpoint(
                            epoch=epoch,
                            step=global_step,
                            reason="resource_limit_before_batch",
                        )
                    )
                    return TrainingHistory(
                        losses=losses,
                        stopped_safely=True,
                        stop_reason=(
                            "Resource limit exceeded before batch."
                        ),
                        checkpoint_path=str(checkpoint),
                    )

                inputs, targets = self.batch_encoder(batch)

                if not isinstance(inputs, Tensor):
                    raise TypeError("batch_encoder must return Tensor inputs.")

                if not isinstance(targets, Tensor):
                    raise TypeError("batch_encoder must return Tensor targets.")

                loss = self.training_loop.train_batch(inputs, targets)
                losses.append(float(loss))
                global_step += 1

                if (global_step % config.resource_check_interval == 0):
                    decision = controller.check()

                    if decision.action == ResourceAction.WARNING:
                        print(
                            "[ResourceGuard] WARNING: resource "
                            "usage is approaching the configured limit."
                        )

                    elif decision.action == ResourceAction.CHECKPOINT:
                        checkpoint = (
                            self.training_loop._save_emergency_checkpoint(
                                epoch=epoch,
                                step=global_step,
                                reason="resource_limit_exceeded",
                            )
                        )
                        return TrainingHistory(
                            losses=losses,
                            stopped_safely=True,
                            stop_reason=(
                                "Resource limit exceeded during training."
                            ),
                            checkpoint_path=str(checkpoint),
                        )

            # Mandatory resource check at the end of each epoch.
            decision = controller.check()
            if decision.action == ResourceAction.CHECKPOINT:
                checkpoint = (
                    self.training_loop._save_emergency_checkpoint(
                        epoch=epoch,
                        step=global_step,
                        reason="resource_limit_at_epoch_end",
                    )
                )
                return TrainingHistory(
                    losses=losses,
                    stopped_safely=True,
                    stop_reason=(
                        "Resource limit exceeded at epoch end."
                    ),
                    checkpoint_path=str(checkpoint),
                )

        return TrainingHistory(losses=losses, stopped_safely=False)