"""Text chunking utilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from data.processing.cleaner import CleanRecord

@dataclass
class TextChunk:
    """A chunk produced from a source record."""

    chunk_id: str
    record_id: str
    content: str
    chunk_index: int
    start_token: int
    end_token: int
    attributes: dict[str, Any] = field(default_factory=dict)


class TextChunker:
    """Split text records into fixed-size token chunks."""

    def __init__(
        self,
        chunk_size: int = 128,
        overlap: int = 0,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")

        if overlap < 0:
            raise ValueError("overlap must not be negative")

        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")

        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, record: CleanRecord) -> list[TextChunk]:
        """Split a record into chunks."""

        tokens = record.content.split()

        if not tokens:
            return []

        step = self.chunk_size - self.overlap
        chunks: list[TextChunk] = []
        start = 0
        index = 0
        while start < len(tokens):
            end = min(start + self.chunk_size, len(tokens))
            content = " ".join(tokens[start:end])
            attributes = dict(record.attributes)
            attributes["chunked"] = True

            chunks.append(
                TextChunk(
                    chunk_id=(f"{record.record_id}" f":chunk:{index}"),
                    record_id=record.record_id,
                    content=content,
                    chunk_index=index,
                    start_token=start,
                    end_token=end,
                    attributes=attributes,
                )
            )

            if end == len(tokens):
                break
            start += step
            index += 1

        return chunks

    def chunk_many(self, records: list[CleanRecord]) -> list[TextChunk]:
        """Chunk multiple records."""

        result: list[TextChunk] = []
        for record in records:
            result.extend(self.chunk(record))

        return result