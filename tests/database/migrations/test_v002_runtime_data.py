from database.migrations.v002_runtime_data import (
    V002_VERSION,
    V002_NAME,
    UP_SQL,
    DOWN_SQL,
)


def test_runtime_migration_metadata():
    assert V002_VERSION == 2
    assert V002_NAME == "runtime_data"


def test_runtime_migration_creates_required_tables():
    sql = "\n".join(UP_SQL)

    assert "CREATE TABLE IF NOT EXISTS users" in sql
    assert "CREATE TABLE IF NOT EXISTS user_profiles" in sql
    assert "CREATE TABLE IF NOT EXISTS user_preferences" in sql
    assert "CREATE TABLE IF NOT EXISTS conversations" in sql
    assert "CREATE TABLE IF NOT EXISTS messages" in sql


def test_runtime_migration_creates_indexes():
    sql = "\n".join(UP_SQL)

    assert "idx_conversations_user_id" in sql
    assert "idx_conversations_user_status" in sql
    assert "idx_messages_conversation_id" in sql
    assert "idx_messages_conversation_created" in sql


def test_runtime_migration_down_order():
    assert DOWN_SQL[0] == "DROP TABLE IF EXISTS messages"
    assert DOWN_SQL[-1] == "DROP TABLE IF EXISTS users"