import pytest

from data.collection.batch import CollectionBatch
from data.collection.collection_record import (
    CollectionMethod,
    CollectionRecord,
)

def create_record(collection_id: str, batch_id: str | None = None) -> CollectionRecord:
    return CollectionRecord(
        collection_id=collection_id,
        source_id="source_001",
        collection_method=CollectionMethod.MANUAL,
        raw_path=f"data/raw/{collection_id}.txt",
        batch_id=batch_id,
    )

def test_batch_add_record():
    batch = CollectionBatch(
        batch_id="batch_001",
        dataset_name="ProjectAI",
    )
    record = create_record("collection_001")
    batch.add_record(record)

    assert batch.record_count == 1
    assert record.batch_id == "batch_001"

def test_batch_get_record():
    batch = CollectionBatch(
        batch_id="batch_001",
        dataset_name="ProjectAI",
    )
    record = create_record("collection_001")
    batch.add_record(record)
    result = batch.get_record("collection_001")

    assert result is record

def test_batch_rejects_duplicate_record():
    batch = CollectionBatch(
        batch_id="batch_001",
        dataset_name="ProjectAI",
    )
    batch.add_record(create_record("collection_001"))

    with pytest.raises(ValueError):
        batch.add_record(create_record("collection_001"))


def test_batch_rejects_other_batch():
    batch = CollectionBatch(
        batch_id="batch_001",
        dataset_name="ProjectAI",
    )
    record = create_record(
        "collection_001",
        batch_id="batch_002",
    )

    with pytest.raises(ValueError):
        batch.add_record(record)