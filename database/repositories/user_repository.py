from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from database.access.repository import BaseRepository, EntityMapper

@dataclass
class User:
    id: int | None
    username: str
    email: str
    password_hash: str | None = None
    status: str = "active"

@dataclass
class UserProfile:
    user_id: int
    display_name: str | None = None
    bio: str | None = None
    avatar_url: str | None = None
    metadata: str | None = None

@dataclass
class UserPreference:
    user_id: int
    language: str | None = None
    timezone: str | None = None
    theme: str | None = None
    preferences: str | None = None


class UserMapper(EntityMapper[User]):
    def from_row(self, row: dict[str, Any]) -> User:
        return User(
            id=row.get("id"),
            username=row["username"],
            email=row["email"],
            password_hash=row.get("password_hash"),
            status=row.get("status", "active"),
        )

    def to_row(self, entity: User) -> dict[str, Any]:
        return {
            "username": entity.username,
            "email": entity.email,
            "password_hash": entity.password_hash,
            "status": entity.status,
        }

class UserProfileMapper(EntityMapper[UserProfile]):
    def from_row(self, row: dict[str, Any]) -> UserProfile:
        return UserProfile(
            user_id=row["user_id"],
            display_name=row.get("display_name"),
            bio=row.get("bio"),
            avatar_url=row.get("avatar_url"),
            metadata=row.get("metadata"),
        )

    def to_row(self, entity: UserProfile) -> dict[str, Any]:
        return {
            "user_id": entity.user_id,
            "display_name": entity.display_name,
            "bio": entity.bio,
            "avatar_url": entity.avatar_url,
            "metadata": entity.metadata,
        }

class UserPreferenceMapper(EntityMapper[UserPreference]):
    def from_row(self, row: dict[str, Any]) -> UserPreference:
        return UserPreference(
            user_id=row["user_id"],
            language=row.get("language"),
            timezone=row.get("timezone"),
            theme=row.get("theme"),
            preferences=row.get("preferences"),
        )

    def to_row(self, entity: UserPreference) -> dict[str, Any]:
        return {
            "user_id": entity.user_id,
            "language": entity.language,
            "timezone": entity.timezone,
            "theme": entity.theme,
            "preferences": entity.preferences,
        }

class UserRepository(BaseRepository[User]):
    def __init__(self, data_access):
        super().__init__(
            data_access=data_access,
            table="users",
            mapper=UserMapper(),
            primary_key="id",
        )

class UserProfileRepository(BaseRepository[UserProfile]):
    def __init__(self, data_access):
        super().__init__(
            data_access=data_access,
            table="user_profiles",
            mapper=UserProfileMapper(),
            primary_key="user_id",
        )

class UserPreferenceRepository(BaseRepository[UserPreference]):
    def __init__(self, data_access):
        super().__init__(
            data_access=data_access,
            table="user_preferences",
            mapper=UserPreferenceMapper(),
            primary_key="user_id",
        )