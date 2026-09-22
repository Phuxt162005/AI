"""Knowledge retrieval."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.knowledge.embedding import EmbeddingModel
from core.knowledge.vector_store import (
    VectorSearchResult,
    VectorStore,
)

@dataclass(frozen=True)
class RetrievedChunk:
    """Chunk returned by retrieval."""

    chunk_id: int
    score: float
    metadata: dict[str, Any]

class Retriever:
    """
    Retrieve relevant chunks from the Vector Store.
    Authorization filters are passed into the Vector Store before
    results are returned.
    """

    def __init__(
        self,
        embedding_model: EmbeddingModel,
        vector_store: VectorStore,
    ) -> None:
        self.embedding_model = embedding_model
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[RetrievedChunk]:
        if not query.strip():
            raise ValueError("query must not be empty")

        query_vector = self.embedding_model.embed(query)

        results = self.vector_store.search(
            query_vector=query_vector,
            top_k=top_k,
            metadata_filter=metadata_filter,
        )

        return [
            self._to_retrieved_chunk(result)
            for result in results
        ]

    @staticmethod
    def _to_retrieved_chunk(result: VectorSearchResult) -> RetrievedChunk:
        return RetrievedChunk(
            chunk_id=result.record.chunk_id,
            score=result.score,
            metadata=result.record.metadata,
        )