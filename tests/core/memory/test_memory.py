import pytest

from core.memory.memory import (
    MemoryItem,
    MemoryStatus,
    MemoryType,
)

def test_memory_item_creation():
    memory = MemoryItem(
        memory_id=1,
        user_id=10,
        memory_type=MemoryType.LONG_TERM,
        content="User prefers Python.",
        importance=0.8,
    )

    assert memory.memory_id == 1
    assert memory.user_id == 10
    assert memory.memory_type == MemoryType.LONG_TERM
    assert memory.content == "User prefers Python."
    assert memory.importance == 0.8
    assert memory.status == MemoryStatus.ACTIVE

def test_memory_type_conversion():
    memory = MemoryItem(
        memory_id=1,
        user_id=10,
        memory_type="semantic",
        content="Python is preferred.",
    )
    assert memory.memory_type == MemoryType.SEMANTIC

def test_invalid_user():
    with pytest.raises(ValueError):
        MemoryItem(
            memory_id=1,
            user_id=0,
            memory_type=MemoryType.WORKING,
            content="test",
        )

def test_empty_content():
    with pytest.raises(ValueError):
        MemoryItem(
            memory_id=1,
            user_id=1,
            memory_type=MemoryType.WORKING,
            content="",
        )

def test_invalid_importance():
    with pytest.raises(ValueError):
        MemoryItem(
            memory_id=1,
            user_id=1,
            memory_type=MemoryType.WORKING,
            content="test",
            importance=1.5,
        )