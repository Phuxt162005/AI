"""Backup and recovery utilities."""

from __future__ import annotations

import hashlib
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

@dataclass(frozen=True)
class RecoveryPolicy:
    """Define Recovery Point Objective and Recovery Time Objective."""

    rpo_seconds: int
    rto_seconds: int

    def __post_init__(self) -> None:
        if self.rpo_seconds < 0:
            raise ValueError("rpo_seconds must be >= 0")

        if self.rto_seconds < 0:
            raise ValueError("rto_seconds must be >= 0")

@dataclass(frozen=True)
class BackupRecord:
    """Metadata describing a backup artifact."""

    backup_id: str
    source_path: str
    backup_path: str
    checksum: str
    created_at: datetime
    size_bytes: int

class BackupManager:
    """Create and restore file-based backups."""

    def __init__(
        self,
        backup_root: str | Path,
        recovery_policy: RecoveryPolicy,
    ) -> None:
        self.backup_root = Path(backup_root)
        self.backup_root.mkdir(parents=True, exist_ok=True)
        self.recovery_policy = recovery_policy

    def create_backup(
        self,
        source_path: str | Path,
        backup_id: str,
    ) -> BackupRecord:
        """Create a backup without modifying the source."""

        source = Path(source_path)

        if not source.exists():
            raise FileNotFoundError(source)

        if not source.is_file():
            raise ValueError("source_path must point to a file")

        destination = self.backup_root / backup_id / source.name
        destination.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(source, destination)

        checksum = self._checksum(destination)

        return BackupRecord(
            backup_id=backup_id,
            source_path=str(source),
            backup_path=str(destination),
            checksum=checksum,
            created_at=datetime.now(timezone.utc),
            size_bytes=destination.stat().st_size,
        )

    def restore(
        self,
        record: BackupRecord,
        destination_path: str | Path,
    ) -> Path:
        """Restore a verified backup."""

        backup = Path(record.backup_path)
        if not backup.exists():
            raise FileNotFoundError(backup)

        actual_checksum = self._checksum(backup)
        if actual_checksum != record.checksum:
            raise ValueError("Backup checksum verification failed")

        destination = Path(destination_path)
        destination.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(backup, destination)

        return destination

    @staticmethod
    def _checksum(path: Path) -> str:
        digest = hashlib.sha256()

        with path.open("rb") as file:
            for chunk in iter(
                lambda: file.read(1024 * 1024),
                b"",
            ):
                digest.update(chunk)

        return digest.hexdigest()