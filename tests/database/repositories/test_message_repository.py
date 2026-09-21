import pytest

from database.repositories.message_repository import (
    Message,
    MessageMapper,
    MessageRepository,
)


class FakeDataAccess:
    def __init__(self):
        self.rows = []

    def query(self, sql, parameters=None):
        self.last_sql = sql
        self.last_parameters = parameters
        return self.rows


def test_message_mapper_round_trip():
    mapper = MessageMapper()

    message = Message(
        id=1,
        conversation_id=20,
        role="user",
        content="Hello",
    )

    row = mapper.to_row(message)

    restored = mapper.from_row(
        {
            "id": 1,
            **row,
        }
    )

    assert restored == message


def test_list_by_conversation():
    data_access = FakeDataAccess()
    data_access.rows = [
        {
            "id": 1,
            "conversation_id": 20,
            "role": "user",
            "content": "Hello",
        },
        {
            "id": 2,
            "conversation_id": 20,
            "role": "assistant",
            "content": "Hi",
        },
    ]

    repository = MessageRepository(data_access)

    messages = repository.list_by_conversation(20)

    assert len(messages) == 2
    assert messages[0].conversation_id == 20
    assert messages[1].role == "assistant"
    assert data_access.last_parameters == (20,)


def test_list_recent_reverses_database_descending_order():
    data_access = FakeDataAccess()
    data_access.rows = [
        {
            "id": 3,
            "conversation_id": 20,
            "role": "assistant",
            "content": "Third",
        },
        {
            "id": 2,
            "conversation_id": 20,
            "role": "user",
            "content": "Second",
        },
    ]

    repository = MessageRepository(data_access)

    messages = repository.list_recent(20, limit=2)

    assert [message.id for message in messages] == [2, 3]
    assert data_access.last_parameters == (20, 2)


def test_list_recent_rejects_invalid_limit():
    repository = MessageRepository(FakeDataAccess())

    with pytest.raises(ValueError):
        repository.list_recent(20, limit=0)


def test_repository_has_correct_table():
    repository = MessageRepository(FakeDataAccess())

    assert repository.table == "messages"
    assert repository.primary_key == "id"