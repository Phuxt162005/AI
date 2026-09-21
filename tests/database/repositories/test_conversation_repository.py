from database.repositories.conversation_repository import (
    Conversation,
    ConversationRepository,
)


def test_conversation_repository_table_name(fake_data_access):
    repository = ConversationRepository(fake_data_access)

    assert repository.table_name == "conversations"


def test_conversation_mapping(fake_data_access):
    repository = ConversationRepository(fake_data_access)

    row = {
        "id": 1,
        "user_id": 10,
        "title": "Test conversation",
        "status": "active",
    }

    entity = repository.mapper.map_from_row(row)

    assert isinstance(entity, Conversation)
    assert entity.id == 1
    assert entity.user_id == 10
    assert entity.title == "Test conversation"
    assert entity.status == "active"