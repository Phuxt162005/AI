from data.processing.augmentation import (
    TextAugmenter,
)
from data.processing.cleaner import CleanRecord


def test_random_deletion_is_reproducible():
    record = CleanRecord(
        "1",
        "one two three four",
    )

    augmenter = TextAugmenter(
        seed=42
    )

    result = augmenter.random_deletion(
        record,
        probability=0.5,
    )

    assert result.record_id == "1"
    assert result.attributes[
        "augmented"
    ] is True


def test_random_swap():
    record = CleanRecord(
        "1",
        "one two three",
    )

    augmenter = TextAugmenter(
        seed=42
    )

    result = augmenter.random_swap(
        record
    )

    assert result.record_id == "1"
    assert result.content != record.content
    assert result.attributes[
        "augmentation"
    ] == "random_swap"