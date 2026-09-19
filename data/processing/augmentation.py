"""Data augmentation utilities."""

from __future__ import annotations

import random
from dataclasses import replace

from data.processing.cleaner import CleanRecord

class TextAugmenter:
    """Lightweight text augmentation utilities."""

    def __init__(self, seed: int | None = None) -> None:
        self.random = random.Random(seed)

    def random_deletion(
        self,
        record: CleanRecord,
        probability: float = 0.1,
    ) -> CleanRecord:
        """Randomly remove words from a text record."""

        if not 0.0 <= probability <= 1.0:
            raise ValueError("probability must be between 0 and 1")

        words = record.content.split()
        if len(words) <= 1:
            return record

        kept = [
            word
            for word in words
            if self.random.random() > probability
        ]

        if not kept:
            kept = [words[0]]

        attributes = dict(record.attributes)
        attributes["augmented"] = True
        attributes["augmentation"] = "random_deletion"

        return replace(
            record,
            content=" ".join(kept),
            attributes=attributes,
        )

    def random_swap(self, record: CleanRecord) -> CleanRecord:
        """Swap two random words."""

        words = record.content.split()
        if len(words) < 2:
            return record
        first, second = self.random.sample(range(len(words)), 2)
        words[first], words[second] = (
            words[second],
            words[first],
        )

        attributes = dict(record.attributes)
        attributes["augmented"] = True
        attributes["augmentation"] = "random_swap"

        return replace(
            record,
            content=" ".join(words),
            attributes=attributes,
        )

    def augment(self, record: CleanRecord, method: str) -> CleanRecord:
        """Apply a selected augmentation method."""

        if method == "random_deletion":
            return self.random_deletion(record)

        if method == "random_swap":
            return self.random_swap(record)

        raise ValueError(f"Unsupported augmentation method: {method}")