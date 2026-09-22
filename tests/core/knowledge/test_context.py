from core.knowledge.context import (
    ContextBuilder,
    ContextChunk,
)

def test_context_removes_duplicate_chunks():
    builder = ContextBuilder(
        max_chunks=5,
    )

    context = builder.build(
        [
            ContextChunk(
                chunk_id=1,
                content="First",
                score=0.8,
                metadata={},
            ),
            ContextChunk(
                chunk_id=1,
                content="First duplicate",
                score=0.6,
                metadata={},
            ),
            ContextChunk(
                chunk_id=2,
                content="Second",
                score=0.9,
                metadata={},
            ),
        ]
    )

    assert context == "Second\n\nFirst"


def test_context_orders_by_score():
    builder = ContextBuilder()

    context = builder.build(
        [
            ContextChunk(
                chunk_id=1,
                content="Low",
                score=0.2,
                metadata={},
            ),
            ContextChunk(
                chunk_id=2,
                content="High",
                score=0.9,
                metadata={},
            ),
        ]
    )

    assert context == "High\n\nLow"


def test_build_prompt():
    builder = ContextBuilder()

    prompt = builder.build_prompt(
        question="What is AI?",
        context="AI is a field of computer science.",
    )

    assert "What is AI?" in prompt
    assert "AI is a field" in prompt