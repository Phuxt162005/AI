import pytest

from self_built.layers import Linear
from self_built.losses import MSELoss
from self_built.model import Model
from self_built.network import Sequential
from self_built.optimizers import SGD
from training.checkpoint import CheckpointManager
from training.model_loader import ModelLoader
from training.registry import TrainingRegistry


def make_model():
    network = Sequential(
        Linear(input_size=1, output_size=1),
    )
    return Model(
        network=network,
        loss=MSELoss(),
        optimizer=SGD(learning_rate=0.01),
    )


def make_registered_model(tmp_path):
    registry = TrainingRegistry(tmp_path / "registry.json")
    checkpoint_manager = CheckpointManager(tmp_path / "checkpoints")

    run = registry.create_run(
        configuration={"epochs": 1},
        dataset={"name": "test", "version": "1.0"},
    )
    registry.complete_run(
        run_id=run.run_id,
        metrics={"loss": 0.1},
    )

    model = make_model()
    checkpoint_path = checkpoint_manager.save(
        {"model": model},
        filename="model.pkl",
    )

    registry.register_model(
        model_version="0.1.0",
        run_id=run.run_id,
        checkpoint_path=str(checkpoint_path),
    )

    return registry, checkpoint_manager


def test_load_model_from_registered_version(tmp_path):
    registry, checkpoint_manager = make_registered_model(tmp_path)

    loader = ModelLoader(
        registry=registry,
        checkpoint_manager=checkpoint_manager,
    )

    model = loader.load_model("0.1.0")

    assert isinstance(model, Model)
    assert model.network.training is False


def test_load_model_rejects_unknown_version(tmp_path):
    registry = TrainingRegistry(tmp_path / "registry.json")
    loader = ModelLoader(registry)

    with pytest.raises(KeyError):
        loader.load_model("unknown")


def test_load_model_rejects_invalid_checkpoint_model(tmp_path):
    registry = TrainingRegistry(tmp_path / "registry.json")
    checkpoint_manager = CheckpointManager(tmp_path / "checkpoints")

    run = registry.create_run({}, {"name": "test"})
    registry.complete_run(run.run_id, metrics={})

    checkpoint_path = checkpoint_manager.save(
        {"model": "not-a-model"},
        filename="invalid.pkl",
    )

    registry.register_model(
        model_version="0.1.0",
        run_id=run.run_id,
        checkpoint_path=str(checkpoint_path),
    )

    loader = ModelLoader(registry, checkpoint_manager)

    with pytest.raises(ValueError, match="valid ProjectAI Model"):
        loader.load_model("0.1.0")


def test_load_model_rejects_missing_checkpoint(tmp_path):
    registry = TrainingRegistry(tmp_path / "registry.json")

    run = registry.create_run({}, {"name": "test"})
    registry.complete_run(run.run_id, metrics={})

    registry.register_model(
        model_version="0.1.0",
        run_id=run.run_id,
        checkpoint_path=str(tmp_path / "missing.pkl"),
    )

    loader = ModelLoader(registry)

    with pytest.raises(FileNotFoundError):
        loader.load_model("0.1.0")