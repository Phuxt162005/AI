"""Raw data collection utilities."""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

from data.collection.collection_record import (
    CollectionMethod,
    CollectionRecord,
)
from data.sources.source import DataSource

class RawDataCollector:
    """Collect data into Raw Data storage without transformation."""

    def __init__(self, raw_root: str | Path) -> None:
        self.raw_root = Path(raw_root)
        self.raw_root.mkdir(parents=True, exist_ok=True)

    def collect_file(
        self,
        source: DataSource,
        file_path: str | Path,
        collection_id: str,
        dataset_name: str | None = None,
        dataset_version: str = "1.0.0",
        batch_id: str | None = None,
    ) -> CollectionRecord:
        """Copy a file into Raw Data storage without modifying it."""

        source_path = Path(file_path)

        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")

        if not source_path.is_file():
            raise ValueError(f"Source path is not a file: {source_path}")

        destination = self._build_destination(source_path, collection_id)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination)
        size_bytes = destination.stat().st_size
        checksum = self._calculate_checksum(destination)
        record = CollectionRecord(
            collection_id=collection_id,
            source_id=source.source_id,
            collection_method=CollectionMethod.DATASET_IMPORT,
            raw_path=str(destination),
            dataset_name=dataset_name,
            dataset_version=dataset_version,
            batch_id=batch_id,
            format=source_path.suffix.lstrip(".") or None,
            size_bytes=size_bytes,
            attributes={
                "original_filename": source_path.name,
                "checksum_sha256": checksum,
                "source_type": source.source_type.value,
            },
        )
        return record

    def _build_destination(
        self,
        source_path: Path,
        collection_id: str,
    ) -> Path:
        """Build a deterministic Raw Data destination."""

        filename = (f"{collection_id}_{source_path.name}")

        return self.raw_root / filename

    @staticmethod
    def _calculate_checksum(path: Path) -> str:
        """Calculate SHA-256 checksum without changing the file."""

        digest = hashlib.sha256()

        with path.open("rb") as file:
            for chunk in iter(lambda: file.read(1024 * 1024), b""):
                digest.update(chunk)

        return digest.hexdigest()