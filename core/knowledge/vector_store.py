"""
Vector store abstraction and in-memory implementation.

The VectorStore defines the interface used by the Knowledge/RAG layer.
InMemoryVectorStore provides a dependency-free implementation for
development, testing, and local execution.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
import math
from typing import Any

from core.knowledge.entities import VectorRecord

@dataclass(frozen=True)
class VectorSearchResult:
    """A vector search result."""

    record: VectorRecord
    score: float

class VectorStore(ABC):
    """
    Abstract interface for vector storage.
    The interface intentionally does not depend on a specific vector
    database. A production implementation can later adapt this contract
    to a dedicated vector database.
    """

    @abstractmethod
    def upsert(self, record: VectorRecord) -> None:
        """Insert or replace a vector record."""

    @abstractmethod
    def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[VectorSearchResult]:
        """Search vectors by similarity."""

    @abstractmethod
    def delete(self, vector_id: str) -> None:
        """Delete a vector record by ID."""

class InMemoryVectorStore(VectorStore):
    """
    In-memory vector store using cosine similarity.
    This implementation is intentionally dependency-free and is suitable
    for unit tests and local development. It can later be replaced by a
    persistent vector database implementation without changing Retriever,
    KnowledgeIndexer, or RAGService.
    """

    def __init__(self) -> None:
        self._records: dict[str, VectorRecord] = {}

    def upsert(self, record: VectorRecord) -> None:
        """
        Insert a new vector record or replace an existing record.
        All vectors stored in this instance must have the same dimension.
        """

        if not isinstance(record, VectorRecord):
            raise TypeError("record must be a VectorRecord")

        if not record.vector:
            raise ValueError("record vector must not be empty")

        if self._records:
            existing_dimension = len(next(iter(self._records.values())).vector)

            if len(record.vector) != existing_dimension:
                raise ValueError("vector dimension must match existing records")
        self._records[record.vector_id] = record

    def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[VectorSearchResult]:
        """
        Search records using cosine similarity.
        Metadata filtering is performed before similarity ranking.
        """

        if not query_vector:
            raise ValueError("query_vector must not be empty")

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero")

        if self._records:
            existing_dimension = len(next(iter(self._records.values())).vector)

            if len(query_vector) != existing_dimension:
                raise ValueError("query vector dimension must match stored vectors")
        results: list[VectorSearchResult] = []

        for record in self._records.values():
            if not self._matches_metadata(record, metadata_filter):
                continue

            score = self._cosine_similarity(query_vector, record.vector)
            results.append(VectorSearchResult(record=record, score=score))

        results.sort(key=lambda result: result.score, reverse=True)

        return results[:top_k]

    def delete(self, vector_id: str) -> None:
        """Delete a vector record if it exists."""

        if not vector_id.strip():
            raise ValueError("vector_id must not be empty")

        self._records.pop(vector_id, None)

    @staticmethod
    def _matches_metadata(
        record: VectorRecord,
        metadata_filter: dict[str, Any] | None,
    ) -> bool:
        if not metadata_filter:
            return True

        return all(
            record.metadata.get(key) == value
            for key, value in metadata_filter.items()
        )

    @staticmethod
    def _cosine_similarity(
        first: list[float],
        second: list[float],
    ) -> float:
        if len(first) != len(second):
            raise ValueError("vectors must have the same dimension")

        dot_product = sum(left * right for left, right in zip(first, second))
        first_norm = math.sqrt(sum(value * value for value in first))
        second_norm = math.sqrt(sum(value * value for value in second))

        if first_norm == 0 or second_norm == 0:
            return 0.0

        return dot_product / (first_norm * second_norm)