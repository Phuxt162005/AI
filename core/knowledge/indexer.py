"""Knowledge indexing pipeline."""

from __future__ import annotations

from core.knowledge.embedding import EmbeddingModel
from core.knowledge.entities import Chunk, VectorRecord
from core.knowledge.vector_store import VectorStore

class KnowledgeIndexer:
    """Create embeddings and index document chunks."""

    def __init__(
        self,
        embedding_model: EmbeddingModel,
        vector_store: VectorStore,
    ) -> None:
        self.embedding_model = embedding_model
        self.vector_store = vector_store

    def index_chunk(self, chunk: Chunk) -> VectorRecord:
        vector = self.embedding_model.embed(chunk.content)
        vector_id = (
            f"chunk:{chunk.chunk_id}"
            if chunk.chunk_id is not None
            else (
                f"document:{chunk.document_id}:"
                f"chunk:{chunk.chunk_index}"
            )
        )
        metadata = {
            "document_id": chunk.document_id,
            "chunk_id": chunk.chunk_id,
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
        }
        metadata.update(chunk.metadata)
        record = VectorRecord(
            vector_id=vector_id,
            chunk_id=chunk.chunk_id or chunk.chunk_index + 1,
            vector=vector,
            metadata=metadata,
        )
        self.vector_store.upsert(record)

        return record

    def index(self, chunks: list[Chunk]) -> list[VectorRecord]:
        return [
            self.index_chunk(chunk)
            for chunk in chunks
        ]