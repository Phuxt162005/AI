from pathlib import Path

from data.collection.collector import RawDataCollector
from data.metadata.metadata import MetadataManager
from data.schemas.metadata_schema import MetadataSchema
from data.sources.source import DataSource, SourceType
from data.validation.input_validator import InputValidator


def create_collected_data(tmp_path: Path):
    original = tmp_path / "sample.txt"

    original.write_text(
        "ProjectAI raw data",
        encoding="utf-8",
    )

    source = DataSource(
        source_id="source_001",
        source_type=SourceType.FILE,
        name="sample.txt",
    )

    collector = RawDataCollector(
        tmp_path / "raw"
    )

    record = collector.collect_file(
        source=source,
        file_path=original,
        collection_id="collection_001",
    )

    manager = MetadataManager()

    metadata = MetadataSchema(
        metadata_id="meta_001",
        source_id="source_001",
        format="txt",
    )

    manager.add(metadata)

    return record, source, manager


def test_input_validation_passes(tmp_path: Path):
    record, source, manager = create_collected_data(
        tmp_path
    )

    validator = InputValidator()

    result = validator.validate(
        collection=record,
        source=source,
        metadata_manager=manager,
        metadata_id="meta_001",
    )

    assert result.valid is True
    assert result.errors == []
    assert record.processing_state.value == "validated"


def test_input_validation_requires_source(
    tmp_path: Path,
):
    record, _, manager = create_collected_data(
        tmp_path
    )

    validator = InputValidator()

    result = validator.validate(
        collection=record,
        source=None,
        metadata_manager=manager,
        metadata_id="meta_001",
    )

    assert result.valid is False
    assert "Source information is missing" in result.errors


def test_input_validation_requires_metadata(
    tmp_path: Path,
):
    record, source, manager = create_collected_data(
        tmp_path
    )

    validator = InputValidator()

    result = validator.validate(
        collection=record,
        source=source,
        metadata_manager=manager,
        metadata_id="missing_metadata",
    )

    assert result.valid is False
    assert (
        "Metadata not found: missing_metadata"
        in result.errors
    )


def test_input_validation_detects_missing_raw_file(
    tmp_path: Path,
):
    record, source, manager = create_collected_data(
        tmp_path
    )

    Path(record.raw_path).unlink()

    validator = InputValidator()

    result = validator.validate(
        collection=record,
        source=source,
        metadata_manager=manager,
        metadata_id="meta_001",
    )

    assert result.valid is False
    assert any(
        "Raw data does not exist"
        in error
        for error in result.errors
    )