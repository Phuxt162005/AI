from pathlib import Path

from database.management.backup import (
    BackupManager,
    RecoveryPolicy,
)


def test_backup_and_restore(tmp_path: Path):
    source = tmp_path / "source.txt"
    backup_root = tmp_path / "backup"
    restored = tmp_path / "restored.txt"

    source.write_text(
        "ProjectAI backup",
        encoding="utf-8",
    )

    manager = BackupManager(
        backup_root=backup_root,
        recovery_policy=RecoveryPolicy(
            rpo_seconds=3600,
            rto_seconds=7200,
        ),
    )

    record = manager.create_backup(
        source_path=source,
        backup_id="backup-001",
    )

    assert record.checksum
    assert record.size_bytes > 0

    manager.restore(record, restored)

    assert restored.read_text(
        encoding="utf-8"
    ) == "ProjectAI backup"


def test_recovery_policy():
    policy = RecoveryPolicy(
        rpo_seconds=300,
        rto_seconds=1800,
    )

    assert policy.rpo_seconds == 300
    assert policy.rto_seconds == 1800