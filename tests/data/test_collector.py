import hashlib
from pathlib import Path

from data.collection.collection_record import (
    CollectionMethod,
    ProcessingState,
)
from data.collection.collector import (
    RawDataCollector,
)
from data.sources.source import (
    DataSource,
    SourceType,
)


def create_source() -> DataSource:
    return DataSource(
        source_id="internal:test",
        source_type=SourceType.FILE,
        name="Test Dataset",
        location="test",
        version="1.0.0",
    )


def test_collect_file_preserves_raw_content(
    tmp_path: Path,
) -> None:
    source_file = tmp_path / "source.jsonl"
    source_file.write_text(
        '{"input": "Xin chào"}\n',
        encoding="utf-8",
    )

    raw_root = tmp_path / "raw"

    collector = RawDataCollector(raw_root)

    record = collector.collect_file(
        source=create_source(),
        file_path=source_file,
        collection_id="batch001",
        dataset_name="test_dataset",
    )

    destination = Path(record.raw_path)

    assert destination.exists()

    assert destination.read_text(
        encoding="utf-8"
    ) == source_file.read_text(
        encoding="utf-8"
    )


def test_collect_file_creates_collection_record(
    tmp_path: Path,
) -> None:
    source_file = tmp_path / "data.json"
    source_file.write_text(
        '{"test": true}',
        encoding="utf-8",
    )

    collector = RawDataCollector(
        tmp_path / "raw"
    )

    record = collector.collect_file(
        source=create_source(),
        file_path=source_file,
        collection_id="collection001",
    )

    assert record.collection_id == (
        "collection001"
    )

    assert record.source_id == (
        "internal:test"
    )

    assert record.collection_method == (
        CollectionMethod.DATASET_IMPORT
    )

    assert record.processing_state == (
        ProcessingState.COLLECTED
    )


def test_collect_file_records_size(
    tmp_path: Path,
) -> None:
    source_file = tmp_path / "data.txt"

    content = "ProjectAI Raw Data"

    source_file.write_text(
        content,
        encoding="utf-8",
    )

    collector = RawDataCollector(
        tmp_path / "raw"
    )

    record = collector.collect_file(
        source=create_source(),
        file_path=source_file,
        collection_id="collection002",
    )

    assert record.size_bytes == (
        source_file.stat().st_size
    )


def test_collect_file_records_checksum(
    tmp_path: Path,
) -> None:
    source_file = tmp_path / "data.txt"

    source_file.write_text(
        "checksum test",
        encoding="utf-8",
    )

    collector = RawDataCollector(
        tmp_path / "raw"
    )

    record = collector.collect_file(
        source=create_source(),
        file_path=source_file,
        collection_id="collection003",
    )

    checksum = record.attributes.get(
        "checksum_sha256"
    )

    expected = hashlib.sha256(
        source_file.read_bytes()
    ).hexdigest()

    assert checksum == expected


def test_collect_file_records_format(
    tmp_path: Path,
) -> None:
    source_file = tmp_path / "dataset.jsonl"

    source_file.write_text(
        "{}",
        encoding="utf-8",
    )

    collector = RawDataCollector(
        tmp_path / "raw"
    )

    record = collector.collect_file(
        source=create_source(),
        file_path=source_file,
        collection_id="collection004",
    )

    assert record.format == "jsonl"


def test_collect_file_rejects_missing_file(
    tmp_path: Path,
) -> None:
    collector = RawDataCollector(
        tmp_path / "raw"
    )

    missing_file = tmp_path / "missing.json"

    try:
        collector.collect_file(
            source=create_source(),
            file_path=missing_file,
            collection_id="collection005",
        )
    except FileNotFoundError:
        pass
    else:
        raise AssertionError(
            "Expected FileNotFoundError"
        )


def test_collect_file_rejects_directory(
    tmp_path: Path,
) -> None:
    collector = RawDataCollector(
        tmp_path / "raw"
    )

    source_directory = tmp_path / "dataset"
    source_directory.mkdir()

    try:
        collector.collect_file(
            source=create_source(),
            file_path=source_directory,
            collection_id="collection006",
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError"
        )