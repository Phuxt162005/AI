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