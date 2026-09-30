"""Batch data loading for ProjectAI training datasets."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterator

from data.dataset.dataset import (DatasetRecord, TrainingDataset)

@dataclass
class DataBatch:
    """A batch of dataset records and their training fields."""

    records: list[DatasetRecord]
    inputs: list[str]
    outputs: list[str | None]
    labels: list[dict]
    token_ids: list[list[int] | None]

    def __len__(self) -> int:
        return len(self.records)

class DataLoader:
    """Iterate over a dataset in batches."""

    def __init__(
        self,
        dataset: TrainingDataset | list[DatasetRecord],
        batch_size: int = 32,
        shuffle: bool = False,
        seed: int | None = 42,
        drop_last: bool = False,
    ) -> None:
        if batch_size <= 0:
            raise ValueError("batch_size must be positive")

        if isinstance(dataset, TrainingDataset):
            self.records = list(dataset.records)
        else:
            self.records = list(dataset)

        self.batch_size = batch_size
        self.shuffle = shuffle
        self.seed = seed
        self.drop_last = drop_last
        self._iteration = 0

    def __len__(self) -> int:
        """Return the number of batches."""

        count = len(self.records)

        if self.drop_last:
            return count // self.batch_size

        return (count + self.batch_size - 1) // self.batch_size

    def __iter__(self) -> Iterator[DataBatch]:
        """Yield batches without modifying source records."""

        indices = list(range(len(self.records)))
        if self.shuffle:
            if self.seed is None:
                random.shuffle(indices)
            else:
                rng = random.Random(self.seed + self._iteration)
                rng.shuffle(indices)
        self._iteration += 1

        for start in range(0, len(indices), self.batch_size):
            batch_indices = indices[start : start + self.batch_size]

            if (self.drop_last and len(batch_indices) < self.batch_size):
                break

            records = [self.records[index] for index in batch_indices]

            yield DataBatch(
                records=records,
                inputs=[record.input for record in records],
                outputs=[record.output for record in records],
                labels=[dict(record.labels) for record in records],
                token_ids=[self._get_token_ids(record) for record in records],
            )

    @staticmethod
    def _get_token_ids(record: DatasetRecord) -> list[int] | None:
        """Read token IDs stored by preprocessing."""

        value = record.metadata.get("token_ids")
        if value is None:
            return None

        if not isinstance(value, list):
            raise TypeError("record metadata token_ids must be a list")

        if any(not isinstance(token, int) for token in value):
            raise TypeError("record metadata token_ids must contain integers")

        return list(value)