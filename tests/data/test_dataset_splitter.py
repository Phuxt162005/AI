import pytest

from data.dataset.dataset import (
    DatasetRecord,
    TrainingDataset,
)
from data.dataset.splitter import (
    DatasetSplitter,
)


def make_dataset(
    count: int = 10,
) -> TrainingDataset:
    dataset = TrainingDataset(
        name="ProjectAI Test Dataset",
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


def test_split_ratios() -> None:
    dataset = make_dataset(100)

    splitter = DatasetSplitter(
        train_ratio=0.8,
        validation_ratio=0.1,
        test_ratio=0.1,
        seed=42,
    )

    split = splitter.split(dataset)

    assert len(split.train) == 80
    assert len(split.validation) == 10
    assert len(split.test) == 10


def test_split_contains_all_records() -> None:
    dataset = make_dataset(100)

    splitter = DatasetSplitter(seed=42)
    split = splitter.split(dataset)

    all_ids = (
        {
            record.record_id
            for record in split.train
        }
        | {
            record.record_id
            for record in split.validation
        }
        | {
            record.record_id
            for record in split.test
        }
    )

    assert all_ids == dataset.record_ids()

    assert (
        len(split.train)
        + len(split.validation)
        + len(split.test)
        == len(dataset)
    )


def test_split_has_no_leakage() -> None:
    dataset = make_dataset(100)

    splitter = DatasetSplitter(seed=42)
    split = splitter.split(dataset)

    assert splitter.has_leakage(split) is False

    leakage = splitter.find_leakage(split)

    assert leakage["train_validation"] == set()
    assert leakage["train_test"] == set()
    assert leakage["validation_test"] == set()


def test_split_is_reproducible() -> None:
    dataset = make_dataset(100)

    splitter_1 = DatasetSplitter(seed=42)
    splitter_2 = DatasetSplitter(seed=42)

    split_1 = splitter_1.split(dataset)
    split_2 = splitter_2.split(dataset)

    assert split_1.ids() == split_2.ids()


def test_different_seed_can_produce_different_split() -> None:
    dataset = make_dataset(100)

    splitter_1 = DatasetSplitter(seed=42)
    splitter_2 = DatasetSplitter(seed=123)

    split_1 = splitter_1.split(dataset)
    split_2 = splitter_2.split(dataset)

    assert split_1.ids() != split_2.ids()


def test_split_does_not_modify_dataset() -> None:
    dataset = make_dataset(20)

    original_ids = [
        record.record_id
        for record in dataset.records
    ]

    splitter = DatasetSplitter(seed=42)
    splitter.split(dataset)

    current_ids = [
        record.record_id
        for record in dataset.records
    ]

    assert current_ids == original_ids


def test_duplicate_record_ids_are_rejected() -> None:
    dataset = TrainingDataset(
        name="ProjectAI Test Dataset",
        version="1.0.0",
        dataset_type="instruction",
    )

    dataset.add_record(
        DatasetRecord(
            record_id="duplicate",
            input="Input 1",
        )
    )

    dataset.add_record(
        DatasetRecord(
            record_id="duplicate",
            input="Input 2",
        )
    )

    splitter = DatasetSplitter(seed=42)

    with pytest.raises(
        ValueError,
        match="duplicate record IDs",
    ):
        splitter.split(dataset)


def test_invalid_ratios_are_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="split ratios must sum to 1",
    ):
        DatasetSplitter(
            train_ratio=0.7,
            validation_ratio=0.2,
            test_ratio=0.2,
        )


def test_negative_ratios_are_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="split ratios must not be negative",
    ):
        DatasetSplitter(
            train_ratio=1.1,
            validation_ratio=-0.1,
            test_ratio=0.0,
        )


def test_sizes_returns_correct_values() -> None:
    dataset = make_dataset(100)

    splitter = DatasetSplitter(seed=42)
    split = splitter.split(dataset)

    assert split.sizes() == {
        "train": 80,
        "validation": 10,
        "test": 10,
    }


def test_split_ids_are_disjoint() -> None:
    dataset = make_dataset(100)

    splitter = DatasetSplitter(seed=42)
    split = splitter.split(dataset)

    ids = split.ids()

    assert ids["train"].isdisjoint(
        ids["validation"]
    )

    assert ids["train"].isdisjoint(
        ids["test"]
    )

    assert ids["validation"].isdisjoint(
        ids["test"]
    )