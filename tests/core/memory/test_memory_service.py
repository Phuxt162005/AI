from core.memory.memory import (
    MemoryItem,
    MemoryType,
)
from core.memory.memory_service import MemoryService


class FakeMemoryRepository:
    def __init__(self):
        self.created = []
        self.updated = []
        self.forgotten = []
        self.deleted = []
        self.items = {}

    def create(self, entity):
        self.created.append(entity)

        if entity.memory_id is None:
            entity.memory_id = 1

        self.items[entity.memory_id] = entity

        return entity

    def update(self, entity_id, entity):
        self.updated.append((entity_id, entity))
        self.items[entity_id] = entity
        return entity

    def find_by_content(self, user_id, content):
        for item in self.items.values():
            if (
                item.user_id == user_id
                and item.content == content
            ):
                return item

        return None

    def list_by_user(self, user_id, limit=100):
        return [
            item
            for item in self.items.values()
            if item.user_id == user_id
        ][:limit]

    def list_by_type(self, user_id, memory_type, limit=100):
        return [
            item
            for item in self.items.values()
            if (
                item.user_id == user_id
                and item.memory_type == memory_type
            )
        ][:limit]

    def mark_forgotten(self, memory_id, user_id):
        self.forgotten.append((memory_id, user_id))

    def expire_due(self):
        pass

    @property
    def data_access(self):
        return None

    @property
    def mapper(self):
        return None


def test_save_memory():
    repository = FakeMemoryRepository()
    service = MemoryService(repository)

    memory = MemoryItem(
        memory_id=None,
        user_id=10,
        memory_type=MemoryType.SEMANTIC,
        content="User likes Python.",
        importance=0.8,
    )

    result = service.save(memory)

    assert result.user_id == 10
    assert result.content == "User likes Python."
    assert len(repository.created) == 1


def test_save_updates_existing_memory():
    repository = FakeMemoryRepository()

    existing = MemoryItem(
        memory_id=1,
        user_id=10,
        memory_type=MemoryType.SEMANTIC,
        content="User likes Python.",
        importance=0.5,
    )

    repository.items[1] = existing

    service = MemoryService(repository)

    memory = MemoryItem(
        memory_id=None,
        user_id=10,
        memory_type=MemoryType.SEMANTIC,
        content="User likes Python.",
        importance=0.9,
    )

    result = service.save(memory)

    assert result.memory_id == 1
    assert result.importance == 0.9
    assert len(repository.updated) == 1


def test_retrieve_isolated_by_user():
    repository = FakeMemoryRepository()

    repository.items[1] = MemoryItem(
        memory_id=1,
        user_id=10,
        memory_type=MemoryType.LONG_TERM,
        content="User 10 memory",
    )

    repository.items[2] = MemoryItem(
        memory_id=2,
        user_id=20,
        memory_type=MemoryType.LONG_TERM,
        content="User 20 memory",
    )

    service = MemoryService(repository)

    result = service.retrieve(user_id=10)

    assert len(result) == 1
    assert result[0].user_id == 10


def test_forget_memory():
    repository = FakeMemoryRepository()

    repository.items[1] = MemoryItem(
        memory_id=1,
        user_id=10,
        memory_type=MemoryType.LONG_TERM,
        content="Test memory",
    )

    service = MemoryService(repository)

    service.forget(
        memory_id=1,
        user_id=10,
    )

    assert repository.forgotten == [(1, 10)]