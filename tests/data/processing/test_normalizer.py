from data.processing.cleaner import CleanRecord
from data.processing.normalizer import TextNormalizer


def test_normalize_unicode():
    record = CleanRecord(
        "1",
        "Cafe\u0301",
    )

    result = TextNormalizer().normalize(record)

    assert result.content == "Café"
    assert result.attributes["normalized"] is True
    assert result.attributes["normalization_form"] == "NFC"


def test_normalize_whitespace():
    record = CleanRecord(
        "2",
        "ProjectAI    is\tan\nAI project.",
    )

    result = TextNormalizer().normalize(record)

    assert result.content == (
        "ProjectAI is an\nAI project."
    )


def test_normalize_line_endings():
    record = CleanRecord(
        "3",
        "line one\r\nline two\rline three",
    )

    result = TextNormalizer().normalize(record)

    assert result.content == (
        "line one\nline two\nline three"
    )