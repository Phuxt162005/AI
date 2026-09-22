"""Knowledge domain entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

class DocumentStatus(str, Enum):
    """Document lifecycle status."""

    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"

@dataclass
class Document:
    """
    Knowledge document.
    The model keeps the document reference and lifecycle information
    required by the Knowledge Database design.
    """

    document_id: int | None
    title: str
    content_reference: str
    source_type: str
    language: str = "vi"
    version: int = 1
    status: DocumentStatus = DocumentStatus.ACTIVE
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("title must not be empty")

        if not self.content_reference.strip():
            raise ValueError("content_reference must not be empty")

        if not self.source_type.strip():
            raise ValueError("source_type must not be empty")

        if self.version <= 0:
            raise ValueError("version must be greater than zero")

        if not isinstance(self.status, DocumentStatus):
            self.status = DocumentStatus(self.status)

@dataclass
class DocumentVersion:
    """Version of a Knowledge document."""

    version_id: int | None
    document_id: int
    version_number: int
    content_reference: str
    created_at: datetime | None = None
    is_current: bool = True

    def __post_init__(self) -> None:
        if self.document_id <= 0:
            raise ValueError("document_id must be greater than zero")

        if self.version_number <= 0:
            raise ValueError("version_number must be greater than zero")

        if not self.content_reference.strip():
            raise ValueError("content_reference must not be empty")

@dataclass
class Chunk:
    """
    A document chunk.
    Document -> Chunk is a one-to-many relationship.
    """

    chunk_id: int | None
    document_id: int
    content: str
    chunk_index: int
    version_id: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.document_id <= 0:
            raise ValueError("document_id must be greater than zero")

        if not self.content.strip():
            raise ValueError("content must not be empty")

        if self.chunk_index < 0:
            raise ValueError("chunk_index must not be negative")

@dataclass
class Embedding:
    """Embedding generated from a Chunk."""

    embedding_id: int | None
    chunk_id: int
    vector: list[float]
    model_name: str
    dimension: int

    def __post_init__(self) -> None:
        if self.chunk_id <= 0:
            raise ValueError("chunk_id must be greater than zero")

        if not self.model_name.strip():
            raise ValueError("model_name must not be empty")

        if self.dimension <= 0:
            raise ValueError("dimension must be greater than zero")

        if len(self.vector) != self.dimension:
            raise ValueError("vector length must match dimension")

@dataclass
class VectorRecord:
    """
    Vector Database record.
    A VectorRecord connects an embedding with its searchable metadata.
    """

    vector_id: str
    chunk_id: int
    vector: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.vector_id.strip():
            raise ValueError("vector_id must not be empty")

        if self.chunk_id <= 0:
            raise ValueError("chunk_id must be greater than zero")

        if not self.vector:
            raise ValueError("vector must not be empty")