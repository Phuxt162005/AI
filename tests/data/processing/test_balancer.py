from data.processing.balancer import DatasetBalancer
from data.processing.cleaner import CleanRecord


def test_balance_limits_overrepresented_group():
    records = [
        CleanRecord(
            "1",
            "A",
            attributes={"language": "en"},
        ),
        CleanRecord(
            "2",
            "B",
            attributes={"language": "en"},
        ),
        CleanRecord(
            "3",
            "C",
            attributes={"language": "en"},
        ),
        CleanRecord(
            "4",
            "D",
            attributes={"language": "vi"},
        ),
    ]

    result = DatasetBalancer(
        max_records_per_group=2
    ).balance(
        records,
        group_attribute="language",
    )

    distribution = DatasetBalancer(
        max_records_per_group=2
    ).distribution(
        result,
        group_attribute="language",
    )

    assert distribution == {
        "en": 2,
        "vi": 1,
    }


def test_balance_preserves_record_order():
    records = [
        CleanRecord(
            "1",
            "A",
            attributes={"domain": "ai"},
        ),
        CleanRecord(
            "2",
            "B",
            attributes={"domain": "ai"},
        ),
        CleanRecord(
            "3",
            "C",
            attributes={"domain": "ai"},
        ),
    ]

    result = DatasetBalancer(
        max_records_per_group=2
    ).balance(
        records,
        group_attribute="domain",
    )

    assert [
        record.record_id
        for record in result
    ] == ["1", "2"]