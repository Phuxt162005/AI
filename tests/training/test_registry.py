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
    
@pytest.mark.parametrize("checkpoint_path", [None, "", "   "])
def test_register_model_rejects_invalid_checkpoint_path(
    tmp_path,
    checkpoint_path,
):
    registry = TrainingRegistry(tmp_path / "registry.json")
    run, _ = create_completed_run(registry)

    with pytest.raises(ValueError):
        registry.register_model(
            model_version="0.1.0",
            run_id=run.run_id,
            checkpoint_path=checkpoint_path,
        )


@pytest.mark.parametrize("metrics", ["invalid", 123, ["accuracy", 0.9]])
def test_register_model_rejects_non_dictionary_metrics(
    tmp_path,
    metrics,
):
    registry = TrainingRegistry(tmp_path / "registry.json")
    run, _ = create_completed_run(registry)

    with pytest.raises(TypeError):
        registry.register_model(
            model_version="0.1.0",
            run_id=run.run_id,
            checkpoint_path="model.pkl",
            metrics=metrics,
        )


def test_register_model_accepts_none_metrics_as_empty_dictionary(tmp_path):
    registry = TrainingRegistry(tmp_path / "registry.json")
    run, _ = create_completed_run(registry)

    model = registry.register_model(
        model_version="0.1.0",
        run_id=run.run_id,
        checkpoint_path="model.pkl",
        metrics=None,
    )

    assert model.metrics == {}


def test_register_model_rejects_non_string_description(tmp_path):
    registry = TrainingRegistry(tmp_path / "registry.json")
    run, _ = create_completed_run(registry)

    with pytest.raises(TypeError):
        registry.register_model(
            model_version="0.1.0",
            run_id=run.run_id,
            checkpoint_path="model.pkl",
            description=123,
        )


def test_get_run_rejects_unknown_run_id(tmp_path):
    registry = TrainingRegistry(tmp_path / "registry.json")

    with pytest.raises(KeyError):
        registry.get_run("run_does_not_exist")


def test_get_model_rejects_unknown_model_version(tmp_path):
    registry = TrainingRegistry(tmp_path / "registry.json")

    with pytest.raises(KeyError):
        registry.get_model("model_does_not_exist")


def test_list_runs_returns_registered_runs(tmp_path):
    registry = TrainingRegistry(tmp_path / "registry.json")

    first = registry.create_run({}, {"name": "first"})
    second = registry.create_run({}, {"name": "second"})

    runs = registry.list_runs()
    run_ids = {run.run_id for run in runs}

    assert len(runs) == 2
    assert run_ids == {first.run_id, second.run_id}


def test_list_models_returns_registered_models(tmp_path):
    registry = TrainingRegistry(tmp_path / "registry.json")
    run, _ = create_completed_run(registry)

    first = registry.register_model(
        "0.1.0",
        run.run_id,
        "model_1.pkl",
    )
    second = registry.register_model(
        "0.2.0",
        run.run_id,
        "model_2.pkl",
    )

    models = registry.list_models()
    model_versions = {model.model_version for model in models}

    assert len(models) == 2
    assert model_versions == {first.model_version, second.model_version}
    
def test_record_evaluation_links_model_and_training_run(tmp_path):
    registry = TrainingRegistry(tmp_path / "registry.json")
    run, _ = create_completed_run(registry)

    model = registry.register_model(
        model_version="0.1.0",
        run_id=run.run_id,
        checkpoint_path="checkpoints/model.pkl",
    )

    evaluation = registry.record_evaluation(
        model_version=model.model_version,
        result={
            "dataset_name": "evaluation-test",
            "dataset_version": "1.0",
            "evaluated_records": 20,
            "loss": 0.25,
            "mae": 0.4,
            "mse": 0.25,
        },
    )

    assert evaluation.model_version == model.model_version
    assert evaluation.run_id == run.run_id
    assert evaluation.result["loss"] == 0.25


def test_get_evaluation_returns_persisted_result(tmp_path):
    registry = TrainingRegistry(tmp_path / "registry.json")
    run, _ = create_completed_run(registry)

    model = registry.register_model(
        "0.1.0",
        run.run_id,
        "model.pkl",
    )

    evaluation = registry.record_evaluation(
        model_version=model.model_version,
        result={"accuracy": 0.9},
    )

    loaded = registry.get_evaluation(evaluation.evaluation_id)

    assert loaded.evaluation_id == evaluation.evaluation_id
    assert loaded.model_version == "0.1.0"
    assert loaded.result["accuracy"] == 0.9


def test_record_evaluation_rejects_unknown_model_version(tmp_path):
    registry = TrainingRegistry(tmp_path / "registry.json")

    with pytest.raises(KeyError):
        registry.record_evaluation(
            model_version="unknown",
            result={"loss": 0.5},
        )


def test_record_evaluation_rejects_non_dictionary_result(tmp_path):
    registry = TrainingRegistry(tmp_path / "registry.json")

    with pytest.raises(TypeError):
        registry.record_evaluation(
            model_version="0.1.0",
            result="invalid",
        )


def test_list_evaluations_can_filter_by_model_version(tmp_path):
    registry = TrainingRegistry(tmp_path / "registry.json")
    run, _ = create_completed_run(registry)

    model_1 = registry.register_model("0.1.0", run.run_id, "model_1.pkl")
    model_2 = registry.register_model("0.2.0", run.run_id, "model_2.pkl")

    registry.record_evaluation(
        model_version=model_1.model_version,
        result={"loss": 0.5},
    )
    registry.record_evaluation(
        model_version=model_2.model_version,
        result={"loss": 0.3},
    )

    evaluations = registry.list_evaluations(
        model_version=model_1.model_version,
    )

    assert len(evaluations) == 1
    assert evaluations[0].model_version == "0.1.0"


def test_list_evaluations_returns_all_results(tmp_path):
    registry = TrainingRegistry(tmp_path / "registry.json")
    run, _ = create_completed_run(registry)

    model = registry.register_model("0.1.0", run.run_id, "model.pkl")

    registry.record_evaluation(
        model_version=model.model_version,
        result={"loss": 0.5},
    )
    registry.record_evaluation(
        model_version=model.model_version,
        result={"loss": 0.3},
    )

    assert len(registry.list_evaluations()) == 2