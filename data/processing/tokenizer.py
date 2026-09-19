"""Tokenization utilities for training data."""

from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class Token:
    """A token and its deterministic token ID."""

    text: str
    token_id: int

class SimpleTokenizer:
    """
    A lightweight tokenizer based on whitespace.
    This is a replaceable tokenizer abstraction for the data pipeline.
    It does not implement a production LLM tokenizer.
    """
    
    UNK_TOKEN = "<UNK>"
    PAD_TOKEN = "<PAD>"

    def __init__(self, vocabulary: dict[str, int] | None = None) -> None:
        self.vocabulary: dict[str, int] = {
            self.PAD_TOKEN: 0,
            self.UNK_TOKEN: 1,
        }

        if vocabulary is not None:
            for token, token_id in vocabulary.items():
                self._validate_token_id(token_id)
                self.vocabulary[token] = token_id
        self._next_id = max(self.vocabulary.values()) + 1

    @staticmethod
    def _validate_token_id(token_id: int) -> None:
        if not isinstance(token_id, int):
            raise TypeError("token_id must be an integer")

        if token_id < 0:
            raise ValueError("token_id must not be negative")

    def build_vocabulary(self, texts: list[str]) -> dict[str, int]:
        """Build vocabulary from a collection of texts."""

        for text in texts:
            for token in text.split():
                if token not in self.vocabulary:
                    self.vocabulary[token] = self._next_id
                    self._next_id += 1

        return dict(self.vocabulary)

    def tokenize(self, text: str) -> list[str]:
        """Split text into tokens."""

        if not isinstance(text, str):
            raise TypeError("text must be a string")

        return text.split()

    def encode(self, text: str) -> list[int]:
        """Convert text into token IDs."""

        tokens = self.tokenize(text)

        return [
            self.vocabulary.get(token, self.vocabulary[self.UNK_TOKEN])
            for token in tokens
        ]

    def tokenize_with_ids(self, text: str) -> list[Token]:
        """Return tokens together with their token IDs."""

        tokens = self.tokenize(text)
        return [
            Token(
                text=token,
                token_id=self.vocabulary.get(
                    token,
                    self.vocabulary[self.UNK_TOKEN],
                ),
            )
            for token in tokens
        ]

    def decode(self, token_ids: list[int]) -> str:
        """Convert token IDs back into text."""

        reverse_vocabulary = {
            token_id: token
            for token, token_id in self.vocabulary.items()
        }

        return " ".join(
            reverse_vocabulary.get(token_id, self.UNK_TOKEN)
            for token_id in token_ids
        )