from database.schema.runtime_schema import (
    CREATE_USERS_TABLE_SQL,
    CREATE_USER_PROFILES_TABLE_SQL,
    CREATE_USER_PREFERENCES_TABLE_SQL,
    CREATE_CONVERSATIONS_TABLE_SQL,
    CREATE_MESSAGES_TABLE_SQL,
    CREATE_RUNTIME_INDEXES_SQL,
    RUNTIME_SCHEMA_SQL,
)

def test_users_schema_contains_primary_and_unique_constraints():
    sql = CREATE_USERS_TABLE_SQL

    assert "PRIMARY KEY" in sql
    assert "UNIQUE (username)" in sql
    assert "UNIQUE (email)" in sql
    assert "NOT NULL" in sql


def test_user_profile_schema_has_foreign_key():
    sql = CREATE_USER_PROFILES_TABLE_SQL

    assert "PRIMARY KEY" in sql
    assert "FOREIGN KEY (user_id)" in sql
    assert "REFERENCES users(id)" in sql
    assert "ON DELETE CASCADE" in sql


def test_user_preference_schema_has_foreign_key():
    sql = CREATE_USER_PREFERENCES_TABLE_SQL

    assert "PRIMARY KEY" in sql
    assert "FOREIGN KEY (user_id)" in sql
    assert "REFERENCES users(id)" in sql


def test_conversation_schema_has_user_relationship():
    sql = CREATE_CONVERSATIONS_TABLE_SQL

    assert "PRIMARY KEY" in sql
    assert "FOREIGN KEY (user_id)" in sql
    assert "REFERENCES users(id)" in sql
    assert "user_id BIGINT NOT NULL" in sql


def test_message_schema_has_conversation_relationship():
    sql = CREATE_MESSAGES_TABLE_SQL

    assert "PRIMARY KEY" in sql
    assert "FOREIGN KEY (conversation_id)" in sql
    assert "REFERENCES conversations(id)" in sql
    assert "content TEXT NOT NULL" in sql


def test_runtime_indexes_cover_required_lookups():
    joined = "\n".join(CREATE_RUNTIME_INDEXES_SQL)

    assert "idx_conversations_user_id" in joined
    assert "idx_messages_conversation_id" in joined
    assert "idx_messages_conversation_created" in joined


def test_runtime_schema_contains_all_tables():
    assert len(RUNTIME_SCHEMA_SQL) >= 8