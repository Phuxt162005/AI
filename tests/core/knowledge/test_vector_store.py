from core.knowledge.entities import VectorRecord
from core.knowledge.vector_store import (
    InMemoryVectorStore,
)


def test_upsert_and_search():
    store = InMemoryVectorStore()

    store.upsert(
        VectorRecord(
            vector_id="1",
            chunk_id=1,
            vector=[1.0, 0.0],
            metadata={
                "document_id": 10,
            },
        )
    )

    store.upsert(
        VectorRecord(
            vector_id="2",
            chunk_id=2,
            vector=[0.0, 1.0],
            metadata={
                "document_id": 20,
            },
        )
    )

    results = store.search(
        query_vector=[1.0, 0.0],
        top_k=1,
    )

    assert len(results) == 1
    assert results[0].record.chunk_id == 1
    assert results[0].score > 0.99


def test_metadata_filter():
    store = InMemoryVectorStore()

    store.upsert(
        VectorRecord(
            vector_id="1",
            chunk_id=1,
            vector=[1.0, 0.0],
            metadata={
                "user_id": 10,
            },
        )
    )

    store.upsert(
        VectorRecord(
            vector_id="2",
            chunk_id=2,
            vector=[1.0, 0.0],
            metadata={
                "user_id": 20,
            },
        )
    )

    results = store.search(
        query_vector=[1.0, 0.0],
        metadata_filter={
            "user_id": 10,
        },
    )

    assert len(results) == 1
    assert results[0].record.chunk_id == 1


def test_delete():
    store = InMemoryVectorStore()

    store.upsert(
        VectorRecord(
            vector_id="1",
            chunk_id=1,
            vector=[1.0, 0.0],
        )
    )

    store.delete("1")

    results = store.search(
        query_vector=[1.0, 0.0],
    )

    assert results == []