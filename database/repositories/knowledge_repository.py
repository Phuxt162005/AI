"""Repositories for Knowledge entities."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from core.knowledge.entities import (
    Chunk,
    Document,
    DocumentStatus,
    DocumentVersion,
)
from database.access.data_access import DataAccess
from database.access.repository import (
    BaseRepository,
    EntityMapper,
)

def _document_from_row(row: Any) -> Document:
    return Document(
        document_id=row.get("document_id"),
        title=row["title"],
        content_reference=row["content_reference"],
        source_type=row["source_type"],
        language=row.get("language", "vi"),
        version=row.get("version", 1),
        status=DocumentStatus(
            row.get("status", "active")
        ),
        created_at=row.get("created_at"),
        updated_at=row.get("updated_at"),
    )

def _document_to_row(entity: Document) -> dict[str, Any]:
    row = {
        "title": entity.title,
        "content_reference": entity.content_reference,
        "source_type": entity.source_type,
        "language": entity.language,
        "version": entity.version,
        "status": entity.status.value,
    }

    if entity.document_id is not None:
        row["document_id"] = entity.document_id

    return row

class DocumentRepository(BaseRepository[Document]):
    """Repository for Knowledge documents."""

    def __init__(self, data_access: DataAccess) -> None:
        mapper = EntityMapper[Document](
            from_row=_document_from_row,
            to_row=_document_to_row,
        )

        super().__init__(
            data_access=data_access,
            table_name="documents",
            mapper=mapper,
            primary_key="document_id",
        )

    def list_active(self) -> list[Document]:
        sql = (
            "SELECT * FROM `documents` "
            "WHERE `status` = %s "
            "ORDER BY `updated_at` DESC"
        )
        rows = self.data_access.query(
            sql,
            [DocumentStatus.ACTIVE.value],
        )

        return [
            self.mapper.map_from_row(row)
            for row in rows
        ]

def _version_from_row(row: Any) -> DocumentVersion:
    return DocumentVersion(
        version_id=row.get("version_id"),
        document_id=row["document_id"],
        version_number=row["version_number"],
        content_reference=row["content_reference"],
        created_at=row.get("created_at"),
        is_current=bool(row.get("is_current", True)),
    )


def _version_to_row(entity: DocumentVersion) -> dict[str, Any]:
    row = {
        "document_id": entity.document_id,
        "version_number": entity.version_number,
        "content_reference": entity.content_reference,
        "is_current": entity.is_current,
    }

    if entity.version_id is not None:
        row["version_id"] = entity.version_id

    return row


class DocumentVersionRepository(BaseRepository[DocumentVersion]):
    """Repository for document versions."""

    def __init__(self, data_access: DataAccess) -> None:
        mapper = EntityMapper[DocumentVersion](
            from_row=_version_from_row,
            to_row=_version_to_row,
        )

        super().__init__(
            data_access=data_access,
            table_name="document_versions",
            mapper=mapper,
            primary_key="version_id",
        )

    def list_by_document(self, document_id: int) -> list[DocumentVersion]:
        sql = (
            "SELECT * FROM `document_versions` "
            "WHERE `document_id` = %s "
            "ORDER BY `version_number` DESC"
        )

        rows = self.data_access.query(sql, [document_id])

        return [
            self.mapper.map_from_row(row)
            for row in rows
        ]

def _chunk_from_row(row: Any) -> Chunk:
    return Chunk(
        chunk_id=row.get("chunk_id"),
        document_id=row["document_id"],
        content=row["content"],
        chunk_index=row["chunk_index"],
        version_id=row.get("version_id"),
        metadata=row.get("metadata", {}),
    )

def _chunk_to_row(entity: Chunk) -> dict[str, Any]:
    row = {
        "document_id": entity.document_id,
        "content": entity.content,
        "chunk_index": entity.chunk_index,
        "version_id": entity.version_id,
    }

    if entity.metadata:
        row["metadata"] = entity.metadata

    if entity.chunk_id is not None:
        row["chunk_id"] = entity.chunk_id

    return row

class ChunkRepository(BaseRepository[Chunk]):
    """Repository for document chunks."""

    def __init__(self, data_access: DataAccess) -> None:
        mapper = EntityMapper[Chunk](
            from_row=_chunk_from_row,
            to_row=_chunk_to_row,
        )

        super().__init__(
            data_access=data_access,
            table_name="chunks",
            mapper=mapper,
            primary_key="chunk_id",
        )

    def list_by_document(self, document_id: int) -> list[Chunk]:
        sql = (
            "SELECT * FROM `chunks` "
            "WHERE `document_id` = %s "
            "ORDER BY `chunk_index` ASC"
        )

        rows = self.data_access.query(sql, [document_id])

        return [
            self.mapper.map_from_row(row)
            for row in rows
        ]