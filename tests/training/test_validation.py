from types import SimpleNamespace

import pytest

from data.dataset.dataset import DatasetRecord, TrainingDataset
from self_built.tensor import Tensor
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
        self.eval_count = 0
        self.predict_count = 0
        self.train_count = 0

    def train(self):
        self.train_count += 1

    def eval(self):
        self.eval_count += 1

    def forward(self, inputs):
        return inputs

    def predict(self, inputs):
        self.predict_count += 1
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


def make_dataset(name, values, dataset_type="instruction"):
    return TrainingDataset(
        name=name,
        version="1.0",
        dataset_type=dataset_type,
        records=[
            DatasetRecord(
                record_id=f"{name}-{index}",
                input=str(value),
                output=str(value * 2),
            )
            for index, value in enumerate(values)
        ],
    )


def encode_batch(batch):
    inputs = Tensor(
        [[float(value)] for value in batch.inputs]
    )
    targets = Tensor(
        [[float(value)] for value in batch.outputs]
    )
    return inputs, targets


def make_executor(
    train_dataset=None,
    validation_dataset=None,
    epochs=2,
    batch_size=1,
):
    model = FakeModel()

    configuration = TrainingConfiguration(
        epochs=epochs,
        batch_size=batch_size,
        shuffle=False,
        gradient_accumulation_steps=1,
    )

    loop = TrainingLoop(
        model=model,
        resource_controller=FakeResourceController(),
        configuration=configuration,
    )

    executor = TrainingExecutor(
        training_loop=loop,
        dataset=(
            train_dataset
            if train_dataset is not None
            else make_dataset("train", [1, 2])
        ),
        batch_encoder=encode_batch,
        validation_dataset=validation_dataset,
        validation_encoder=(
            encode_batch if validation_dataset is not None else None
        ),
    )

    return executor, model


def test_validation_runs_once_after_each_epoch():
    validation_dataset = make_dataset("validation", [3, 4])

    executor, model = make_executor(
        validation_dataset=validation_dataset,
        epochs=3,
    )

    history = executor.run()

    assert len(history.validation_losses) == 3
    assert model.eval_count == 3
    assert model.predict_count == 6


def test_validation_does_not_update_optimizer():
    validation_dataset = make_dataset("validation", [3, 4])

    executor, model = make_executor(
        validation_dataset=validation_dataset,
        epochs=2,
    )

    history = executor.run()

    # 2 training records × 2 epochs; validation must not add optimizer steps.
    assert model.optimizer.step_count == 4
    assert len(history.validation_losses) == 2


def test_validation_losses_are_recorded_in_history():
    validation_dataset = make_dataset("validation", [3, 4])

    executor, _ = make_executor(
        validation_dataset=validation_dataset,
        epochs=2,
    )

    history = executor.run()

    assert history.validation_losses == [0.5, 0.5]
    assert len(history.epoch_metrics) == 2
    assert history.epoch_metrics[0]["epoch"] == 1
    assert history.epoch_metrics[1]["epoch"] == 2


def test_training_without_validation_is_supported():
    executor, _ = make_executor(
        validation_dataset=None,
        epochs=2,
    )

    history = executor.run()

    assert history.validation_losses == []
    assert len(history.epoch_metrics) == 2
    assert all(
        item["validation_loss"] is None
        for item in history.epoch_metrics
    )


def test_validation_dataset_requires_encoder():
    model = FakeModel()
    loop = TrainingLoop(
        model=model,
        resource_controller=FakeResourceController(),
        configuration=TrainingConfiguration(
            gradient_accumulation_steps=1,
        ),
    )

    with pytest.raises(
        ValueError,
        match="validation_encoder is required",
    ):
        TrainingExecutor(
            training_loop=loop,
            dataset=make_dataset("train", [1, 2]),
            batch_encoder=encode_batch,
            validation_dataset=make_dataset("validation", [3]),
        )


def test_validation_rejects_empty_dataset():
    empty_validation = make_dataset("validation", [])

    with pytest.raises(
        ValueError,
        match="Validation dataset must not be empty",
    ):
        make_executor(validation_dataset=empty_validation)


def test_validation_rejects_mismatched_dataset_type():
    validation_dataset = make_dataset(
        "validation",
        [3, 4],
        dataset_type="emotion",
    )

    with pytest.raises(
        ValueError,
        match="dataset types must match",
    ):
        make_executor(validation_dataset=validation_dataset)