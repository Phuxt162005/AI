from data.collection.collection_record import (
    CollectionMethod,
    CollectionRecord,
    ProcessingState,
)


def test_create_collection_record():
    record = CollectionRecord(
        collection_id="collection_001",
        source_id="source_001",
        collection_method=CollectionMethod.DATASET_IMPORT,
        raw_path="data/raw/sample.json",
        dataset_name="ProjectAI",
        dataset_version="1.0.0",
        batch_id="batch_001",
        format="json",
        size_bytes=100,
    )

    assert record.collection_id == "collection_001"
    assert record.source_id == "source_001"
    assert record.collection_method == CollectionMethod.DATASET_IMPORT
    assert record.processing_state == ProcessingState.COLLECTED


def test_collection_record_state_changes():
    record = CollectionRecord(
        collection_id="collection_002",
        source_id="source_001",
        collection_method=CollectionMethod.MANUAL,
        raw_path="data/raw/sample.txt",
    )

    record.mark_validated()
    assert record.processing_state == ProcessingState.VALIDATED

    record.mark_processing()
    assert record.processing_state == ProcessingState.PROCESSING

    record.mark_processed()
    assert record.processing_state == ProcessingState.PROCESSED


def test_collection_record_to_dict():
    record = CollectionRecord(
        collection_id="collection_003",
        source_id="source_001",
        collection_method=CollectionMethod.API,
        raw_path="data/raw/api.json",
    )

    result = record.to_dict()

    assert result["collection_id"] == "collection_003"
    assert result["source_id"] == "source_001"
    assert result["collection_method"] == "api"
    assert result["processing_state"] == "collected"