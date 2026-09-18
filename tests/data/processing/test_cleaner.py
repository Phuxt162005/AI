from data.processing.cleaner import (
    CleanRecord,
    DataCleaner,
)


def test_cleaner_removes_invalid_characters():
    record = CleanRecord(
        record_id="record_001",
        content="\x00  ProjectAI  \n",
    )

    result = DataCleaner().clean(record)

    assert "\x00" not in result.content
    assert result.content == "ProjectAI"
    assert result.attributes["cleaned"] is True


def test_cleaner_preserves_record_identity():
    record = CleanRecord(
        record_id="record_002",
        content="Hello",
        source_id="source_001",
        metadata_id="metadata_001",
    )

    result = DataCleaner().clean(record)

    assert result.record_id == record.record_id
    assert result.source_id == record.source_id
    assert result.metadata_id == record.metadata_id