from core.knowledge.embedding import (
    SimpleEmbeddingModel,
)
from core.knowledge.entities import VectorRecord
from core.knowledge.retriever import Retriever
from core.knowledge.vector_store import (
    InMemoryVectorStore,
)


def test_retriever():
    model = SimpleEmbeddingModel(
        dimension=16,
    )

    store = InMemoryVectorStore()

    vector = model.embed(
        "Python programming language"
    )

    store.upsert(
        VectorRecord(
            vector_id="1",
            chunk_id=1,
            vector=vector,
            metadata={
                "document_id": 10,
            },
        )
    )

    retriever = Retriever(
        embedding_model=model,
        vector_store=store,
    )

    results = retriever.retrieve(
        query="Python programming language",
        top_k=1,
    )

    assert len(results) == 1
    assert results[0].chunk_id == 1