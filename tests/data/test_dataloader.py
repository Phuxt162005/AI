import pytest

from data.dataset.dataloader import (
    DataLoader,
)
from data.dataset.dataset import (
    DatasetRecord,
    TrainingDataset,
)


def make_dataset(count: int = 10) -> TrainingDataset:
    dataset = TrainingDataset(
        name="ProjectAI DataLoader Test",
        version="1.0.0",
        dataset_type="instruction",
    )

    for index in range(count):
        dataset.add_record(
            DatasetRecord(
                record_id=f"record_{index}",
                input=f"Input {index}",
                output=f"Output {index}",
                labels={"index": index},
                metadata={
                    "token_ids": [index, index + 1],
                },
            )
        )

    return dataset


def collect_ids(loader: DataLoader) -> list[str]:
    return [
        record.record_id
        for batch in loader
        for record in batch.records
    ]


def test_dataloader_batches_records() -> None:
    loader = DataLoader(
        make_dataset(10),
        batch_size=4,
    )

    batches = list(loader)

    assert len(batches) == 3
    assert [len(batch) for batch in batches] == [4, 4, 2]


def test_dataloader_keeps_all_records() -> None:
    dataset = make_dataset(11)
    loader = DataLoader(dataset, batch_size=3)

    loaded_ids = collect_ids(loader)

    assert len(loaded_ids) == len(dataset)
    assert set(loaded_ids) == dataset.record_ids()


def test_dataloader_drop_last() -> None:
    loader = DataLoader(
        make_dataset(10),
        batch_size=4,
        drop_last=True,
    )

    batches = list(loader)

    assert len(batches) == 2
    assert [len(batch) for batch in batches] == [4, 4]


def test_dataloader_shuffle_is_reproducible() -> None:
    dataset = make_dataset(20)

    loader_1 = DataLoader(
        dataset,
        batch_size=5,
        shuffle=True,
        seed=42,
    )
    loader_2 = DataLoader(
        dataset,
        batch_size=5,
        shuffle=True,
        seed=42,
    )

    assert collect_ids(loader_1) == collect_ids(loader_2)


def test_dataloader_shuffle_does_not_modify_dataset() -> None:
    dataset = make_dataset(20)
    original_ids = [
        record.record_id
        for record in dataset.records
    ]

    loader = DataLoader(
        dataset,
        batch_size=4,
        shuffle=True,
        seed=42,
    )
    list(loader)

    assert [
        record.record_id
        for record in dataset.records
    ] == original_ids


def test_batch_preserves_training_fields() -> None:
    loader = DataLoader(
        make_dataset(2),
        batch_size=2,
    )

    batch = next(iter(loader))

    assert batch.inputs == ["Input 0", "Input 1"]
    assert batch.outputs == ["Output 0", "Output 1"]
    assert batch.labels == [
        {"index": 0},
        {"index": 1},
    ]
    assert batch.token_ids == [[0, 1], [1, 2]]


def test_batch_supports_records_without_token_ids() -> None:
    record = DatasetRecord(
        record_id="record_1",
        input="Hello",
        output="Hi",
    )

    batch = next(
        iter(
            DataLoader(
                [record],
                batch_size=1,
            )
        )
    )

    assert batch.token_ids == [None]


def test_dataloader_empty_dataset() -> None:
    loader = DataLoader(
        make_dataset(0),
        batch_size=4,
    )

    assert len(loader) == 0
    assert list(loader) == []


def test_dataloader_rejects_invalid_batch_size() -> None:
    with pytest.raises(
        ValueError,
        match="batch_size must be positive",
    ):
        DataLoader(
            make_dataset(),
            batch_size=0,
        )


def test_dataloader_rejects_invalid_token_ids() -> None:
    record = DatasetRecord(
        record_id="record_1",
        input="Hello",
        metadata={"token_ids": "invalid"},
    )

    loader = DataLoader([record], batch_size=1)

    with pytest.raises(
        TypeError,
        match="token_ids must be a list",
    ):
        list(loader)