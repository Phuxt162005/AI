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
    result = run_training(tmp_path)

    assert result["epochs_completed"] > 0
    assert result["final_training_loss"] < result["first_training_loss"]
    assert result["test_total"] == 12
    assert 0.0 <= result["test_accuracy"] <= 1.0
    assert result["checkpoint_path"]
    assert (tmp_path / "metrics.json").exists()
    assert (tmp_path / "registry.json").exists()