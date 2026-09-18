from data.processing.cleaner import CleanRecord
from data.processing.filter import DataFilter


def test_filter_by_minimum_length():
    records = [
        CleanRecord("1", "A"),
        CleanRecord("2", "ProjectAI"),
        CleanRecord("3", "Artificial Intelligence"),
    ]

    result = DataFilter(
        min_length=5
    ).filter(records)

    assert [record.record_id for record in result] == [
        "2",
        "3",
    ]


def test_filter_by_maximum_length():
    records = [
        CleanRecord("1", "Short"),
        CleanRecord(
            "2",
            "This record is much longer.",
        ),
    ]

    result = DataFilter(
        max_length=10
    ).filter(records)

    assert len(result) == 1
    assert result[0].record_id == "1"


def test_filter_custom_predicate():
    records = [
        CleanRecord(
            "1",
            "English",
            attributes={"language": "en"},
        ),
        CleanRecord(
            "2",
            "Vietnamese",
            attributes={"language": "vi"},
        ),
    ]

    result = DataFilter(
        predicate=lambda record:
        record.attributes.get("language") == "vi"
    ).filter(records)

    assert len(result) == 1
    assert result[0].record_id == "2"