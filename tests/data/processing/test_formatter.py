from data.processing.cleaner import CleanRecord
from data.processing.formatter import (
    DataFormatter,
)
from data.processing.labeler import (
    DataLabeler,
)


def test_formatter():
    record = CleanRecord(
        "1",
        "Hello AI",
        source_id="source_001",
        metadata_id="metadata_001",
        attributes={
            "language": "en"
        },
    )

    result = DataFormatter().format(
        record
    )

    assert result.record_id == "1"
    assert result.input == "Hello AI"
    assert result.output is None
    assert result.metadata["source_id"] == (
        "source_001"
    )
    assert result.metadata["language"] == "en"


def test_formatter_with_labels():
    record = CleanRecord(
        "1",
        "Hello",
    )

    labeled = DataLabeler().label(
        record,
        {"intent": "greeting"},
    )

    result = DataFormatter().format(
        labeled
    )

    assert result.labels == {
        "intent": "greeting"
    }