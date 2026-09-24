from pathlib import Path

import pytest

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
    """Fake resource controller for training-loop tests."""

    def __init__(self, decisions):
        self.decisions = iter(decisions)

    def preflight(self):
        return next(self.decisions)

    def check(self):
        return next(self.decisions)


def make_decision(
    state: ResourceState,
    action: ResourceAction,
):
    return ResourceDecision(
        state=state,
        action=action,
        snapshot=ResourceSnapshot(
            process_ram_gb=1.0,
            system_ram_used_gb=6.0,
            system_ram_available_gb=6.0,
            gpu_memory_used_gb=None,
            gpu_memory_total_gb=None,
            disk_free_gb=100.0,
        ),
    )


class FakeModel:
    """
    Minimal model used to test TrainingLoop control flow.

    It is intentionally independent from the real model
    implementation because these tests focus on resource
    protection rather than neural-network correctness.
    """

    def __init__(self):
        self.optimizer = object()
        self.network = FakeNetwork()
        self.loss = FakeLoss()

    def train(self):
        pass

    def forward(self, inputs):
        return inputs


class FakeNetwork:
    def backward(self, gradient):
        pass

    def gradients(self):
        return {}


class FakeLoss:
    def forward(self, predictions, targets):
        return 0.5

    def backward(self):
        return object()


def make_loop(
    controller,
    checkpoint_directory: Path,
):
    return TrainingLoop(
        model=FakeModel(),
        resource_controller=controller,
        checkpoint_manager=CheckpointManager(
            checkpoint_directory
        ),
        configuration=TrainingConfiguration(
            resource_check_interval=1
        ),
    )


def test_training_continues_when_resources_are_safe(
    tmp_path: Path,
):
    controller = FakeResourceController(
        [
            # preflight
            make_decision(
                ResourceState.SAFE,
                ResourceAction.CONTINUE,
            ),
            # before epoch
            make_decision(
                ResourceState.SAFE,
                ResourceAction.CONTINUE,
            ),
            # periodic check
            make_decision(
                ResourceState.SAFE,
                ResourceAction.CONTINUE,
            ),
            # epoch-end check
            make_decision(
                ResourceState.SAFE,
                ResourceAction.CONTINUE,
            ),
        ]
    )

    loop = make_loop(
        controller,
        tmp_path,
    )

    history = loop.fit(
        inputs=object(),
        targets=object(),
        epochs=1,
    )

    assert history.stopped_safely is False
    assert history.stop_reason is None
    assert history.checkpoint_path is None
    assert len(history.losses) == 1
    assert history.losses[0] == 0.5


def test_training_is_blocked_by_preflight(
    tmp_path: Path,
):
    controller = FakeResourceController(
        [
            make_decision(
                ResourceState.CRITICAL,
                ResourceAction.CHECKPOINT,
            )
        ]
    )

    loop = make_loop(
        controller,
        tmp_path,
    )

    with pytest.raises(RuntimeError):
        loop.fit(
            inputs=object(),
            targets=object(),
            epochs=1,
        )

    assert not list(tmp_path.iterdir())


def test_training_stops_and_checkpoints_when_resource_becomes_critical(
    tmp_path: Path,
):
    controller = FakeResourceController(
        [
            # preflight
            make_decision(
                ResourceState.SAFE,
                ResourceAction.CONTINUE,
            ),
            # before epoch
            make_decision(
                ResourceState.SAFE,
                ResourceAction.CONTINUE,
            ),
            # periodic check -> critical
            make_decision(
                ResourceState.CRITICAL,
                ResourceAction.CHECKPOINT,
            ),
        ]
    )

    loop = make_loop(
        controller,
        tmp_path,
    )

    history = loop.fit(
        inputs=object(),
        targets=object(),
        epochs=1,
    )

    assert history.stopped_safely is True

    assert (
        history.stop_reason
        == "Resource limit exceeded during training."
    )

    assert history.checkpoint_path is not None

    checkpoint = Path(
        history.checkpoint_path
    )

    assert checkpoint.exists()

    manager = CheckpointManager(
        tmp_path
    )

    state = manager.load(
        checkpoint
    )

    assert state["epoch"] == 0
    assert state["step"] == 1
    assert (
        state["reason"]
        == "resource_limit_exceeded"
    )


def test_training_stops_at_epoch_end_when_resource_becomes_critical(
    tmp_path: Path,
):
    controller = FakeResourceController(
        [
            # preflight
            make_decision(
                ResourceState.SAFE,
                ResourceAction.CONTINUE,
            ),
            # before epoch
            make_decision(
                ResourceState.SAFE,
                ResourceAction.CONTINUE,
            ),
            # periodic check
            make_decision(
                ResourceState.SAFE,
                ResourceAction.CONTINUE,
            ),
            # epoch-end check -> critical
            make_decision(
                ResourceState.CRITICAL,
                ResourceAction.CHECKPOINT,
            ),
        ]
    )

    loop = make_loop(
        controller,
        tmp_path,
    )

    history = loop.fit(
        inputs=object(),
        targets=object(),
        epochs=1,
    )

    assert history.stopped_safely is True

    assert (
        history.stop_reason
        == "Resource limit exceeded at epoch end."
    )

    assert history.checkpoint_path is not None

    checkpoint = Path(
        history.checkpoint_path
    )

    assert checkpoint.exists()


def test_warning_does_not_stop_training(
    tmp_path: Path,
):
    controller = FakeResourceController(
        [
            # preflight
            make_decision(
                ResourceState.SAFE,
                ResourceAction.CONTINUE,
            ),
            # before epoch
            make_decision(
                ResourceState.SAFE,
                ResourceAction.CONTINUE,
            ),
            # periodic check -> warning
            make_decision(
                ResourceState.WARNING,
                ResourceAction.WARNING,
            ),
            # epoch-end
            make_decision(
                ResourceState.SAFE,
                ResourceAction.CONTINUE,
            ),
        ]
    )

    loop = make_loop(
        controller,
        tmp_path,
    )

    history = loop.fit(
        inputs=object(),
        targets=object(),
        epochs=1,
    )

    assert history.stopped_safely is False
    assert len(history.losses) == 1