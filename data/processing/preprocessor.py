"""Dataset preprocessing utilities for ProjectAI."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from data.processing.chunker import (TextChunk, TextChunker)
from data.processing.cleaner import (CleanRecord)
from data.processing.formatter import (DataFormatter, FormattedRecord)
from data.processing.normalizer import (TextNormalizer)
from data.processing.tokenizer import (SimpleTokenizer)

@dataclass
class PreprocessedRecord:
    """A record after preprocessing."""

    record_id: str
    input: str
    output: str | None = None
    tokens: list[str] = field(default_factory=list)
    token_ids: list[int] = field(default_factory=list)
    labels: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def token_count(self) -> int:
        """Return the number of tokens."""

        return len(self.tokens)

@dataclass
class PreprocessingResult:
    """Result of a preprocessing run."""

    records: list[PreprocessedRecord]
    input_count: int
    output_count: int
    chunk_count: int = 0

class DataPreprocessor:
    """Prepare cleaned records for training."""

    SUPPORTED_TYPES = {
        "pre_training",
        "instruction",
        "conversation",
        "personality",
        "emotion",
        "multimodal",
        "preference",
    }

    def __init__(
        self,
        tokenizer: SimpleTokenizer | None = None,
        normalizer: TextNormalizer | None = None,
        formatter: DataFormatter | None = None,
        chunker: TextChunker | None = None,
    ) -> None:
        self.tokenizer = (
            tokenizer
            if tokenizer is not None
            else SimpleTokenizer()
        )
        self.normalizer = (
            normalizer
            if normalizer is not None
            else TextNormalizer()
        )
        self.formatter = (
            formatter
            if formatter is not None
            else DataFormatter()
        )
        self.chunker = chunker

    def preprocess(
        self,
        records: list[CleanRecord],
        dataset_type: str,
        *,
        build_vocabulary: bool = False,
        chunk: bool = False,
    ) -> PreprocessingResult:
        """Preprocess cleaned records."""

        if dataset_type not in self.SUPPORTED_TYPES:
            raise ValueError(
                f"Unsupported dataset type: "
                f"{dataset_type}"
            )

        normalized = self.normalizer.normalize_many(list(records))
        formatted = self.formatter.format_many(normalized)

        if build_vocabulary:
            texts = self._build_vocabulary_texts(formatted)
            self.tokenizer.build_vocabulary(texts)

        if chunk:
            return self._preprocess_with_chunks(normalized, dataset_type)

        result: list[PreprocessedRecord] = []

        for record in formatted:
            result.append(self._preprocess_record(record))

        return PreprocessingResult(
            records=result,
            input_count=len(records),
            output_count=len(result),
        )

    def _preprocess_record(self, record: FormattedRecord) -> PreprocessedRecord:
        """Convert one formatted record."""

        tokens = self.tokenizer.tokenize(record.input)
        token_ids = self.tokenizer.encode(record.input)
        metadata = dict(record.metadata)
        metadata["preprocessed"] = True
        metadata["token_count"] = len(tokens)

        return PreprocessedRecord(
            record_id=record.record_id,
            input=record.input,
            output=record.output,
            tokens=tokens,
            token_ids=token_ids,
            labels=dict(record.labels),
            metadata=metadata,
        )

    def _preprocess_with_chunks(
        self,
        records: list[CleanRecord],
        dataset_type: str,
    ) -> PreprocessingResult:
        """Preprocess records after text chunking."""

        if self.chunker is None:
            raise ValueError(
                "A TextChunker is required "
                "when chunk=True"
            )

        chunks = self.chunker.chunk_many(records)
        result: list[PreprocessedRecord] = []

        for chunk in chunks:
            formatted = FormattedRecord(
                record_id=chunk.chunk_id,
                input=chunk.content,
                metadata={
                    "dataset_type": dataset_type,
                    "source_record_id": (chunk.record_id),
                    "chunk_index": (chunk.chunk_index),
                    "start_token": (chunk.start_token),
                    "end_token": (chunk.end_token),
                    **dict(chunk.attributes),
                },
            )

            result.append(self._preprocess_record(formatted))

        return PreprocessingResult(
            records=result,
            input_count=len(records),
            output_count=len(result),
            chunk_count=len(chunks),
        )

    @staticmethod
    def _build_vocabulary_texts(records: list[FormattedRecord]) -> list[str]:
        """Collect text used for vocabulary construction."""

        texts: list[str] = []
        for record in records:
            texts.append(record.input)
            if record.output:
                texts.append(record.output)
        return texts