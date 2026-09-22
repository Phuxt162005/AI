"""Avatar persistence entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

@dataclass
class Avatar:
    avatar_id: int | None
    user_id: int
    name: str
    model_reference: str | None = None
    display_configuration: dict[str, Any] = field(default_factory=dict)
    status: str = "active"

    def __post_init__(self) -> None:
        if self.user_id <= 0:
            raise ValueError("user_id must be greater than zero")

        if not self.name.strip():
            raise ValueError("name must not be empty")

@dataclass
class Expression:
    expression_id: int | None
    avatar_id: int
    name: str
    emotion: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.avatar_id <= 0:
            raise ValueError("avatar_id must be greater than zero")

        if not self.name.strip():
            raise ValueError("name must not be empty")

@dataclass
class Animation:
    animation_id: int | None
    avatar_id: int
    name: str
    intent: str = "idle"
    loop: bool = False
    duration_ms: int = 0
    transition_ms: int = 0
    asset_reference: str | None = None

    def __post_init__(self) -> None:
        if self.avatar_id <= 0:
            raise ValueError("avatar_id must be greater than zero")

        if not self.name.strip():
            raise ValueError("name must not be empty")

        if self.duration_ms < 0:
            raise ValueError("duration_ms must not be negative")

        if self.transition_ms < 0:
            raise ValueError("transition_ms must not be negative")

@dataclass
class Voice:
    voice_id: int | None
    avatar_id: int
    external_voice_id: str
    model: str = ""
    language: str = ""
    configuration: dict[str, Any] = field(default_factory=dict)
    speech_parameters: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.avatar_id <= 0:
            raise ValueError("avatar_id must be greater than zero")

        if not self.external_voice_id.strip():
            raise ValueError("external_voice_id must not be empty")


@dataclass
class Audio:
    audio_id: int | None
    avatar_id: int
    asset_reference: str
    content_type: str = "audio"
    duration_ms: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.avatar_id <= 0:
            raise ValueError("avatar_id must be greater than zero")

        if not self.asset_reference.strip():
            raise ValueError("asset_reference must not be empty")

        if self.duration_ms < 0:
            raise ValueError("duration_ms must not be negative")

@dataclass
class VisualState:
    visual_state_id: int | None
    avatar_id: int
    expression_id: int | None = None
    animation_id: int | None = None
    pose: str = "idle"
    visible: bool = True
    parameters: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.avatar_id <= 0:
            raise ValueError("avatar_id must be greater than zero")

        if (
            self.expression_id is not None
            and self.expression_id <= 0
        ):
            raise ValueError("expression_id must be greater than zero")

        if (
            self.animation_id is not None
            and self.animation_id <= 0
        ):
            raise ValueError("animation_id must be greater than zero")

        if not self.pose.strip():
            raise ValueError("pose must not be empty")