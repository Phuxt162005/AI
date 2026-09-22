from core.knowledge.context import (
    ContextBuilder,
    ContextChunk,
)
from core.knowledge.embedding import (
    SimpleEmbeddingModel,
)
from core.knowledge.entities import VectorRecord
from core.knowledge.rag import RAGService
from core.knowledge.retriever import Retriever
from core.knowledge.vector_store import (
    InMemoryVectorStore,
)


def test_rag_pipeline():
    model = SimpleEmbeddingModel(
        dimension=16,
    )

    store = InMemoryVectorStore()

    vector = model.embed(
        "Artificial intelligence is a field of computer science."
    )

    store.upsert(
        VectorRecord(
            vector_id="1",
            chunk_id=1,
            vector=vector,
            metadata={
                "content":
                    "Artificial intelligence is a field "
                    "of computer science.",
            },
        )
    )

    retriever = Retriever(
        embedding_model=model,
        vector_store=store,
    )

    builder = ContextBuilder()

    service = RAGService(
        retriever=retriever,
        context_builder=builder,
    )

    results = service.retrieve(
        "What is artificial intelligence?",
        top_k=1,
    )

    chunks = [
        ContextChunk(
            chunk_id=result.chunk_id,
            content=result.metadata["content"],
            score=result.score,
            metadata=result.metadata,
        )
        for result in results
    ]

    prompt = service.generate(
        question="What is artificial intelligence?",
        chunks=chunks,
    )

    assert "Artificial intelligence" in prompt
    assert "What is artificial intelligence?" in prompt