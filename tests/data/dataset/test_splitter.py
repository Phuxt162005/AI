from data.dataset.dataset import (
    DatasetRecord,
    TrainingDataset,
)
from data.dataset.splitter import DatasetSplitter


def create_dataset(count: int = 10) -> TrainingDataset:
    dataset = TrainingDataset(
        name="projectai",
        version="1.0.0",
        dataset_type="instruction",
    )

    for index in range(count):
        dataset.add_record(
            DatasetRecord(
                record_id=f"record_{index}",
                input=f"Input {index}",
                output=f"Output {index}",
            )
        )

    return dataset


def test_dataset_split():
    dataset = create_dataset(10)

    splitter = DatasetSplitter(
        train_ratio=0.8,
        validation_ratio=0.1,
        test_ratio=0.1,
        seed=42,
    )

    result = splitter.split(dataset)

    assert len(result.train) == 8
    assert len(result.validation) == 1
    assert len(result.test) == 1


def test_dataset_split_is_reproducible():
    dataset = create_dataset(20)

    splitter = DatasetSplitter(
        seed=42
    )

    first = splitter.split(dataset)
    second = splitter.split(dataset)

    assert [
        record.record_id
        for record in first.train
    ] == [
        record.record_id
        for record in second.train
    ]


def test_dataset_split_has_no_leakage():
    dataset = create_dataset(30)

    result = DatasetSplitter(
        seed=42
    ).split(dataset)

    assert DatasetSplitter.has_leakage(
        result
    ) is False


def test_dataset_split_preserves_all_records():
    dataset = create_dataset(25)

    result = DatasetSplitter(
        seed=42
    ).split(dataset)

    original_ids = dataset.record_ids()

    split_ids = (
        {
            record.record_id
            for record in result.train
        }
        |
        {
            record.record_id
            for record in result.validation
        }
        |
        {
            record.record_id
            for record in result.test
        }
    )

    assert split_ids == original_ids