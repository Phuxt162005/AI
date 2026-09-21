from database.repositories.conversation_repository import (
    Conversation,
    ConversationMapper,
    ConversationRepository,
)


class FakeDataAccess:
    def __init__(self):
        self.rows = []

    def query(self, sql, parameters=None):
        self.last_sql = sql
        self.last_parameters = parameters
        return self.rows


def test_conversation_mapper_round_trip():
    mapper = ConversationMapper()

    conversation = Conversation(
        id=10,
        user_id=1,
        title="Test conversation",
        status="active",
    )

    row = mapper.to_row(conversation)

    restored = mapper.from_row(
        {
            "id": 10,
            **row,
        }
    )

    assert restored == conversation


def test_list_by_user():
    data_access = FakeDataAccess()
    data_access.rows = [
        {
            "id": 1,
            "user_id": 10,
            "title": "First",
            "status": "active",
        },
        {
            "id": 2,
            "user_id": 10,
            "title": "Second",
            "status": "closed",
        },
    ]

    repository = ConversationRepository(data_access)

    conversations = repository.list_by_user(10)

    assert len(conversations) == 2
    assert conversations[0].user_id == 10
    assert data_access.last_parameters == (10,)


def test_list_active_by_user():
    data_access = FakeDataAccess()
    data_access.rows = [
        {
            "id": 1,
            "user_id": 10,
            "title": "Active",
            "status": "active",
        }
    ]

    repository = ConversationRepository(data_access)

    conversations = repository.list_active_by_user(10)

    assert len(conversations) == 1
    assert conversations[0].status == "active"
    assert data_access.last_parameters == (10,)


def test_repository_has_correct_table():
    repository = ConversationRepository(FakeDataAccess())

    assert repository.table == "conversations"
    assert repository.primary_key == "id"