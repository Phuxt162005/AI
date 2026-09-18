from data.processing.cleaner import CleanRecord
from data.processing.deduplicator import DataDeduplicator


def test_exact_deduplication():
    records = [
        CleanRecord("1", "ProjectAI"),
        CleanRecord("2", "ProjectAI"),
        CleanRecord("3", "Another record"),
    ]

    result = DataDeduplicator().exact_deduplicate(
        records
    )

    assert len(result) == 2
    assert result[0].record_id == "1"
    assert result[1].record_id == "3"


def test_near_deduplication():
    records = [
        CleanRecord(
            "1",
            "ProjectAI is an AI assistant project.",
        ),
        CleanRecord(
            "2",
            "ProjectAI is an AI assistant project!",
        ),
        CleanRecord(
            "3",
            "This is a completely different record.",
        ),
    ]

    result = DataDeduplicator(
        similarity_threshold=0.90
    ).near_deduplicate(records)

    assert len(result) == 2


def test_deduplication_keeps_unique_records():
    records = [
        CleanRecord("1", "Alpha"),
        CleanRecord("2", "Beta"),
        CleanRecord("3", "Gamma"),
    ]

    result = DataDeduplicator().deduplicate(
        records
    )

    assert len(result) == 3