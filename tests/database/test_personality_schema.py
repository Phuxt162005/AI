from database.schema.personality_schema import (
    PERSONALITY_TABLES_UP_SQL,
)


def test_personality_schema_contains_required_tables():
    required = [
        "personalities",
        "personality_emotions",
        "personality_moods",
        "personality_relationships",
    ]

    for table in required:
        assert f"`{table}`" in PERSONALITY_TABLES_UP_SQL


def test_personality_relationships_are_defined():
    assert "FOREIGN KEY" in PERSONALITY_TABLES_UP_SQL
    assert "users" in PERSONALITY_TABLES_UP_SQL