"""Initial validation for collected raw data."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from data.collection.collection_record import CollectionRecord
from data.metadata.metadata import MetadataManager
from data.sources.source import DataSource

@dataclass
class ValidationResult:
    """Result of an initial input validation."""

    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        """Add a validation error."""

        self.errors.append(message)
        self.valid = False

    def add_warning(self, message: str) -> None:
        """Add a validation warning."""

        self.warnings.append(message)

class InputValidator:
    """Perform initial validation before data processing."""

    def validate(
        self,
        collection: CollectionRecord,
        source: DataSource | None = None,
        metadata_manager: MetadataManager | None = None,
        metadata_id: str | None = None,
    ) -> ValidationResult:
        """Validate a collected raw-data record."""

        result = ValidationResult(valid=True)
        self._validate_collection(collection, result)
        self._validate_raw_file(collection, result)
        self._validate_source(source, result)
        self._validate_metadata(
            metadata_manager,
            metadata_id,
            result,
        )

        if result.valid:
            collection.mark_validated()

        return result

    @staticmethod
    def _validate_collection(
        collection: CollectionRecord,
        result: ValidationResult,
    ) -> None:
        """Validate required collection information."""

        if not collection.collection_id.strip():
            result.add_error("collection_id is missing")

        if not collection.source_id.strip():
            result.add_error("source_id is missing")

        if not collection.raw_path.strip():
            result.add_error("raw_path is missing")

    @staticmethod
    def _validate_raw_file(
        collection: CollectionRecord,
        result: ValidationResult,
    ) -> None:
        """Check whether the Raw Data file can be read."""

        path = Path(collection.raw_path)

        if not path.exists():
            result.add_error(f"Raw data does not exist: {path}")
            return

        if not path.is_file():
            result.add_error(f"Raw data path is not a file: {path}")
            return

        try:
            with path.open("rb") as file:
                file.read(1)
        except OSError as exc:
            result.add_error(f"Raw data cannot be read: {exc}")
            return

        actual_size = path.stat().st_size

        if actual_size == 0:
            result.add_warning("Raw data file is empty")

        if (
            collection.size_bytes is not None
            and actual_size != collection.size_bytes
        ):
            result.add_error(
                "Raw data size does not match "
                "collection metadata"
            )

    @staticmethod
    def _validate_source(
        source: DataSource | None,
        result: ValidationResult,
    ) -> None:
        """Check whether source information is available."""

        if source is None:
            result.add_error("Source information is missing")
            return

        if not source.source_id.strip():
            result.add_error("Source ID is missing")

        if not source.name.strip():
            result.add_error("Source name is missing")

    @staticmethod
    def _validate_metadata(
        metadata_manager: MetadataManager | None,
        metadata_id: str | None,
        result: ValidationResult,
    ) -> None:
        """Check whether required metadata is available."""

        if metadata_manager is None:
            result.add_error("Metadata manager is missing")
            return

        if metadata_id is None or not metadata_id.strip():
            result.add_error("Metadata ID is missing")
            return
        metadata = metadata_manager.get(metadata_id)

        if metadata is None:
            result.add_error(f"Metadata not found: {metadata_id}")