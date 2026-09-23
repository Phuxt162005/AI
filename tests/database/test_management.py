from datetime import datetime, timedelta, timezone

from database.management.retention import (
    RetentionManager,
    RetentionPolicy,
)
from database.management.versioning import (
    VersionManager,
)

def test_version_manager_creates_incremental_versions():
    manager = VersionManager()

    first = manager.create_version(
        object_id="dataset-1",
        checksum="abc",
    )
    second = manager.create_version(
        object_id="dataset-1",
        checksum="def",
    )

    assert first.version == 1
    assert second.version == 2
    assert manager.current("dataset-1") == second
    assert len(manager.history("dataset-1")) == 2


def test_retention_manager_detects_expired_data():
    manager = RetentionManager(
        RetentionPolicy(
            retention_days=7,
            allow_deletion=True,
        )
    )
    old = datetime.now(timezone.utc) - timedelta(days=8)
    assert manager.is_expired(old)