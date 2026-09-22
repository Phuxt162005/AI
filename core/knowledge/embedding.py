"""Embedding interfaces."""

from __future__ import annotations

import math
import re
from abc import ABC, abstractmethod
from hashlib import sha256

class EmbeddingModel(ABC):
    """Interface for an embedding model."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return model name."""

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return vector dimension."""

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Convert text into an embedding vector."""

class SimpleEmbeddingModel(EmbeddingModel):
    """
    Deterministic local embedding implementation.
    This is a lightweight implementation for development/testing.
    It is not intended to replace a trained semantic embedding model.
    """

    def __init__(
        self,
        dimension: int = 64,
        model_name: str = "simple-hash-embedding",
    ) -> None:
        if dimension <= 0:
            raise ValueError("dimension must be greater than zero")

        self._dimension = dimension
        self._model_name = model_name

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed(self, text: str) -> list[float]:
        if not text.strip():
            raise ValueError("text must not be empty")

        tokens = re.findall(
            r"\w+",
            text.lower(),
            flags=re.UNICODE,
        )

        vector = [0.0] * self._dimension
        for token in tokens:
            digest = sha256(
                token.encode("utf-8")
            ).digest()

            for index in range(self._dimension):
                byte = digest[index % len(digest)]
                value = (byte / 127.5) - 1.0
                vector[index] += value

        norm = math.sqrt(sum(value * value for value in vector))

        if norm == 0:
            return vector

        return [value / norm for value in vector]