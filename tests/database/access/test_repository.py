from dataclasses import dataclass

from database.access.data_access import DataAccess
from database.access.repository import (
    BaseRepository,
    EntityMapper,
)


@dataclass
class TestEntity:
    id: int
    name: str


class FakeConnection:
    def __init__(self):
        self.executed = []
        self.rows = []

    def cursor(self):
        return FakeCursor(self)

    def commit(self):
        pass

    def rollback(self):
        pass


class FakeCursor:
    def __init__(self, connection):
        self.connection = connection

    def execute(self, sql, parameters=()):
        self.connection.executed.append(
            (sql, tuple(parameters))
        )

    def fetchall(self):
        return self.connection.rows

    def fetchone(self):
        if not self.connection.rows:
            return None
        return self.connection.rows[0]


class FakeDatabaseConnection:
    def __init__(self):
        self.raw = FakeConnection()

    def cursor(self):
        return self.raw.cursor()

    def commit(self):
        self.raw.commit()

    def rollback(self):
        self.raw.rollback()


def create_repository():
    connection = FakeDatabaseConnection()

    data_access = DataAccess(connection)

    mapper = EntityMapper(
        from_row=lambda row: TestEntity(
            id=row["id"],
            name=row["name"],
        ),
        to_row=lambda entity: {
            "id": entity.id,
            "name": entity.name,
        },
    )

    repository = BaseRepository(
        data_access=data_access,
        table_name="test_entity",
        mapper=mapper,
    )

    return connection, repository


def test_repository_create():
    connection, repository = create_repository()

    entity = TestEntity(
        id=1,
        name="ProjectAI",
    )

    result = repository.create(entity)

    assert result == entity
    assert len(connection.raw.executed) == 1

    sql, parameters = (
        connection.raw.executed[0]
    )

    assert "INSERT INTO" in sql
    assert parameters == (
        1,
        "ProjectAI",
    )


def test_repository_get_by_id():
    connection, repository = create_repository()

    connection.raw.rows = [
        {
            "id": 1,
            "name": "ProjectAI",
        }
    ]

    result = repository.get_by_id(1)

    assert result == TestEntity(
        id=1,
        name="ProjectAI",
    )


def test_repository_get_by_id_not_found():
    connection, repository = create_repository()

    connection.raw.rows = []

    result = repository.get_by_id(999)

    assert result is None


def test_repository_list_all():
    connection, repository = create_repository()

    connection.raw.rows = [
        {
            "id": 1,
            "name": "AI",
        },
        {
            "id": 2,
            "name": "Assistant",
        },
    ]

    result = repository.list_all()

    assert result == [
        TestEntity(
            id=1,
            name="AI",
        ),
        TestEntity(
            id=2,
            name="Assistant",
        ),
    ]


def test_repository_update():
    connection, repository = create_repository()

    entity = TestEntity(
        id=1,
        name="Updated",
    )

    result = repository.update(
        1,
        entity,
    )

    assert result == entity

    sql, parameters = (
        connection.raw.executed[0]
    )

    assert "UPDATE" in sql
    assert parameters == (
        1,
        "Updated",
        1,
    )


def test_repository_delete():
    connection, repository = create_repository()

    repository.delete(1)

    sql, parameters = (
        connection.raw.executed[0]
    )

    assert "DELETE FROM" in sql
    assert parameters == (1,)


def test_entity_mapper():
    mapper = EntityMapper(
        from_row=lambda row: TestEntity(
            id=row["id"],
            name=row["name"],
        ),
        to_row=lambda entity: {
            "id": entity.id,
            "name": entity.name,
        },
    )

    entity = TestEntity(
        id=1,
        name="AI",
    )

    row = mapper.map_to_row(entity)
    restored = mapper.map_from_row(row)

    assert row == {
        "id": 1,
        "name": "AI",
    }
    assert restored == entity