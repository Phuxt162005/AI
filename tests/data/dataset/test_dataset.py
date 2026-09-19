from data.dataset.dataset import (
    DatasetRecord,
    TrainingDataset,
)


def test_training_dataset_creation():
    dataset = TrainingDataset(
        name="projectai-instruction",
        version="1.0.0",
        dataset_type="instruction",
    )

    assert dataset.name == (
        "projectai-instruction"
    )
    assert dataset.version == "1.0.0"
    assert dataset.dataset_type == "instruction"
    assert len(dataset) == 0


def test_training_dataset_add_record():
    dataset = TrainingDataset(
        name="projectai",
        version="1.0.0",
        dataset_type="conversation",
    )

    record = DatasetRecord(
        record_id="record_001",
        input="Hello",
        output="Hi",
    )

    dataset.add_record(record)

    assert len(dataset) == 1
    assert dataset.record_ids() == {
        "record_001"
    }


def test_training_dataset_supports_required_types():
    for dataset_type in (
        "pre_training",
        "instruction",
        "conversation",
        "personality",
        "emotion",
        "multimodal",
        "preference",
    ):
        dataset = TrainingDataset(
            name="projectai",
            version="1.0.0",
            dataset_type=dataset_type,
        )

        assert dataset.dataset_type == dataset_type