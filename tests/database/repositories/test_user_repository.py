from database.repositories.user_repository import (
    User,
    UserMapper,
    UserProfile,
    UserProfileMapper,
    UserPreference,
    UserPreferenceMapper,
)

def test_user_mapper_round_trip():
    mapper = UserMapper()
    user = User(
        id=1,
        username="alice",
        email="alice@example.com",
        password_hash="hash",
        status="active",
    )
    row = mapper.to_row(user)

    assert row["username"] == "alice"
    assert row["email"] == "alice@example.com"
    restored = mapper.from_row({"id": 1, **row})
    assert restored == user


def test_user_profile_mapper():
    mapper = UserProfileMapper()
    profile = UserProfile(
        user_id=1,
        display_name="Alice",
        bio="Developer",
        avatar_url="/avatar.png",
        metadata="{}",
    )
    restored = mapper.from_row(mapper.to_row(profile))
    assert restored == profile


def test_user_preference_mapper():
    mapper = UserPreferenceMapper()
    preference = UserPreference(
        user_id=1,
        language="vi",
        timezone="Asia/Ho_Chi_Minh",
        theme="dark",
        preferences="{}",
    )
    restored = mapper.from_row(mapper.to_row(preference))
    assert restored == preference