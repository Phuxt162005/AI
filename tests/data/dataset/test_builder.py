from data.dataset.builder import DatasetBuilder
from data.processing.formatter import (
    DataFormatter,
)
from data.processing.cleaner import CleanRecord


def test_dataset_builder():
    records = [
        CleanRecord(
            record_id="1",
            content="Hello AI",
            source_id="source_001",
        ),
        CleanRecord(
            record_id="2",
            content="How are you?",
            source_id="source_002",
        ),
    ]

    formatted = DataFormatter().format_many(
        records
    )

    builder = DatasetBuilder(
        name="projectai-conversation",
        version="1.0.0",
        dataset_type="conversation",
    )

    builder.add_many(formatted)

    dataset = builder.build()

    assert len(dataset) == 2
    assert dataset.records[0].record_id == "1"
    assert dataset.records[1].record_id == "2"


def test_dataset_builder_preserves_metadata():
    record = CleanRecord(
        record_id="1",
        content="ProjectAI",
        source_id="source_001",
        metadata_id="metadata_001",
        attributes={
            "language": "en",
        },
    )

    formatted = DataFormatter().format(record)

    builder = DatasetBuilder(
        name="projectai",
        version="1.0.0",
        dataset_type="pre_training",
    )

    builder.add(formatted)

    dataset = builder.build()

    assert dataset.records[0].metadata[
        "source_id"
    ] == "source_001"

    assert dataset.records[0].metadata[
        "language"
    ] == "en"