from data.processing.cleaner import CleanRecord
from data.processing.labeler import (
    DataLabeler,
)


def test_explicit_labeling():
    record = CleanRecord(
        "1",
        "Hello",
    )

    result = DataLabeler().label(
        record,
        labels={
            "intent": "greeting",
            "emotion": "neutral",
        },
    )

    assert result.labels == {
        "intent": "greeting",
        "emotion": "neutral",
    }


def test_function_labeling():
    record = CleanRecord(
        "1",
        "Hello",
        attributes={
            "language": "en"
        },
    )

    labeler = DataLabeler(
        label_function=lambda item: {
            "language": item.attributes[
                "language"
            ]
        }
    )

    result = labeler.label(record)

    assert result.labels == {
        "language": "en"
    }