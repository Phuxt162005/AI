"""RAG pipeline."""

from __future__ import annotations

from collections.abc import Callable

from core.knowledge.context import (
    ContextBuilder,
    ContextChunk,
)
from core.knowledge.retriever import Retriever

class RAGService:
    """
    Retrieval-Augmented Generation service.
    The generation layer is injected so the Knowledge/RAG layer does not
    depend directly on a specific LLM.
    """

    def __init__(
        self,
        retriever: Retriever,
        context_builder: ContextBuilder,
        generator: Callable[[str], str] | None = None,
    ) -> None:
        self.retriever = retriever
        self.context_builder = context_builder
        self.generator = generator

    def retrieve(
        self,
        question: str,
        top_k: int = 5,
        metadata_filter: dict | None = None,
    ):
        return self.retriever.retrieve(
            query=question,
            top_k=top_k,
            metadata_filter=metadata_filter,
        )

    def build_context(
        self,
        question: str,
        chunks: list[ContextChunk],
    ) -> str:
        context = self.context_builder.build(chunks)

        return self.context_builder.build_prompt(
            question=question,
            context=context,
        )

    def generate(
        self,
        question: str,
        chunks: list[ContextChunk],
    ) -> str:
        prompt = self.build_context(question=question, chunks=chunks)
        if self.generator is None:
            return prompt
        return self.generator(prompt)

    def answer(
        self,
        question: str,
        top_k: int = 5,
        metadata_filter: dict | None = None,
    ) -> str:
        retrieved = self.retrieve(
            question=question,
            top_k=top_k,
            metadata_filter=metadata_filter,
        )
        chunks = [
            ContextChunk(
                chunk_id=item.chunk_id,
                content=str(item.metadata.get("content", "")),
                score=item.score,
                metadata=item.metadata,
            )
            for item in retrieved
        ]

        return self.generate(question=question, chunks=chunks)