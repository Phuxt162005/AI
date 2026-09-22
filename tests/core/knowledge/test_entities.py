import pytest

from core.knowledge.entities import (
    Chunk,
    Document,
    DocumentVersion,
    DocumentStatus,
    Embedding,
    VectorRecord,
)


def test_document_creation():
    document = Document(
        document_id=1,
        title="AI Document",
        content_reference="documents/ai.txt",
        source_type="file",
    )

    assert document.document_id == 1
    assert document.title == "AI Document"
    assert document.status == DocumentStatus.ACTIVE


def test_document_version_creation():
    version = DocumentVersion(
        version_id=1,
        document_id=10,
        version_number=2,
        content_reference="documents/ai-v2.txt",
    )

    assert version.document_id == 10
    assert version.version_number == 2
    assert version.is_current is True


def test_chunk_creation():
    chunk = Chunk(
        chunk_id=1,
        document_id=10,
        content="AI is a field of computer science.",
        chunk_index=0,
    )

    assert chunk.document_id == 10
    assert chunk.chunk_index == 0


def test_embedding_dimension():
    embedding = Embedding(
        embedding_id=1,
        chunk_id=10,
        vector=[0.1, 0.2, 0.3],
        model_name="test-model",
        dimension=3,
    )

    assert embedding.dimension == 3


def test_invalid_embedding_dimension():
    with pytest.raises(ValueError):
        Embedding(
            embedding_id=1,
            chunk_id=10,
            vector=[0.1, 0.2],
            model_name="test-model",
            dimension=3,
        )


def test_vector_record():
    record = VectorRecord(
        vector_id="chunk:1",
        chunk_id=1,
        vector=[1.0, 0.0],
        metadata={
            "document_id": 10,
        },
    )

    assert record.vector_id == "chunk:1"
    assert record.chunk_id == 1