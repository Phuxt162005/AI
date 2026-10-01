from pathlib import Path
from types import SimpleNamespace

import pytest

from data.dataset.dataset import DatasetRecord, TrainingDataset
from self_built.tensor import Tensor
from training.checkpoint import CheckpointManager
from training.configuration import TrainingConfiguration
from training.execution import TrainingExecutor
from training.loop import TrainingLoop
from training.resource_guard import ResourceAction, ResourceState


class FakeOptimizer:
    def __init__(self):
        self.step_count = 0

    def step(self, gradients):
        self.step_count += 1


class FakeNetwork:
    def backward(self, gradient):
        pass

    def gradients(self):
        return []


class FakeLoss:
    def forward(self, predictions, targets):
        return 0.5

    def backward(self):
        return Tensor([0.0], (1,))


class FakeModel:
    def __init__(self):
        self.optimizer = FakeOptimizer()
        self.network = FakeNetwork()
        self.loss = FakeLoss()

    def train(self):
        pass

    def eval(self):
        pass

    def forward(self, inputs):
        return inputs

    def predict(self, inputs):
        return inputs


class FakeResourceController:
    def _decision(self):
        return SimpleNamespace(
            state=ResourceState.SAFE,
            action=ResourceAction.CONTINUE,
        )

    def preflight(self):
        return self._decision()

    def check(self):
        return self._decision()


class ScheduledValidationExecutor(TrainingExecutor):
    """Provide deterministic validation losses for control-flow tests."""

    def __init__(self, *args, validation_loss_schedule, **kwargs):
        super().__init__(*args, **kwargs)
        self.validation_loss_schedule = list(validation_loss_schedule)
        self.validation_call_count = 0

    def _evaluate_validation(self, loader):
        value = self.validation_loss_schedule[
            self.validation_call_count
        ]
        self.validation_call_count += 1
        return value


def make_dataset(name):
    return TrainingDataset(
        name=name,
        version="1.0",
        dataset_type="instruction",
        records=[
            DatasetRecord(
                record_id=f"{name}-1",
                input="1.0",
                output="2.0",
            ),
            DatasetRecord(
                record_id=f"{name}-2",
                input="3.0",
                output="4.0",
            ),
        ],
    )


def encode_batch(batch):
    inputs = Tensor([[float(value)] for value in batch.inputs])
    targets = Tensor([[float(value)] for value in batch.outputs])
    return inputs, targets


def make_executor(
    tmp_path: Path,
    validation_losses,
    epochs,
    patience=None,
    min_delta=0.0,
):
    model = FakeModel()

    loop = TrainingLoop(
        model=model,
        resource_controller=FakeResourceController(),
        checkpoint_manager=CheckpointManager(tmp_path),
        configuration=TrainingConfiguration(
            epochs=epochs,
            batch_size=2,
            shuffle=False,
            gradient_accumulation_steps=1,
        ),
    )

    executor = ScheduledValidationExecutor(
        training_loop=loop,
        dataset=make_dataset("train"),
        batch_encoder=encode_batch,
        validation_dataset=make_dataset("validation"),
        validation_encoder=encode_batch,
        early_stopping_patience=patience,
        min_delta=min_delta,
        validation_loss_schedule=validation_losses,
    )

    return executor, model, loop


def test_best_model_checkpoint_is_saved(tmp_path):
    executor, _, loop = make_executor(
        tmp_path,
        validation_losses=[0.8, 0.5, 0.6],
        epochs=3,
    )

    history = executor.run()

    assert history.best_validation_loss == 0.5
    assert history.best_epoch == 2
    assert history.early_stopped is False

    checkpoint_path = Path(history.checkpoint_path)
    assert checkpoint_path.exists()

    checkpoint = loop.checkpoint_manager.load(checkpoint_path)
    assert checkpoint["checkpoint_type"] == "best_model"
    assert checkpoint["epoch"] == 2
    assert checkpoint["validation_loss"] == 0.5


def test_early_stopping_stops_after_patience(tmp_path):
    executor, _, _ = make_executor(
        tmp_path,
        validation_losses=[0.5, 0.6, 0.7, 0.8, 0.9],
        epochs=5,
        patience=2,
    )

    history = executor.run()

    assert history.early_stopped is True
    assert history.best_epoch == 1
    assert len(history.validation_losses) == 3


def test_early_stopping_resets_when_validation_improves(tmp_path):
    executor, _, _ = make_executor(
        tmp_path,
        validation_losses=[0.5, 0.6, 0.4, 0.45, 0.46],
        epochs=5,
        patience=2,
    )

    history = executor.run()

    assert history.early_stopped is True
    assert history.best_epoch == 3
    assert history.best_validation_loss == 0.4
    assert len(history.validation_losses) == 5


def test_min_delta_controls_improvement(tmp_path):
    executor, _, _ = make_executor(
        tmp_path,
        validation_losses=[0.5, 0.495, 0.49],
        epochs=3,
        patience=2,
        min_delta=0.01,
    )

    history = executor.run()

    # Reductions smaller than min_delta are not improvements.
    assert history.best_epoch == 1
    assert history.early_stopped is True
    assert len(history.validation_losses) == 3


def test_early_stopping_requires_validation_dataset(tmp_path):
    model = FakeModel()
    loop = TrainingLoop(
        model=model,
        resource_controller=FakeResourceController(),
        checkpoint_manager=CheckpointManager(tmp_path),
        configuration=TrainingConfiguration(),
    )

    with pytest.raises(ValueError, match="requires a validation dataset"):
        TrainingExecutor(
            training_loop=loop,
            dataset=make_dataset("train"),
            batch_encoder=encode_batch,
            early_stopping_patience=2,
        )


@pytest.mark.parametrize("patience", [0, -1])
def test_early_stopping_rejects_invalid_patience(tmp_path, patience):
    with pytest.raises(ValueError, match="at least 1"):
        make_executor(
            tmp_path,
            validation_losses=[0.5],
            epochs=1,
            patience=patience,
        )


def test_early_stopping_rejects_negative_min_delta(tmp_path):
    with pytest.raises(ValueError, match="min_delta"):
        make_executor(
            tmp_path,
            validation_losses=[0.5],
            epochs=1,
            min_delta=-0.1,
        )