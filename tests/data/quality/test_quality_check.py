from data.processing.cleaner import CleanRecord
from data.quality.quality_check import (
    DataQualityChecker,
)


def test_quality_check_passes_valid_data():
    records = [
        CleanRecord(
            "1",
            "ProjectAI",
            source_id="source_001",
            metadata_id="metadata_001",
        ),
        CleanRecord(
            "2",
            "Artificial Intelligence",
            source_id="source_002",
            metadata_id="metadata_002",
        ),
    ]

    result = DataQualityChecker().check(records)

    assert result.valid is True
    assert result.record_count == 2
    assert result.errors == []
    assert result.empty_count == 0
    assert result.duplicate_count == 0


def test_quality_check_detects_empty_content():
    records = [
        CleanRecord(
            "1",
            "",
            source_id="source_001",
            metadata_id="metadata_001",
        )
    ]

    result = DataQualityChecker().check(records)

    assert result.valid is False
    assert result.empty_count == 1


def test_quality_check_detects_duplicates():
    records = [
        CleanRecord(
            "1",
            "ProjectAI",
        ),
        CleanRecord(
            "2",
            "ProjectAI",
        ),
    ]

    result = DataQualityChecker().check(records)

    assert result.valid is False
    assert result.duplicate_count == 1


def test_quality_check_warns_missing_metadata():
    records = [
        CleanRecord(
            "1",
            "ProjectAI",
            source_id=None,
            metadata_id=None,
        )
    ]

    result = DataQualityChecker().check(records)

    assert result.valid is True
    assert len(result.warnings) == 2