from data.dataset.dataset import (
    DatasetRecord,
    TrainingDataset,
)
from data.dataset.splitter import (
    DatasetSplitter,
)
from data.processing.cleaner import CleanRecord
from data.quality.quality_check import (
    DataQualityChecker,
)


def test_distribution_check():
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
            attributes={"language": "vi"},
        ),
    ]

    result = DataQualityChecker().check_distribution(
        records,
        "language",
    )

    assert result == {
        "en": 2,
        "vi": 1,
    }


def test_bias_check_detects_underrepresented_group():
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
            attributes={"language": "en"},
        ),
        CleanRecord(
            "5",
            "E",
            attributes={"language": "vi"},
        ),
    ]

    warnings = DataQualityChecker().check_bias(
        records,
        "language",
        minimum_ratio=0.2,
    )

    assert len(warnings) == 0


def test_bias_check_detects_small_group():
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
            attributes={"language": "en"},
        ),
        CleanRecord(
            "5",
            "E",
            attributes={"language": "en"},
        ),
        CleanRecord(
            "6",
            "F",
            attributes={"language": "vi"},
        ),
    ]

    warnings = DataQualityChecker().check_bias(
        records,
        "language",
        minimum_ratio=0.2,
    )

    assert len(warnings) == 1
    assert "vi" in warnings[0]