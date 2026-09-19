from data.processing.chunker import (
    TextChunker,
)
from data.processing.cleaner import CleanRecord


def test_chunker():
    record = CleanRecord(
        "record_001",
        "one two three four five six",
    )

    chunks = TextChunker(
        chunk_size=2
    ).chunk(record)

    assert len(chunks) == 3

    assert chunks[0].content == "one two"
    assert chunks[1].content == "three four"
    assert chunks[2].content == "five six"


def test_chunker_with_overlap():
    record = CleanRecord(
        "record_002",
        "one two three four five",
    )

    chunks = TextChunker(
        chunk_size=3,
        overlap=1,
    ).chunk(record)

    assert chunks[0].content == (
        "one two three"
    )

    assert chunks[1].content == (
        "three four five"
    )


def test_chunk_ids_are_unique():
    record = CleanRecord(
        "record_003",
        "one two three four",
    )

    chunks = TextChunker(
        chunk_size=2
    ).chunk(record)

    assert len({
        chunk.chunk_id
        for chunk in chunks
    }) == len(chunks)