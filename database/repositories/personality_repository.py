"""Repositories for Personality data."""

from __future__ import annotations

import json
from typing import Any

from database.access.data_access import DataAccess
from database.access.repository import (
    BaseRepository,
    EntityMapper,
)
from database.models.personality import (
    Emotion,
    Mood,
    Personality,
    Relationship,
)

def _json(value: Any) -> dict[str, Any]:
    if value is None:
        return {}

    if isinstance(value, dict):
        return value

    if isinstance(value, str):
        return json.loads(value)

    return dict(value)

class PersonalityRepository(BaseRepository[Personality]):
    def __init__(self, data_access: DataAccess) -> None:
        mapper = EntityMapper(
            from_row=lambda row: Personality(
                personality_id=row.get("personality_id"),
                user_id=row["user_id"],
                name=row["name"],
                description=row.get("description", ""),
                speaking_style=row.get(
                    "speaking_style",
                    "",
                ),
                traits=_json(row.get("traits")),
                behaviors=_json(row.get("behaviors")),
                version=row.get("version", "1.0"),
                active=bool(row.get("active", True)),
            ),
            to_row=lambda entity: {
                **{
                    "user_id": entity.user_id,
                    "name": entity.name,
                    "description": entity.description,
                    "speaking_style": entity.speaking_style,
                    "traits": json.dumps(entity.traits),
                    "behaviors": json.dumps(entity.behaviors),
                    "version": entity.version,
                    "active": entity.active,
                },
                **(
                    {"personality_id": entity.personality_id}
                    if entity.personality_id is not None
                    else {}
                ),
            },
        )

        super().__init__(
            data_access=data_access,
            table_name="personalities",
            mapper=mapper,
            primary_key="personality_id",
        )

    def get_by_user(
        self,
        user_id: int,
    ) -> Personality | None:
        row = self.data_access.query_one(
            "SELECT * FROM `personalities` "
            "WHERE `user_id` = %s",
            [user_id],
        )

        if row is None:
            return None

        return self.mapper.map_from_row(row)

class EmotionRepository(BaseRepository[Emotion]):
    def __init__(self, data_access: DataAccess) -> None:
        mapper = EntityMapper(
            from_row=lambda row: Emotion(
                emotion_id=row.get("emotion_id"),
                personality_id=row["personality_id"],
                name=row["name"],
                intensity=float(row.get("intensity", 0)),
                valence=float(row.get("valence", 0)),
                context=row.get("context", ""),
            ),
            to_row=lambda entity: {
                **{
                    "personality_id": entity.personality_id,
                    "name": entity.name,
                    "intensity": entity.intensity,
                    "valence": entity.valence,
                    "context": entity.context,
                },
                **(
                    {"emotion_id": entity.emotion_id}
                    if entity.emotion_id is not None
                    else {}
                ),
            },
        )

        super().__init__(
            data_access=data_access,
            table_name="personality_emotions",
            mapper=mapper,
            primary_key="emotion_id",
        )

    def list_by_personality(self, personality_id: int) -> list[Emotion]:
        rows = self.data_access.query(
            "SELECT * FROM `personality_emotions` "
            "WHERE `personality_id` = %s "
            "ORDER BY `emotion_id`",
            [personality_id],
        )

        return [
            self.mapper.map_from_row(row)
            for row in rows
        ]

class MoodRepository(BaseRepository[Mood]):
    def __init__(self, data_access: DataAccess) -> None:
        mapper = EntityMapper(
            from_row=lambda row: Mood(
                mood_id=row.get("mood_id"),
                personality_id=row["personality_id"],
                state=row["state"],
                intensity=float(row.get("intensity", 0)),
            ),
            to_row=lambda entity: {
                **{
                    "personality_id": entity.personality_id,
                    "state": entity.state,
                    "intensity": entity.intensity,
                },
                **(
                    {"mood_id": entity.mood_id}
                    if entity.mood_id is not None
                    else {}
                ),
            },
        )

        super().__init__(
            data_access=data_access,
            table_name="personality_moods",
            mapper=mapper,
            primary_key="mood_id",
        )


class RelationshipRepository(BaseRepository[Relationship]):
    def __init__(self, data_access: DataAccess) -> None:
        mapper = EntityMapper(
            from_row=lambda row: Relationship(
                relationship_id=row.get(
                    "relationship_id"
                ),
                personality_id=row["personality_id"],
                target_user_id=row["target_user_id"],
                relationship_type=row[
                    "relationship_type"
                ],
                strength=float(
                    row.get("strength", 0)
                ),
            ),
            to_row=lambda entity: {
                **{
                    "personality_id": entity.personality_id,
                    "target_user_id": entity.target_user_id,
                    "relationship_type": (
                        entity.relationship_type
                    ),
                    "strength": entity.strength,
                },
                **(
                    {
                        "relationship_id":
                            entity.relationship_id
                    }
                    if entity.relationship_id is not None
                    else {}
                ),
            },
        )

        super().__init__(
            data_access=data_access,
            table_name="personality_relationships",
            mapper=mapper,
            primary_key="relationship_id",
        )