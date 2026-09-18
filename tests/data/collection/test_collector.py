from pathlib import Path

from data.collection.collector import RawDataCollector
from data.collection.collection_record import (
    CollectionMethod,
    ProcessingState,
)
from data.sources.source import DataSource, SourceType

def test_collect_file_preserves_raw_content(tmp_path: Path):
    original = tmp_path / "original.txt"
    content = "ProjectAI raw data\nDữ liệu gốc."
    original.write_text(content, encoding="utf-8")
    raw_root = tmp_path / "raw"
    source = DataSource(
        source_id="source_001",
        source_type=SourceType.FILE,
        name="original.txt",
    )
    collector = RawDataCollector(raw_root)
    record = collector.collect_file(
        source=source,
        file_path=original,
        collection_id="collection_001",
        dataset_name="ProjectAI",
        dataset_version="1.0.0",
        batch_id="batch_001",
    )
    raw_file = Path(record.raw_path)

    assert raw_file.exists()
    assert raw_file.read_text(encoding="utf-8") == content
    assert record.source_id == "source_001"
    assert record.collection_id == "collection_001"
    assert record.processing_state == ProcessingState.COLLECTED

def test_collect_file_records_size_and_checksum(tmp_path: Path):
    original = tmp_path / "sample.txt"
    original.write_bytes(b"raw-data")
    source = DataSource(
        source_id="source_002",
        source_type=SourceType.FILE,
        name="sample.txt",
    )
    collector = RawDataCollector(
        tmp_path / "raw"
    )

    record = collector.collect_file(
        source=source,
        file_path=original,
        collection_id="collection_002",
    )

    assert record.size_bytes == len(b"raw-data")
    assert len(
        record.attributes["checksum_sha256"]
    ) == 64


def test_collect_file_requires_existing_file(tmp_path: Path):
    source = DataSource(
        source_id="source_003",
        source_type=SourceType.FILE,
        name="missing.txt",
    )

    collector = RawDataCollector(
        tmp_path / "raw"
    )

    missing = tmp_path / "missing.txt"

    try:
        collector.collect_file(
            source=source,
            file_path=missing,
            collection_id="collection_003",
        )
        assert False
    except FileNotFoundError:
        assert True