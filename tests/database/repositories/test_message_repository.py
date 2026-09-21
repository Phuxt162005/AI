from database.repositories.message_repository import (
    Message,
    MessageRepository,
)


def test_message_repository_table_name(fake_data_access):
    repository = MessageRepository(fake_data_access)

    assert repository.table_name == "messages"


def test_message_mapping(fake_data_access):
    repository = MessageRepository(fake_data_access)

    row = {
        "id": 1,
        "conversation_id": 10,
        "role": "user",
        "content": "Hello",
    }

    entity = repository.mapper.map_from_row(row)

    assert isinstance(entity, Message)
    assert entity.id == 1
    assert entity.conversation_id == 10
    assert entity.role == "user"
    assert entity.content == "Hello"