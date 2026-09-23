"""Append-only audit log."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class AuditEvent:
    """Represent one auditable system event."""

    event_id: str
    actor_id: str
    action: str
    resource: str
    timestamp: str
    details: dict[str, Any]
    previous_hash: str = ""
    event_hash: str = ""


class AuditLogger:
    """Write audit events to an append-only JSONL file."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def record(
        self,
        event_id: str,
        actor_id: str,
        action: str,
        resource: str,
        details: dict[str, Any] | None = None,
    ) -> AuditEvent:
        """Append an audit event."""

        self._validate_required(
            event_id,
            "event_id",
        )
        self._validate_required(
            actor_id,
            "actor_id",
        )
        self._validate_required(
            action,
            "action",
        )
        self._validate_required(
            resource,
            "resource",
        )

        previous_hash = self._last_hash()

        event = AuditEvent(
            event_id=event_id,
            actor_id=actor_id,
            action=action,
            resource=resource,
            timestamp=datetime.now(
                timezone.utc
            ).isoformat(),
            details=dict(details or {}),
            previous_hash=previous_hash,
        )

        event_hash = self._calculate_hash(event)

        event = AuditEvent(
            **{
                **asdict(event),
                "event_hash": event_hash,
            }
        )

        with self.path.open(
            "a",
            encoding="utf-8",
        ) as file:
            file.write(
                json.dumps(
                    asdict(event),
                    ensure_ascii=False,
                    sort_keys=True,
                    default=str,
                )
            )
            file.write("\n")

        return event

    def read_events(self) -> list[AuditEvent]:
        """Read all audit events."""

        if not self.path.exists():
            return []

        events: list[AuditEvent] = []

        with self.path.open(
            "r",
            encoding="utf-8",
        ) as file:
            for line in file:
                if not line.strip():
                    continue

                events.append(
                    AuditEvent(
                        **json.loads(line)
                    )
                )

        return events

    def verify_integrity(self) -> bool:
        """Verify the complete audit hash chain."""

        events = self.read_events()
        previous_hash = ""

        for event in events:
            if event.previous_hash != previous_hash:
                return False

            expected_hash = self._calculate_hash(
                event
            )

            if event.event_hash != expected_hash:
                return False

            previous_hash = event.event_hash

        return True

    def _last_hash(self) -> str:
        events = self.read_events()

        if not events:
            return ""

        return events[-1].event_hash

    @staticmethod
    def _validate_required(
        value: str,
        field_name: str,
    ) -> None:
        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string"
            )

        if not value.strip():
            raise ValueError(
                f"{field_name} must not be empty"
            )

    @staticmethod
    def _calculate_hash(
        event: AuditEvent,
    ) -> str:
        payload = asdict(event)
        payload["event_hash"] = ""

        raw = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            default=str,
        ).encode("utf-8")

        return hashlib.sha256(raw).hexdigest()