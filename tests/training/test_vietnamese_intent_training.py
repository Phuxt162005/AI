import json

from training.registry import TrainingRegistry
from examples.vietnamese_intent_training import (
    build_datasets,
    build_vocabulary,
    encode_batch,
    evaluate_accuracy,
    run_training,
)
from data.dataset.dataloader import DataLoader


def test_vietnamese_intent_dataset_split_is_disjoint():
    train, validation, test = build_datasets()

    train_ids = train.record_ids()
    validation_ids = validation.record_ids()
    test_ids = test.record_ids()

    assert train_ids.isdisjoint(validation_ids)
    assert train_ids.isdisjoint(test_ids)
    assert validation_ids.isdisjoint(test_ids)


def test_vocabulary_is_built_from_training_data_only():
    train, _, _ = build_datasets()
    vocabulary = build_vocabulary(train)

    assert vocabulary
    assert list(vocabulary.values()) == list(range(len(vocabulary)))


def test_encoder_produces_expected_tensor_shapes():
    train, _, _ = build_datasets()
    vocabulary = build_vocabulary(train)
    batch = next(iter(DataLoader(train, batch_size=4, shuffle=False)))

    inputs, targets = encode_batch(batch, vocabulary)

    assert inputs.shape == (4, len(vocabulary))
    assert targets.shape == (4, 6)
    assert all(abs(sum(row) - 1.0) < 1e-8 for row in targets.tolist())


def test_vietnamese_intent_training_end_to_end(tmp_path):
    _, _, test_dataset = build_datasets()

    result = run_training(tmp_path)

    assert result["epochs_completed"] > 0
    assert result["final_training_loss"] < result["first_training_loss"]

    # So sánh với số mẫu thực tế trong test dataset,
    # không hard-code số lượng mẫu.
    assert result["test_total"] == len(test_dataset)

    assert 0.0 <= result["test_accuracy"] <= 1.0
    assert result["test_correct"] <= result["test_total"]
    assert result["checkpoint_path"]
    assert (tmp_path / "metrics.json").exists()
    assert (tmp_path / "registry.json").exists()
    
    assert "confusion_matrix" in result
    assert "per_class_metrics" in result

    assert set(result["per_class_metrics"]) == set(result["labels"])

    assert 0.0 <= result["macro_precision"] <= 1.0
    assert 0.0 <= result["macro_recall"] <= 1.0
    assert 0.0 <= result["macro_f1"] <= 1.0

    matrix_total = sum(
        sum(row.values())
        for row in result["confusion_matrix"].values()
    )
    assert matrix_total == result["test_total"]

    assert sum(
        metrics["support"]
        for metrics in result["per_class_metrics"].values()
    ) == result["test_total"]
    
    evaluation_path = tmp_path / "evaluation.json"
    assert evaluation_path.exists()

    with evaluation_path.open("r", encoding="utf-8") as file:
        evaluation_artifact = json.load(file)

    assert evaluation_artifact["run_id"] == result["run_id"]
    assert evaluation_artifact["model_version"] == result["model_version"]
    assert evaluation_artifact["evaluation_id"] == result["evaluation_id"]
    assert evaluation_artifact["metrics"]["total"] == result["test_total"]
    assert evaluation_artifact["confusion_matrix"] == result["confusion_matrix"]
    assert evaluation_artifact["predictions"] == result["predictions"]

    registry = TrainingRegistry(tmp_path / "registry.json")

    registered_run = registry.get_run(result["run_id"])
    registered_model = registry.get_model(result["model_version"])
    registered_evaluation = registry.get_evaluation(result["evaluation_id"])

    assert registered_run.status == "completed"
    assert registered_run.evaluation_path == str(evaluation_path)
    assert registered_model.run_id == result["run_id"]
    assert registered_evaluation.run_id == result["run_id"]
    assert registered_evaluation.model_version == result["model_version"]
    assert registered_evaluation.result["metrics"]["total"] == result["test_total"]