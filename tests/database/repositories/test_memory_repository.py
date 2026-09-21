from core.memory.memory import (
    MemoryItem,
    MemoryStatus,
    MemoryType,
)
from database.repositories.memory_repository import (
    MemoryRepository,
)

def test_memory_repository_table_name(fake_data_access):
    repository = MemoryRepository(fake_data_access)

    assert repository.table_name == "memories"
    assert repository.primary_key == "memory_id"


def test_memory_mapping(fake_data_access):
    repository = MemoryRepository(fake_data_access)

    row = {
        "memory_id": 1,
        "user_id": 10,
        "memory_type": "semantic",
        "content": "User likes Python.",
        "importance": 0.8,
        "status": "active",
    }

    entity = repository.mapper.map_from_row(row)

    assert isinstance(entity, MemoryItem)
    assert entity.memory_id == 1
    assert entity.user_id == 10
    assert entity.memory_type == MemoryType.SEMANTIC
    assert entity.content == "User likes Python."
    assert entity.importance == 0.8
    assert entity.status == MemoryStatus.ACTIVE


def test_memory_to_row(fake_data_access):
    repository = MemoryRepository(fake_data_access)

    entity = MemoryItem(
        memory_id=None,
        user_id=10,
        memory_type=MemoryType.LONG_TERM,
        content="User prefers Vietnamese.",
        importance=0.9,
    )

    row = repository.mapper.map_to_row(entity)

    assert row["user_id"] == 10
    assert row["memory_type"] == "long_term"
    assert row["content"] == "User prefers Vietnamese."
    assert row["importance"] == 0.9
    assert row["status"] == "active"


def test_memory_user_query(fake_data_access):
    repository = MemoryRepository(fake_data_access)

    repository.list_by_user(
        user_id=10,
        limit=20,
    )

    sql, parameters = fake_data_access.queries[-1]

    assert "FROM `memories`" in sql
    assert "`user_id` = %s" in sql
    assert parameters[0] == 10


def test_memory_type_query(fake_data_access):
    repository = MemoryRepository(fake_data_access)

    repository.list_by_type(
        user_id=10,
        memory_type=MemoryType.EPISODIC,
        limit=10,
    )

    sql, parameters = fake_data_access.queries[-1]

    assert "FROM `memories`" in sql
    assert "`memory_type` = %s" in sql
    assert parameters == [
        10,
        "episodic",
        "active",
        10,
    ]


def test_mark_forgotten(fake_data_access):
    repository = MemoryRepository(fake_data_access)

    repository.mark_forgotten(
        memory_id=5,
        user_id=10,
    )

    sql, parameters = fake_data_access.executed[-1]

    assert "UPDATE `memories`" in sql
    assert parameters == [
        "forgotten",
        5,
        10,
    ]