"""Data deduplication utilities."""

from __future__ import annotations

from difflib import SequenceMatcher

from data.processing.cleaner import CleanRecord

class DataDeduplicator:
    """Remove exact and near-duplicate records."""

    def __init__(self, similarity_threshold: float = 0.90) -> None:
        if not 0.0 < similarity_threshold <= 1.0:
            raise ValueError(
                "similarity_threshold must be between "
                "0 and 1"
            )

        self.similarity_threshold = similarity_threshold

    @staticmethod
    def _normalized_content(content: str) -> str:
        """Create a comparison representation."""

        return " ".join(content.casefold().split())

    def exact_deduplicate(self, records: list[CleanRecord]) -> list[CleanRecord]:
        """Remove records with exactly equal normalized content."""

        seen: set[str] = set()
        result: list[CleanRecord] = []

        for record in records:
            key = self._normalized_content(record.content)

            if key in seen:
                continue

            seen.add(key)
            result.append(record)

        return result

    def near_deduplicate(self, records: list[CleanRecord]) -> list[CleanRecord]:
        """Remove records very similar to an earlier record."""

        result: list[CleanRecord] = []

        for record in records:
            duplicate = False
            current = self._normalized_content(record.content)

            for existing in result:
                previous = self._normalized_content(existing.content)
                similarity = SequenceMatcher(
                    None,
                    current,
                    previous,
                ).ratio()

                if (similarity >= self.similarity_threshold):
                    duplicate = True
                    break

            if not duplicate:
                result.append(record)

        return result

    def deduplicate(
        self,
        records: list[CleanRecord],
        near: bool = True,
    ) -> list[CleanRecord]:
        """Apply exact and optionally near deduplication."""

        result = self.exact_deduplicate(records)
        if near:
            result = self.near_deduplicate(result)
        return result