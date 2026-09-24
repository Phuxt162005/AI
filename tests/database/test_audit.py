import pytest
from pathlib import Path

from database.audit.audit_log import (
    AuditLogger,
)


def test_audit_log_and_integrity(tmp_path: Path):
    path = tmp_path / "audit.jsonl"

    logger = AuditLogger(path)

    first = logger.record(
        event_id="event-1",
        actor_id="user-1",
        action="create",
        resource="dataset:1",
    )

    second = logger.record(
        event_id="event-2",
        actor_id="user-1",
        action="update",
        resource="dataset:1",
    )

    events = logger.read_events()

    assert len(events) == 2
    assert first.event_hash
    assert second.previous_hash == first.event_hash
    assert logger.verify_integrity()
    
def test_audit_detects_tampering(tmp_path: Path):
    path = tmp_path / "audit.jsonl"

    logger = AuditLogger(path)

    logger.record(
        event_id="event-1",
        actor_id="user-1",
        action="create",
        resource="dataset:1",
    )

    assert logger.verify_integrity()

    content = path.read_text(
        encoding="utf-8"
    )

    content = content.replace(
        '"action": "create"',
        '"action": "delete"',
    )

    path.write_text(
        content,
        encoding="utf-8",
    )

    assert not logger.verify_integrity()
    
     
def test_audit_requires_required_fields(
    tmp_path: Path,
):
    path = tmp_path / "audit.jsonl"
    logger = AuditLogger(path)

    with pytest.raises(ValueError):
        logger.record(
            event_id="",
            actor_id="user-1",
            action="create",
            resource="dataset:1",
        )