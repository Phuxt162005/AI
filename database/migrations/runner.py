"""Database migration runner."""

from __future__ import annotations

from typing import Any

from database.migrations.migration import Migration

class MigrationRunner:
    """Run ordered database migrations."""

    def __init__(self, migrations: list[Migration]) -> None:
        self.migrations = sorted(
            migrations,
            key=lambda migration: migration.version,
        )

        self._validate_versions()

    def _validate_versions(self) -> None:
        versions = [
            migration.version
            for migration in self.migrations
        ]

        if len(versions) != len(set(versions)):
            raise ValueError("Migration versions must be unique")

    def pending_versions(self, applied_versions: set[int]) -> list[int]:
        """Return migrations that have not been applied."""

        return [
            migration.version
            for migration in self.migrations
            if migration.version
            not in applied_versions
        ]

    def migrate(
        self,
        applied_versions: set[int],
        execute: Any,
    ) -> list[int]:
        """Apply all pending migrations in order."""

        applied: list[int] = []
        for migration in self.migrations:
            if migration.version in applied_versions:
                continue
            migration.apply(execute)
            applied_versions.add(migration.version)
            applied.append(migration.version)

        return applied

    def rollback_last(self, applied_versions: set[int], execute: Any) -> int | None:
        """Rollback the latest applied migration."""

        applied = [
            migration
            for migration in self.migrations
            if migration.version in applied_versions
        ]
        if not applied:
            return None
        migration = max(applied, key=lambda item: item.version)
        migration.rollback(execute)
        applied_versions.remove(migration.version)

        return migration.version