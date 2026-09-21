from database.migrations.migration import Migration
from database.migrations.runner import MigrationRunner


def create_migrations():
    return [
        Migration(
            version=1,
            name="create_base_schema",
            up_sql="CREATE DATABASE projectai;",
            down_sql="DROP DATABASE projectai;",
        ),
        Migration(
            version=2,
            name="create_metadata",
            up_sql="CREATE TABLE metadata (id INT);",
            down_sql="DROP TABLE metadata;",
        ),
    ]


def test_migration_definition():
    migration = Migration(
        version=1,
        name="initial",
        up_sql="CREATE TABLE test (id INT);",
        down_sql="DROP TABLE test;",
    )

    assert migration.version == 1
    assert migration.name == "initial"


def test_migration_runner_orders_migrations():
    migrations = [
        create_migrations()[1],
        create_migrations()[0],
    ]

    runner = MigrationRunner(migrations)

    assert [
        migration.version
        for migration in runner.migrations
    ] == [1, 2]


def test_pending_migrations():
    runner = MigrationRunner(
        create_migrations()
    )

    assert runner.pending_versions(
        {1}
    ) == [2]


def test_migrate_runs_pending_migrations():
    runner = MigrationRunner(
        create_migrations()
    )

    applied_versions = set()
    executed = []

    def execute(sql):
        executed.append(sql)

    result = runner.migrate(
        applied_versions,
        execute,
    )

    assert result == [1, 2]
    assert applied_versions == {1, 2}
    assert len(executed) == 2


def test_rollback_last_migration():
    runner = MigrationRunner(
        create_migrations()
    )

    applied_versions = {1, 2}
    executed = []

    def execute(sql):
        executed.append(sql)

    result = runner.rollback_last(
        applied_versions,
        execute,
    )

    assert result == 2
    assert applied_versions == {1}
    assert executed == [
        "DROP TABLE metadata;"
    ]


def test_duplicate_migration_versions_rejected():
    migration_a = Migration(
        version=1,
        name="a",
        up_sql="SELECT 1;",
        down_sql="SELECT 1;",
    )

    migration_b = Migration(
        version=1,
        name="b",
        up_sql="SELECT 2;",
        down_sql="SELECT 2;",
    )

    try:
        MigrationRunner(
            [migration_a, migration_b]
        )
        assert False
    except ValueError:
        assert True