from core.knowledge.embedding import (
    SimpleEmbeddingModel,
)


def test_embedding_dimension():
    model = SimpleEmbeddingModel(
        dimension=8,
    )

    vector = model.embed(
        "Knowledge retrieval test."
    )

    assert len(vector) == 8


def test_embedding_is_deterministic():
    model = SimpleEmbeddingModel(
        dimension=8,
    )

    first = model.embed("hello world")
    second = model.embed("hello world")

    assert first == second


def test_embedding_normalized():
    model = SimpleEmbeddingModel(
        dimension=8,
    )

    vector = model.embed("hello world")

    length = sum(
        value * value
        for value in vector
    ) ** 0.5

    assert abs(length - 1.0) < 1e-6