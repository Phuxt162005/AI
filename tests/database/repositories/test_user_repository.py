from database.repositories.user_repository import (
    User,
    UserPreference,
    UserPreferenceRepository,
    UserProfile,
    UserProfileRepository,
    UserRepository,
)


def test_user_repository_table_name(fake_data_access):
    repository = UserRepository(fake_data_access)

    assert repository.table_name == "users"


def test_user_profile_repository_table_name(fake_data_access):
    repository = UserProfileRepository(fake_data_access)

    assert repository.table_name == "user_profiles"


def test_user_preference_repository_table_name(fake_data_access):
    repository = UserPreferenceRepository(fake_data_access)

    assert repository.table_name == "user_preferences"


def test_user_mapping(fake_data_access):
    repository = UserRepository(fake_data_access)

    row = {
        "id": 1,
        "username": "alice",
        "email": "alice@example.com",
        "password_hash": "hash",
        "status": "active",
    }

    entity = repository.mapper.map_from_row(row)

    assert isinstance(entity, User)
    assert entity.id == 1
    assert entity.username == "alice"
    assert entity.email == "alice@example.com"


def test_user_to_row(fake_data_access):
    repository = UserRepository(fake_data_access)

    entity = User(
        id=None,
        username="alice",
        email="alice@example.com",
        password_hash="hash",
    )

    row = repository.mapper.map_to_row(entity)

    assert row["username"] == "alice"
    assert row["email"] == "alice@example.com"
    assert row["password_hash"] == "hash"