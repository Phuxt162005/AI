"""Training, validation and test dataset splitting."""

from __future__ import annotations

import random
from dataclasses import dataclass

from data.dataset.dataset import (
    DatasetRecord,
    TrainingDataset,
)

@dataclass
class DatasetSplit:
    """Three-way dataset split."""

    train: list[DatasetRecord]
    validation: list[DatasetRecord]
    test: list[DatasetRecord]

    def sizes(self) -> dict[str, int]:
        """Return split sizes."""

        return {
            "train": len(self.train),
            "validation": len(self.validation),
            "test": len(self.test),
        }

    def ids(self) -> dict[str, set[str]]:
        """Return record IDs for every split."""

        return {
            "train": {
                record.record_id
                for record in self.train
            },
            "validation": {
                record.record_id
                for record in self.validation
            },
            "test": {
                record.record_id
                for record in self.test
            },
        }

class DatasetSplitter:
    """Split a dataset into train, validation and test sets."""

    def __init__(
        self,
        train_ratio: float = 0.8,
        validation_ratio: float = 0.1,
        test_ratio: float = 0.1,
        seed: int | None = 42,
    ) -> None:
        total = (
            train_ratio
            + validation_ratio
            + test_ratio
        )

        if abs(total - 1.0) > 1e-9:
            raise ValueError("split ratios must sum to 1")

        if any(
            ratio < 0
            for ratio in (
                train_ratio,
                validation_ratio,
                test_ratio,
            )
        ):
            raise ValueError("split ratios must not be negative")

        self.train_ratio = train_ratio
        self.validation_ratio = validation_ratio
        self.test_ratio = test_ratio
        self.seed = seed

    def split(self, dataset: TrainingDataset) -> DatasetSplit:
        """Create a reproducible random split."""

        records = list(dataset.records)
        self._validate_unique_ids(records)
        rng = random.Random(self.seed)
        rng.shuffle(records)
        total = len(records)
        train_count = int(total * self.train_ratio)
        validation_count = int(total * self.validation_ratio)
        train_end = train_count
        validation_end = (train_count + validation_count)

        return DatasetSplit(
            train=records[:train_end],
            validation=records[train_end:validation_end],
            test=records[validation_end:],
        )

    @staticmethod
    def _validate_unique_ids(records: list[DatasetRecord]) -> None:
        ids = [
            record.record_id
            for record in records
        ]

        if len(ids) != len(set(ids)):
            raise ValueError(
                "Dataset contains duplicate record IDs"
            )

    @staticmethod
    def find_leakage(split: DatasetSplit) -> dict[str, set[str]]:
        """Find overlapping record IDs between splits."""

        ids = split.ids()

        return {
            "train_validation": (
                ids["train"]
                & ids["validation"]
            ),
            "train_test": (
                ids["train"]
                & ids["test"]
            ),
            "validation_test": (
                ids["validation"]
                & ids["test"]
            ),
        }

    @staticmethod
    def has_leakage(split: DatasetSplit) -> bool:
        """Return whether any record ID overlaps."""

        leakage = DatasetSplitter.find_leakage(split)

        return any(
            bool(records)
            for records in leakage.values()
        )