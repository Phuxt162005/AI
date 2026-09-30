"""Dataset-driven training execution with validation monitoring."""

from __future__ import annotations

from collections.abc import Callable

from data.dataset.dataloader import DataBatch, DataLoader
from data.dataset.dataset import TrainingDataset
from self_built.tensor import Tensor
from training.loop import TrainingHistory, TrainingLoop
from training.monitoring import TrainingMonitor
from training.resource_guard import ResourceAction, ResourceState

BatchEncoder = Callable[[DataBatch], tuple[Tensor, Tensor]]


class TrainingExecutor:
    """Execute training batches and optional epoch-level validation."""

    def __init__(
        self,
        training_loop: TrainingLoop,
        dataset: TrainingDataset,
        batch_encoder: BatchEncoder,
        validation_dataset: TrainingDataset | None = None,
        validation_encoder: BatchEncoder | None = None,
    ) -> None:
        if not callable(batch_encoder):
            raise TypeError("batch_encoder must be callable.")

        if validation_dataset is not None and validation_encoder is None:
            raise ValueError(
                "validation_encoder is required when "
                "validation_dataset is provided."
            )

        if validation_encoder is not None and not callable(validation_encoder):
            raise TypeError("validation_encoder must be callable.")

        self.training_loop = training_loop
        self.dataset = dataset
        self.batch_encoder = batch_encoder
        self.validation_dataset = validation_dataset
        self.validation_encoder = validation_encoder
        self.monitor = TrainingMonitor()

        config = training_loop.configuration

        for configured, actual, field_name in (
            (config.dataset_type, dataset.dataset_type, "dataset_type"),
            (config.dataset_name, dataset.name, "dataset_name"),
            (config.dataset_version, dataset.version, "dataset_version"),
        ):
            if configured is not None and configured != actual:
                raise ValueError(
                    f"Configured {field_name} does not match "
                    "the supplied training dataset."
                )

        if validation_dataset is not None:
            if len(validation_dataset) == 0:
                raise ValueError("Validation dataset must not be empty.")

            if validation_dataset.dataset_type != dataset.dataset_type:
                raise ValueError(
                    "Training and validation dataset types must match."
                )

    def _evaluate_validation(self, loader: DataLoader) -> float:
        """Evaluate validation batches without optimizer updates."""

        model = self.training_loop.model
        model.eval()

        total_loss = 0.0
        total_records = 0

        assert self.validation_encoder is not None

        for batch in loader:
            inputs, targets = self.validation_encoder(batch)

            if not isinstance(inputs, Tensor):
                raise TypeError(
                    "validation_encoder must return Tensor inputs."
                )

            if not isinstance(targets, Tensor):
                raise TypeError(
                    "validation_encoder must return Tensor targets."
                )

            predictions = model.predict(inputs)
            loss = model.loss.forward(predictions, targets)

            batch_size = len(batch)
            total_loss += float(loss) * batch_size
            total_records += batch_size

        if total_records == 0:
            raise ValueError("Validation DataLoader produced no records.")

        return total_loss / total_records

    def run(self) -> TrainingHistory:
        """Train over batches and validate after each completed epoch."""

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

        train_loader = DataLoader(
            dataset=self.dataset,
            batch_size=config.batch_size,
            shuffle=config.shuffle,
            seed=config.seed,
            drop_last=config.drop_last,
        )

        if len(train_loader) == 0:
            raise ValueError(
                "Training DataLoader produced no batches. "
                "Check batch_size and drop_last."
            )

        validation_loader = None
        if self.validation_dataset is not None:
            validation_loader = DataLoader(
                dataset=self.validation_dataset,
                batch_size=config.batch_size,
                shuffle=False,
                seed=config.seed,
                drop_last=False,
            )

        controller = self.training_loop.resource_controller
        preflight = controller.preflight()

        if preflight.state != ResourceState.SAFE:
            raise RuntimeError(
                "Training blocked by Resource Guard before "
                f"training: state={preflight.state.value}"
            )

        losses: list[float] = []
        validation_losses: list[float] = []
        epoch_metrics: list[dict[str, float | int | bool | None]] = []
        global_step = 0

        for epoch in range(config.epochs):
            epoch_training_losses: list[float] = []

            for batch in train_loader:
                decision = controller.check()

                if decision.action == ResourceAction.CHECKPOINT:
                    checkpoint = self.training_loop._save_emergency_checkpoint(
                        epoch=epoch,
                        step=global_step,
                        reason="resource_limit_before_batch",
                    )
                    return TrainingHistory(
                        losses=losses,
                        stopped_safely=True,
                        stop_reason="Resource limit exceeded before batch.",
                        checkpoint_path=str(checkpoint),
                        validation_losses=validation_losses,
                        epoch_metrics=epoch_metrics,
                    )

                inputs, targets = self.batch_encoder(batch)

                if not isinstance(inputs, Tensor):
                    raise TypeError(
                        "batch_encoder must return Tensor inputs."
                    )

                if not isinstance(targets, Tensor):
                    raise TypeError(
                        "batch_encoder must return Tensor targets."
                    )

                loss = float(
                    self.training_loop.train_batch(inputs, targets)
                )
                losses.append(loss)
                epoch_training_losses.append(loss)
                global_step += 1

                if global_step % config.resource_check_interval == 0:
                    decision = controller.check()

                    if decision.action == ResourceAction.WARNING:
                        print(
                            "[ResourceGuard] WARNING: resource usage "
                            "is approaching the configured limit."
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
                            validation_losses=validation_losses,
                            epoch_metrics=epoch_metrics,
                        )

            decision = controller.check()

            if decision.action == ResourceAction.CHECKPOINT:
                checkpoint = self.training_loop._save_emergency_checkpoint(
                    epoch=epoch,
                    step=global_step,
                    reason="resource_limit_at_epoch_end",
                )
                return TrainingHistory(
                    losses=losses,
                    stopped_safely=True,
                    stop_reason=(
                        "Resource limit exceeded at epoch end."
                    ),
                    checkpoint_path=str(checkpoint),
                    validation_losses=validation_losses,
                    epoch_metrics=epoch_metrics,
                )

            training_loss = (
                sum(epoch_training_losses) / len(epoch_training_losses)
            )

            validation_loss = None
            if validation_loader is not None:
                validation_loss = self._evaluate_validation(
                    validation_loader
                )
                validation_losses.append(validation_loss)

            metrics = self.monitor.record_epoch(
                epoch=epoch + 1,
                training_loss=training_loss,
                validation_loss=validation_loss,
            )

            epoch_metrics.append(
                {
                    "epoch": metrics.epoch,
                    "training_loss": metrics.training_loss,
                    "validation_loss": metrics.validation_loss,
                    "generalization_gap": metrics.generalization_gap,
                    "possible_overfitting": metrics.possible_overfitting,
                }
            )

        return TrainingHistory(
            losses=losses,
            stopped_safely=False,
            validation_losses=validation_losses,
            epoch_metrics=epoch_metrics,
        )