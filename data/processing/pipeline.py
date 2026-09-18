"""Data cleaning and processing pipeline."""

from __future__ import annotations

from dataclasses import dataclass

from data.processing.balancer import DatasetBalancer
from data.processing.cleaner import CleanRecord, DataCleaner
from data.processing.deduplicator import DataDeduplicator
from data.processing.filter import DataFilter
from data.processing.normalizer import TextNormalizer

@dataclass
class ProcessingResult:
    """Result of processing a collection of records."""

    records: list[CleanRecord]
    input_count: int
    cleaned_count: int
    deduplicated_count: int
    filtered_count: int
    normalized_count: int
    balanced_count: int

    @property
    def output_count(self) -> int:
        """Return the final number of records."""

        return len(self.records)

class DataProcessingPipeline:
    """Run Cleaning → Deduplication → Filtering → Normalization."""

    def __init__(
        self,
        cleaner: DataCleaner | None = None,
        deduplicator: DataDeduplicator | None = None,
        data_filter: DataFilter | None = None,
        normalizer: TextNormalizer | None = None,
        balancer: DatasetBalancer | None = None,
    ) -> None:
        self.cleaner = (
            cleaner
            if cleaner is not None
            else DataCleaner()
        )
        self.deduplicator = (
            deduplicator
            if deduplicator is not None
            else DataDeduplicator()
        )
        self.data_filter = (
            data_filter
            if data_filter is not None
            else DataFilter()
        )
        self.normalizer = (
            normalizer
            if normalizer is not None
            else TextNormalizer()
        )
        self.balancer = balancer

    def process(
        self,
        records: list[CleanRecord],
        use_near_deduplication: bool = True,
        balance_group: str | None = None,
    ) -> ProcessingResult:
        """Process records without modifying the input list."""

        input_count = len(records)
        cleaned = self.cleaner.clean_many(list(records))
        cleaned_count = len(cleaned)
        deduplicated = self.deduplicator.deduplicate(
            cleaned,
            near=use_near_deduplication,
        )
        deduplicated_count = len(deduplicated)
        filtered = self.data_filter.filter(deduplicated)
        filtered_count = len(filtered)
        normalized = self.normalizer.normalize_many(filtered)
        normalized_count = len(normalized)
        balanced = normalized

        if (
            self.balancer is not None
            and balance_group is not None
        ):
            balanced = self.balancer.balance(normalized, balance_group)

        balanced_count = len(balanced)

        return ProcessingResult(
            records=balanced,
            input_count=input_count,
            cleaned_count=cleaned_count,
            deduplicated_count=deduplicated_count,
            filtered_count=filtered_count,
            normalized_count=normalized_count,
            balanced_count=balanced_count,
        )