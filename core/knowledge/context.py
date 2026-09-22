"""Context construction for RAG."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from core.knowledge.retriever import RetrievedChunk

@dataclass(frozen=True)
class ContextChunk:
    """Retrieved chunk with its source text."""

    chunk_id: int
    content: str
    score: float
    metadata: dict

class ContextBuilder:
    """
    Build the context sent to the generation layer.
    The construction process follows:
    deduplicate -> sort by relevance -> select -> concatenate.
    """

    def __init__(self, max_chunks: int = 5) -> None:
        if max_chunks <= 0:
            raise ValueError("max_chunks must be greater than zero")

        self.max_chunks = max_chunks

    def build(self, chunks: Iterable[ContextChunk]) -> str:
        unique: dict[int, ContextChunk] = {}

        for chunk in chunks:
            existing = unique.get(chunk.chunk_id)

            if existing is None or chunk.score > existing.score:
                unique[chunk.chunk_id] = chunk

        ordered = sorted(
            unique.values(),
            key=lambda item: item.score,
            reverse=True,
        )
        selected = ordered[:self.max_chunks]

        return "\n\n".join(
            chunk.content
            for chunk in selected
            if chunk.content.strip()
        )

    def build_prompt(
        self,
        question: str,
        context: str,
    ) -> str:
        if not question.strip():
            raise ValueError("question must not be empty")

        return (
            "Context:\n"
            f"{context}\n\n"
            "Question:\n"
            f"{question}"
        )