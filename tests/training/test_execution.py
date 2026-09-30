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
    def __init__(self):
        self.backward_count = 0

    def backward(self, gradient):
        self.backward_count += 1

    def gradients(self):
        return []


class FakeLoss:
    def forward(self, predictions, targets):
        if predictions.shape != targets.shape:
            raise ValueError("Prediction and target shapes must match.")
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

    def forward(self, inputs):
        return inputs


class FakeResourceController:
    def __init__(self, actions=None):
        self.actions = list(actions or [])
        self.index = 0

    def _decision(self):
        if self.index < len(self.actions):
            action = self.actions[self.index]
            self.index += 1
        else:
            action = ResourceAction.CONTINUE

        state = (
            ResourceState.CRITICAL
            if action == ResourceAction.CHECKPOINT
            else ResourceState.SAFE
        )

        return SimpleNamespace(
            state=state,
            action=action,
        )

    def preflight(self):
        return self._decision()

    def check(self):
        return self._decision()


def make_dataset():
    return TrainingDataset(
        name="test-dataset",
        version="1.0",
        dataset_type="instruction",
        records=[
            DatasetRecord(
                record_id="record-1",
                input="1.0",
                output="2.0",
            ),
            DatasetRecord(
                record_id="record-2",
                input="3.0",
                output="4.0",
            ),
            DatasetRecord(
                record_id="record-3",
                input="5.0",
                output="6.0",
            ),
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
    dataset=None,
    configuration=None,
    resource_controller=None,
):
    model = FakeModel()

    loop = TrainingLoop(
        model=model,
        resource_controller=(
            resource_controller or FakeResourceController()
        ),
        configuration=(
            configuration
            or TrainingConfiguration(
                epochs=1,
                batch_size=2,
                shuffle=False,
                gradient_accumulation_steps=1,
            )
        ),
    )

    executor = TrainingExecutor(
        training_loop=loop,
        dataset=dataset if dataset is not None else make_dataset(),
        batch_encoder=encode_batch,
    )

    return executor, model


def test_execution_runs_all_batches():
    executor, model = make_executor()

    history = executor.run()

    # 3 records, batch_size=2, epochs=1 => 2 batches.
    assert len(history.losses) == 2
    assert history.losses == [0.5, 0.5]
    assert history.stopped_safely is False
    assert model.optimizer.step_count == 2


def test_execution_runs_multiple_epochs():
    executor, model = make_executor(
        configuration=TrainingConfiguration(
            epochs=3,
            batch_size=2,
            shuffle=False,
            gradient_accumulation_steps=1,
        )
    )

    history = executor.run()

    # 2 batches per epoch × 3 epochs.
    assert len(history.losses) == 6
    assert model.optimizer.step_count == 6


def test_execution_rejects_empty_dataset():
    dataset = TrainingDataset(
        name="empty-dataset",
        version="1.0",
        dataset_type="instruction",
    )

    executor, _ = make_executor(dataset=dataset)

    with pytest.raises(ValueError, match="empty dataset"):
        executor.run()


def test_execution_rejects_invalid_encoder_result():
    executor, _ = make_executor()

    executor.batch_encoder = lambda batch: ([], [])

    with pytest.raises(TypeError, match="must return Tensor"):
        executor.run()


def test_execution_rejects_gradient_accumulation():
    executor, _ = make_executor(
        configuration=TrainingConfiguration(
            epochs=1,
            batch_size=2,
            gradient_accumulation_steps=2,
        )
    )

    with pytest.raises(NotImplementedError):
        executor.run()


def test_execution_stops_when_resource_limit_is_reached(
    tmp_path,
):
    controller = FakeResourceController(
        actions=[
            ResourceAction.CONTINUE,   # preflight
            ResourceAction.CONTINUE,   # before first batch
            ResourceAction.CHECKPOINT,  # before second batch
        ]
    )

    model = FakeModel()
    loop = TrainingLoop(
        model=model,
        resource_controller=controller,
        configuration=TrainingConfiguration(
            epochs=1,
            batch_size=1,
            shuffle=False,
            gradient_accumulation_steps=1,
        ),
    )

    # Dùng checkpoint manager trong thư mục test tạm.
    from training.checkpoint import CheckpointManager

    loop.checkpoint_manager = CheckpointManager(tmp_path)

    executor = TrainingExecutor(
        training_loop=loop,
        dataset=make_dataset(),
        batch_encoder=encode_batch,
    )

    history = executor.run()

    assert history.stopped_safely is True
    assert history.stop_reason == (
        "Resource limit exceeded before batch."
    )
    assert history.checkpoint_path is not None