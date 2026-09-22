from database.schema.avatar_schema import (
    AVATAR_TABLES_UP_SQL,
)


def test_avatar_schema_contains_required_tables():
    required = [
        "avatars",
        "avatar_expressions",
        "avatar_animations",
        "avatar_voices",
        "avatar_audio",
        "avatar_visual_states",
    ]

    for table in required:
        assert f"`{table}`" in AVATAR_TABLES_UP_SQL


def test_avatar_schema_contains_relationships():
    assert "FOREIGN KEY" in AVATAR_TABLES_UP_SQL
    assert "avatars" in AVATAR_TABLES_UP_SQL
    assert "avatar_expressions" in AVATAR_TABLES_UP_SQL
    assert "avatar_animations" in AVATAR_TABLES_UP_SQL