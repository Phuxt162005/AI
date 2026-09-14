"""Core state definitions for the Avatar system.

This module contains technology-independent Avatar state models.

The Avatar state describes WHAT the avatar is doing or expressing.
It does not contain rendering logic, Avatar model logic, or AI reasoning.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping

class AvatarActivity(str, Enum):
    """High-level activity currently performed by the avatar."""

    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    TALKING = "talking"
    REACTING = "reacting"

class AvatarExpression(str, Enum):
    """Technology-independent facial/emotional expression."""

    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    SURPRISED = "surprised"
    FEARFUL = "fearful"
    DISGUSTED = "disgusted"
    CURIOUS = "curious"
    CONCERNED = "concerned"
    RELIEVED = "relieved"

class AvatarPose(str, Enum):
    """High-level body/head pose of the avatar."""

    DEFAULT = "default"
    RELAXED = "relaxed"
    ATTENTIVE = "attentive"
    THINKING = "thinking"
    EXCITED = "excited"
    SAD = "sad"

class AvatarVisibility(str, Enum):
    """Visibility state of the avatar."""

    HIDDEN = "hidden"
    VISIBLE = "visible"

@dataclass(frozen=True)
class AvatarState:
    """Immutable snapshot of the current Avatar state.

    This class intentionally contains no rendering or model-specific
    information. A renderer or VTuber adapter can interpret this state
    according to its own technology.
    """

    activity: AvatarActivity = AvatarActivity.IDLE
    expression: AvatarExpression = AvatarExpression.NEUTRAL
    pose: AvatarPose = AvatarPose.DEFAULT
    visibility: AvatarVisibility = AvatarVisibility.VISIBLE

    parameters: Mapping[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        normalized_parameters = {
            str(name): float(value)
            for name, value in self.parameters.items()
        }

        for name, value in normalized_parameters.items():
            if not -1.0 <= value <= 1.0:
                raise ValueError(f"Avatar parameter '{name}' must be between -1.0 and 1.0.")

        object.__setattr__(self, "parameters", normalized_parameters)

    def with_activity(self, activity: AvatarActivity) -> "AvatarState":
        """Return a copy with a different activity."""

        return AvatarState(
            activity=activity,
            expression=self.expression,
            pose=self.pose,
            visibility=self.visibility,
            parameters=self.parameters,
        )

    def with_expression(self, expression: AvatarExpression) -> "AvatarState":
        """Return a copy with a different expression."""

        return AvatarState(
            activity=self.activity,
            expression=expression,
            pose=self.pose,
            visibility=self.visibility,
            parameters=self.parameters,
        )

    def with_pose(self, pose: AvatarPose) -> "AvatarState":
        """Return a copy with a different pose."""

        return AvatarState(
            activity=self.activity,
            expression=self.expression,
            pose=pose,
            visibility=self.visibility,
            parameters=self.parameters,
        )

    def with_visibility(self, visibility: AvatarVisibility) -> "AvatarState":
        """Return a copy with a different visibility state."""

        return AvatarState(
            activity=self.activity,
            expression=self.expression,
            pose=self.pose,
            visibility=visibility,
            parameters=self.parameters,
        )

    def with_parameter(self, name: str, value: float) -> "AvatarState":
        """Return a copy with one parameter changed."""

        if not -1.0 <= value <= 1.0:
            raise ValueError(f"Avatar parameter '{name}' must be between -1.0 and 1.0.")

        updated_parameters = dict(self.parameters)
        updated_parameters[str(name)] = float(value)

        return AvatarState(
            activity=self.activity,
            expression=self.expression,
            pose=self.pose,
            visibility=self.visibility,
            parameters=updated_parameters,
        )

class AvatarActionType(str, Enum):
    """Types of high-level actions an avatar can perform."""

    SET_ACTIVITY = "set_activity"
    SET_EXPRESSION = "set_expression"
    SET_POSE = "set_pose"
    SET_VISIBILITY = "set_visibility"
    SET_PARAMETER = "set_parameter"
    RESET = "reset"

@dataclass(frozen=True)
class AvatarAction:
    """A technology-independent command for changing Avatar state."""

    type: AvatarActionType
    value: object | None = None
    parameter_name: str | None = None

    def __post_init__(self) -> None:
        if self.type is AvatarActionType.SET_ACTIVITY:
            if not isinstance(self.value, AvatarActivity):
                raise TypeError("SET_ACTIVITY requires an AvatarActivity value.")

        elif self.type is AvatarActionType.SET_EXPRESSION:
            if not isinstance(self.value, AvatarExpression):
                raise TypeError("SET_EXPRESSION requires an AvatarExpression value.")

        elif self.type is AvatarActionType.SET_POSE:
            if not isinstance(self.value, AvatarPose):
                raise TypeError("SET_POSE requires an AvatarPose value.")

        elif self.type is AvatarActionType.SET_VISIBILITY:
            if not isinstance(self.value, AvatarVisibility):
                raise TypeError("SET_VISIBILITY requires an AvatarVisibility value.")

        elif self.type is AvatarActionType.SET_PARAMETER:
            if not self.parameter_name:
                raise ValueError("SET_PARAMETER requires parameter_name.")

            if not isinstance(self.value, (int, float)):
                raise TypeError("SET_PARAMETER requires a numeric value.")

            if not -1.0 <= float(self.value) <= 1.0:
                raise ValueError("Avatar parameter must be between -1.0 and 1.0.")

        elif self.type is AvatarActionType.RESET:
            if self.value is not None or self.parameter_name is not None:
                raise ValueError("RESET does not accept a value or parameter_name.")