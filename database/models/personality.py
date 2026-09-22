"""Personality, emotion, mood and relationship entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

@dataclass
class Personality:
    personality_id: int | None
    user_id: int
    name: str
    description: str = ""
    speaking_style: str = ""
    traits: dict[str, Any] = field(default_factory=dict)
    behaviors: dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"
    active: bool = True

    def __post_init__(self) -> None:
        if self.user_id <= 0:
            raise ValueError("user_id must be greater than zero")

        if not self.name.strip():
            raise ValueError("name must not be empty")

        if not self.version.strip():
            raise ValueError("version must not be empty")

@dataclass
class Emotion:
    emotion_id: int | None
    personality_id: int
    name: str
    intensity: float = 0.0
    valence: float = 0.0
    context: str = ""

    def __post_init__(self) -> None:
        if self.personality_id <= 0:
            raise ValueError("personality_id must be greater than zero")

        if not self.name.strip():
            raise ValueError("name must not be empty")

        if not 0.0 <= self.intensity <= 1.0:
            raise ValueError("intensity must be between 0 and 1")

@dataclass
class Mood:
    mood_id: int | None
    personality_id: int
    state: str
    intensity: float = 0.0

    def __post_init__(self) -> None:
        if self.personality_id <= 0:
            raise ValueError("personality_id must be greater than zero")

        if not self.state.strip():
            raise ValueError("state must not be empty")

        if not 0.0 <= self.intensity <= 1.0:
            raise ValueError("intensity must be between 0 and 1")

@dataclass
class Relationship:
    relationship_id: int | None
    personality_id: int
    target_user_id: int
    relationship_type: str
    strength: float = 0.0

    def __post_init__(self) -> None:
        if self.personality_id <= 0:
            raise ValueError("personality_id must be greater than zero")

        if self.target_user_id <= 0:
            raise ValueError("target_user_id must be greater than zero")

        if not self.relationship_type.strip():
            raise ValueError("relationship_type must not be empty")

        if not 0.0 <= self.strength <= 1.0:
            raise ValueError("strength must be between 0 and 1")