import json

import pytest

from training.registry import TrainingRegistry


def create_completed_run(registry):
    run = registry.create_run(
        configuration={"epochs": 3, "learning_rate": 0.001},
        dataset={
            "name": "sample",
            "version": "1.0",
            "type": "instruction",
        },
    )

    completed = registry.complete_run(
        run_id=run.run_id,
        metrics={"best_validation_loss": 0.25},
        checkpoint_path="checkpoints/best_model.pkl",
        evaluation_path="reports/evaluation.json",
    )

    return run, completed


def test_create_run_persists_running_status(tmp_path):
    registry = TrainingRegistry(tmp_path / "registry.json")

    run = registry.create_run(
        configuration={"epochs": 2},
        dataset={"name": "demo", "version": "1"},
    )

    loaded = registry.get_run(run.run_id)

    assert loaded.status == "running"
    assert loaded.configuration["epochs"] == 2
    assert loaded.dataset["name"] == "demo"


def test_complete_run_persists_metrics_and_artifacts(tmp_path):
    registry = TrainingRegistry(tmp_path / "registry.json")
    run, completed = create_completed_run(registry)

    loaded = registry.get_run(run.run_id)

    assert completed.status == "completed"
    assert loaded.metrics["best_validation_loss"] == 0.25
    assert loaded.checkpoint_path == "checkpoints/best_model.pkl"
    assert loaded.evaluation_path == "reports/evaluation.json"
    assert loaded.duration_seconds is not None


def test_fail_run_records_error(tmp_path):
    registry = TrainingRegistry(tmp_path / "registry.json")

    run = registry.create_run({}, {"name": "demo"})
    failed = registry.fail_run(run.run_id, "training error")

    assert failed.status == "failed"
    assert failed.error == "training error"


def test_cannot_complete_run_twice(tmp_path):
    registry = TrainingRegistry(tmp_path / "registry.json")
    run, _ = create_completed_run(registry)

    with pytest.raises(ValueError):
        registry.complete_run(run.run_id, metrics={})


def test_cannot_register_model_from_running_run(tmp_path):
    registry = TrainingRegistry(tmp_path / "registry.json")
    run = registry.create_run({}, {"name": "demo"})

    with pytest.raises(ValueError):
        registry.register_model(
            model_version="0.1.0",
            run_id=run.run_id,
            checkpoint_path="checkpoint.pkl",
        )


def test_register_and_retrieve_model_version(tmp_path):
    registry = TrainingRegistry(tmp_path / "registry.json")
    run, _ = create_completed_run(registry)

    model = registry.register_model(
        model_version="0.1.0",
        run_id=run.run_id,
        checkpoint_path="checkpoints/best_model.pkl",
        metrics={"accuracy": 0.9},
    )

    loaded = registry.get_model("0.1.0")

    assert loaded.run_id == run.run_id
    assert loaded.checkpoint_path == "checkpoints/best_model.pkl"
    assert loaded.metrics["accuracy"] == 0.9
    assert model.model_version == "0.1.0"


def test_duplicate_model_version_is_rejected(tmp_path):
    registry = TrainingRegistry(tmp_path / "registry.json")
    run, _ = create_completed_run(registry)

    registry.register_model("0.1.0", run.run_id, "model.pkl")

    with pytest.raises(ValueError):
        registry.register_model("0.1.0", run.run_id, "other.pkl")


def test_registry_file_contains_valid_json(tmp_path):
    path = tmp_path / "registry.json"
    registry = TrainingRegistry(path)
    registry.create_run({}, {"name": "demo"})

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    assert data["schema_version"] == 1
    assert len(data["training_runs"]) == 1