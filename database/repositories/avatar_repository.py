"""Repositories for Avatar data."""

from __future__ import annotations

import json
from typing import Any

from database.access.data_access import DataAccess
from database.access.repository import (
    BaseRepository,
    EntityMapper,
)
from database.models.avatar import (
    Animation,
    Audio,
    Avatar,
    Expression,
    VisualState,
    Voice,
)

def _json(value: Any) -> dict[str, Any]:
    if value is None:
        return {}

    if isinstance(value, dict):
        return value

    if isinstance(value, str):
        return json.loads(value)

    return dict(value)

class AvatarRepository(BaseRepository[Avatar]):
    def __init__(self, data_access: DataAccess) -> None:
        mapper = EntityMapper(
            from_row=lambda row: Avatar(
                avatar_id=row.get("avatar_id"),
                user_id=row["user_id"],
                name=row["name"],
                model_reference=row.get(
                    "model_reference"
                ),
                display_configuration=_json(
                    row.get("display_configuration")
                ),
                status=row.get("status", "active"),
            ),
            to_row=lambda entity: {
                **{
                    "user_id": entity.user_id,
                    "name": entity.name,
                    "model_reference": (
                        entity.model_reference
                    ),
                    "display_configuration": json.dumps(
                        entity.display_configuration
                    ),
                    "status": entity.status,
                },
                **(
                    {"avatar_id": entity.avatar_id}
                    if entity.avatar_id is not None
                    else {}
                ),
            },
        )

        super().__init__(
            data_access=data_access,
            table_name="avatars",
            mapper=mapper,
            primary_key="avatar_id",
        )

    def list_by_user(self, user_id: int) -> list[Avatar]:
        rows = self.data_access.query(
            "SELECT * FROM `avatars` "
            "WHERE `user_id` = %s "
            "ORDER BY `avatar_id`",
            [user_id],
        )

        return [
            self.mapper.map_from_row(row)
            for row in rows
        ]

class ExpressionRepository(BaseRepository[Expression]):
    def __init__(self, data_access: DataAccess) -> None:
        mapper = EntityMapper(
            from_row=lambda row: Expression(
                expression_id=row.get("expression_id"),
                avatar_id=row["avatar_id"],
                name=row["name"],
                emotion=row.get("emotion", ""),
                parameters=_json(
                    row.get("parameters")
                ),
            ),
            to_row=lambda entity: {
                **{
                    "avatar_id": entity.avatar_id,
                    "name": entity.name,
                    "emotion": entity.emotion,
                    "parameters": json.dumps(
                        entity.parameters
                    ),
                },
                **(
                    {"expression_id": entity.expression_id}
                    if entity.expression_id is not None
                    else {}
                ),
            },
        )

        super().__init__(
            data_access=data_access,
            table_name="avatar_expressions",
            mapper=mapper,
            primary_key="expression_id",
        )

class AnimationRepository(BaseRepository[Animation]):
    def __init__(self, data_access: DataAccess) -> None:
        mapper = EntityMapper(
            from_row=lambda row: Animation(
                animation_id=row.get("animation_id"),
                avatar_id=row["avatar_id"],
                name=row["name"],
                intent=row.get("intent", "idle"),
                loop=bool(row.get("loop", False)),
                duration_ms=int(
                    row.get("duration_ms", 0)
                ),
                transition_ms=int(
                    row.get("transition_ms", 0)
                ),
                asset_reference=row.get(
                    "asset_reference"
                ),
            ),
            to_row=lambda entity: {
                **{
                    "avatar_id": entity.avatar_id,
                    "name": entity.name,
                    "intent": entity.intent,
                    "loop": entity.loop,
                    "duration_ms": entity.duration_ms,
                    "transition_ms": entity.transition_ms,
                    "asset_reference": (
                        entity.asset_reference
                    ),
                },
                **(
                    {"animation_id": entity.animation_id}
                    if entity.animation_id is not None
                    else {}
                ),
            },
        )

        super().__init__(
            data_access=data_access,
            table_name="avatar_animations",
            mapper=mapper,
            primary_key="animation_id",
        )

class VoiceRepository(BaseRepository[Voice]):
    def __init__(self, data_access: DataAccess) -> None:
        mapper = EntityMapper(
            from_row=lambda row: Voice(
                voice_id=row.get("voice_id"),
                avatar_id=row["avatar_id"],
                external_voice_id=row[
                    "external_voice_id"
                ],
                model=row.get("model", ""),
                language=row.get("language", ""),
                configuration=_json(
                    row.get("configuration")
                ),
                speech_parameters=_json(
                    row.get("speech_parameters")
                ),
            ),
            to_row=lambda entity: {
                **{
                    "avatar_id": entity.avatar_id,
                    "external_voice_id": (
                        entity.external_voice_id
                    ),
                    "model": entity.model,
                    "language": entity.language,
                    "configuration": json.dumps(
                        entity.configuration
                    ),
                    "speech_parameters": json.dumps(
                        entity.speech_parameters
                    ),
                },
                **(
                    {"voice_id": entity.voice_id}
                    if entity.voice_id is not None
                    else {}
                ),
            },
        )

        super().__init__(
            data_access=data_access,
            table_name="avatar_voices",
            mapper=mapper,
            primary_key="voice_id",
        )

class AudioRepository(BaseRepository[Audio]):
    def __init__(self, data_access: DataAccess) -> None:
        mapper = EntityMapper(
            from_row=lambda row: Audio(
                audio_id=row.get("audio_id"),
                avatar_id=row["avatar_id"],
                asset_reference=row["asset_reference"],
                content_type=row.get("content_type", "audio"),
                duration_ms=int(row.get("duration_ms", 0)),
                metadata=_json(row.get("metadata")),
            ),
            to_row=lambda entity: {
                **{
                    "avatar_id": entity.avatar_id,
                    "asset_reference": (
                        entity.asset_reference
                    ),
                    "content_type": entity.content_type,
                    "duration_ms": entity.duration_ms,
                    "metadata": json.dumps(
                        entity.metadata
                    ),
                },
                **(
                    {"audio_id": entity.audio_id}
                    if entity.audio_id is not None
                    else {}
                ),
            },
        )

        super().__init__(
            data_access=data_access,
            table_name="avatar_audio",
            mapper=mapper,
            primary_key="audio_id",
        )

class VisualStateRepository(BaseRepository[VisualState]):
    def __init__(self, data_access: DataAccess) -> None:
        mapper = EntityMapper(
            from_row=lambda row: VisualState(
                visual_state_id=row.get("visual_state_id"),
                avatar_id=row["avatar_id"],
                expression_id=row.get("expression_id"),
                animation_id=row.get("animation_id"),
                pose=row.get("pose", "idle"),
                visible=bool(row.get("visible", True)),
                parameters=_json(row.get("parameters")),
            ),
            to_row=lambda entity: {
                **{
                    "avatar_id": entity.avatar_id,
                    "expression_id": entity.expression_id,
                    "animation_id": entity.animation_id,
                    "pose": entity.pose,
                    "visible": entity.visible,
                    "parameters": json.dumps(
                        entity.parameters
                    ),
                },
                **(
                    {
                        "visual_state_id":
                            entity.visual_state_id
                    }
                    if entity.visual_state_id is not None
                    else {}
                ),
            },
        )

        super().__init__(
            data_access=data_access,
            table_name="avatar_visual_states",
            mapper=mapper,
            primary_key="visual_state_id",
        )