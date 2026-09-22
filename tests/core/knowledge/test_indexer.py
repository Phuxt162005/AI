from core.knowledge.embedding import (
    SimpleEmbeddingModel,
)
from core.knowledge.entities import Chunk
from core.knowledge.indexer import KnowledgeIndexer
from core.knowledge.vector_store import (
    InMemoryVectorStore,
)


def test_index_chunk():
    model = SimpleEmbeddingModel(
        dimension=8,
    )

    store = InMemoryVectorStore()

    indexer = KnowledgeIndexer(
        embedding_model=model,
        vector_store=store,
    )

    chunk = Chunk(
        chunk_id=1,
        document_id=10,
        content="Knowledge chunk.",
        chunk_index=0,
        metadata={
            "source": "test",
        },
    )

    record = indexer.index_chunk(chunk)

    assert record.chunk_id == 1
    assert record.metadata["document_id"] == 10
    assert record.metadata["source"] == "test"

    results = store.search(
        query_vector=model.embed(
            "Knowledge chunk."
        ),
        top_k=1,
    )

    assert len(results) == 1
    assert results[0].record.chunk_id == 1