"""Repositories for users, profiles, and preferences."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from database.access.data_access import DataAccess
from database.access.repository import BaseRepository, EntityMapper


@dataclass
class User:
    id: int | None
    username: str
    email: str
    password_hash: str | None = None
    status: str = "active"
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class UserProfile:
    user_id: int
    display_name: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class UserPreference:
    user_id: int
    language: str = "vi"
    timezone: str = "Asia/Ho_Chi_Minh"
    settings: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


def _user_from_row(row: Any) -> User:
    return User(
        id=row.get("id"),
        username=row["username"],
        email=row["email"],
        password_hash=row.get("password_hash"),
        status=row.get("status", "active"),
        created_at=row.get("created_at"),
        updated_at=row.get("updated_at"),
    )


def _user_to_row(entity: User) -> dict[str, Any]:
    row = {
        "username": entity.username,
        "email": entity.email,
        "password_hash": entity.password_hash,
        "status": entity.status,
    }

    if entity.id is not None:
        row["id"] = entity.id

    return row


def _profile_from_row(row: Any) -> UserProfile:
    return UserProfile(
        user_id=row["user_id"],
        display_name=row.get("display_name"),
        avatar_url=row.get("avatar_url"),
        bio=row.get("bio"),
        created_at=row.get("created_at"),
        updated_at=row.get("updated_at"),
    )


def _profile_to_row(entity: UserProfile) -> dict[str, Any]:
    return {
        "user_id": entity.user_id,
        "display_name": entity.display_name,
        "avatar_url": entity.avatar_url,
        "bio": entity.bio,
    }


def _preference_from_row(row: Any) -> UserPreference:
    return UserPreference(
        user_id=row["user_id"],
        language=row.get("language", "vi"),
        timezone=row.get("timezone", "Asia/Ho_Chi_Minh"),
        settings=row.get("settings"),
        created_at=row.get("created_at"),
        updated_at=row.get("updated_at"),
    )


def _preference_to_row(entity: UserPreference) -> dict[str, Any]:
    return {
        "user_id": entity.user_id,
        "language": entity.language,
        "timezone": entity.timezone,
        "settings": entity.settings,
    }


class UserRepository(BaseRepository[User]):
    """Repository for users."""

    def __init__(self, data_access: DataAccess) -> None:
        mapper = EntityMapper[User](
            from_row=_user_from_row,
            to_row=_user_to_row,
        )

        super().__init__(
            data_access=data_access,
            table_name="users",
            mapper=mapper,
            primary_key="id",
        )

    def get_by_username(self, username: str) -> User | None:
        sql = (
            "SELECT * FROM `users` "
            "WHERE `username` = %s"
        )

        row = self.data_access.query_one(sql, [username])

        if row is None:
            return None

        return self.mapper.map_from_row(row)

    def get_by_email(self, email: str) -> User | None:
        sql = (
            "SELECT * FROM `users` "
            "WHERE `email` = %s"
        )

        row = self.data_access.query_one(sql, [email])

        if row is None:
            return None

        return self.mapper.map_from_row(row)


class UserProfileRepository(BaseRepository[UserProfile]):
    """Repository for user profiles."""

    def __init__(self, data_access: DataAccess) -> None:
        mapper = EntityMapper[UserProfile](
            from_row=_profile_from_row,
            to_row=_profile_to_row,
        )

        super().__init__(
            data_access=data_access,
            table_name="user_profiles",
            mapper=mapper,
            primary_key="user_id",
        )

    def get_by_user_id(self, user_id: int) -> UserProfile | None:
        return self.get_by_id(user_id)


class UserPreferenceRepository(BaseRepository[UserPreference]):
    """Repository for user preferences."""

    def __init__(self, data_access: DataAccess) -> None:
        mapper = EntityMapper[UserPreference](
            from_row=_preference_from_row,
            to_row=_preference_to_row,
        )

        super().__init__(
            data_access=data_access,
            table_name="user_preferences",
            mapper=mapper,
            primary_key="user_id",
        )

    def get_by_user_id(self, user_id: int) -> UserPreference | None:
        return self.get_by_id(user_id)