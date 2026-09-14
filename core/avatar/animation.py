"""Technology-independent Avatar animation system.

This module converts Avatar actions into animation intents and manages
animation playback state.

The animation system does not contain:
- AI reasoning
- Personality logic
- Emotion calculation
- Rendering logic
- VTuber/Live2D/VRM-specific logic

It operates entirely on technology-independent Avatar actions and
animation abstractions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping

from .state import (
    AvatarAction,
    AvatarActionType,
    AvatarActivity,
    AvatarExpression,
    AvatarPose,
)

class AnimationType(str, Enum):
    """High-level technology-independent animation categories."""

    IDLE = "idle"
    LISTEN = "listen"
    THINK = "think"
    TALK = "talk"
    REACT = "react"
    EMOTION = "emotion"
    POSE = "pose"
    TRANSITION = "transition"

class AnimationPlaybackState(str, Enum):
    """Current playback status of an animation."""

    STOPPED = "stopped"
    PLAYING = "playing"

@dataclass(frozen=True)
class AnimationDefinition:
    """Definition of an animation.

    This describes animation intent only. It does not contain renderer
    or VTuber-specific implementation details.
    """

    name: str
    type: AnimationType
    duration: float = 0.0
    priority: int = 0
    loop: bool = False
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        name = str(self.name).strip()

        if not name:
            raise ValueError("Animation name cannot be empty.")
        if self.duration < 0.0:
            raise ValueError("Animation duration cannot be negative.")
        if not isinstance(self.priority, int):
            raise TypeError("Animation priority must be an integer.")

        object.__setattr__(self, "name", name)
        object.__setattr__(self, "metadata", dict(self.metadata))

    @property
    def is_transient(self) -> bool:
        """Return whether this animation is a short-lived animation."""

        return self.type in {
            AnimationType.EMOTION,
            AnimationType.REACT,
            AnimationType.TRANSITION,
        }

@dataclass(frozen=True)
class AnimationIntent:
    """Technology-independent request to play an animation."""

    animation: AnimationDefinition
    source_action: AvatarAction | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", dict(self.metadata))


@dataclass(frozen=True)
class AnimationState:
    """Immutable snapshot of the current animation playback state."""

    animation: AnimationDefinition | None = None
    elapsed_time: float = 0.0
    playback: AnimationPlaybackState = AnimationPlaybackState.STOPPED

    def __post_init__(self) -> None:
        if self.elapsed_time < 0.0:
            raise ValueError("elapsed_time cannot be negative.")

        if self.animation is None and self.playback is AnimationPlaybackState.PLAYING:
            raise ValueError("Animation state cannot be PLAYING without an animation.")

        if (
            self.animation is not None
            and self.animation.duration > 0.0
            and self.elapsed_time > self.animation.duration
        ):
            raise ValueError(
                "elapsed_time cannot exceed animation duration."
            )

class AnimationAction(str, Enum):
    """Result of submitting an animation intent."""

    STARTED = "started"
    TRANSITIONED = "transitioned"
    IGNORED = "ignored"

class AvatarAnimationMapper:
    """Convert Avatar actions into animation intents.

    The mapper does not make personality or emotional decisions.
    It only translates already-decided Avatar actions into animation
    intent.
    """

    _ACTIVITY_DEFINITIONS = {
        AvatarActivity.IDLE: AnimationDefinition(
            name="idle",
            type=AnimationType.IDLE,
            duration=0.0,
            priority=10,
            loop=True,
        ),
        AvatarActivity.LISTENING: AnimationDefinition(
            name="listen",
            type=AnimationType.LISTEN,
            duration=0.0,
            priority=20,
            loop=True,
        ),
        AvatarActivity.THINKING: AnimationDefinition(
            name="think",
            type=AnimationType.THINK,
            duration=0.0,
            priority=30,
            loop=True,
        ),
        AvatarActivity.TALKING: AnimationDefinition(
            name="talk",
            type=AnimationType.TALK,
            duration=0.0,
            priority=40,
            loop=True,
        ),
        AvatarActivity.REACTING: AnimationDefinition(
            name="react",
            type=AnimationType.REACT,
            duration=0.0,
            priority=50,
            loop=False,
        ),
    }

    _EXPRESSION_DEFINITIONS = {
        AvatarExpression.NEUTRAL: "neutral",
        AvatarExpression.HAPPY: "happy",
        AvatarExpression.SAD: "sad",
        AvatarExpression.ANGRY: "angry",
        AvatarExpression.SURPRISED: "surprised",
        AvatarExpression.FEARFUL: "fearful",
        AvatarExpression.DISGUSTED: "disgusted",
        AvatarExpression.CURIOUS: "curious",
        AvatarExpression.CONCERNED: "concerned",
        AvatarExpression.RELIEVED: "relieved",
    }

    _POSE_DEFINITIONS = {
        AvatarPose.DEFAULT: "default",
        AvatarPose.RELAXED: "relaxed",
        AvatarPose.ATTENTIVE: "attentive",
        AvatarPose.THINKING: "thinking",
        AvatarPose.EXCITED: "excited",
        AvatarPose.SAD: "sad",
    }

    @classmethod
    def from_action(
        cls,
        action: AvatarAction,
    ) -> AnimationIntent | None:
        """Convert one Avatar action into an AnimationIntent."""

        if action.type is AvatarActionType.SET_ACTIVITY:
            activity = action.value
            definition = cls._ACTIVITY_DEFINITIONS.get(activity)

            if definition is None:
                return None

            return AnimationIntent(
                animation=definition,
                source_action=action,
                metadata={"source": "activity", "activity": activity.value},
            )

        if action.type is AvatarActionType.SET_EXPRESSION:
            expression = action.value

            if expression not in cls._EXPRESSION_DEFINITIONS:
                return None

            return AnimationIntent(
                animation=AnimationDefinition(
                    name=f"emotion_{cls._EXPRESSION_DEFINITIONS[expression]}",
                    type=AnimationType.EMOTION,
                    duration=0.5,
                    priority=60,
                    loop=False,
                    metadata={
                        "expression": expression.value,
                    },
                ),
                source_action=action,
                metadata={"source": "expression", "expression": expression.value},
            )

        if action.type is AvatarActionType.SET_POSE:
            pose = action.value

            if pose not in cls._POSE_DEFINITIONS:
                return None

            return AnimationIntent(
                animation=AnimationDefinition(
                    name=f"pose_{cls._POSE_DEFINITIONS[pose]}",
                    type=AnimationType.POSE,
                    duration=0.0,
                    priority=55,
                    loop=True,
                    metadata={
                        "pose": pose.value,
                    },
                ),
                source_action=action,
                metadata={"source": "pose", "pose": pose.value},
            )

        if action.type is AvatarActionType.RESET:
            return AnimationIntent(
                animation=cls._ACTIVITY_DEFINITIONS[AvatarActivity.IDLE],
                source_action=action,
                metadata={"source": "reset"},
            )

        return None

    @classmethod
    def from_actions(
        cls,
        actions: tuple[AvatarAction, ...] | list[AvatarAction],
    ) -> tuple[AnimationIntent, ...]:
        """Convert multiple Avatar actions into animation intents."""

        intents: list[AnimationIntent] = []

        for action in actions:
            intent = cls.from_action(action)
            if intent is not None:
                intents.append(intent)

        return tuple(intents)

class AnimationController:
    """Control technology-independent Avatar animation playback.

    The controller is time-independent. Call update(delta_time) with
    elapsed time supplied by the caller.
    """

    def __init__(self, initial_state: AnimationState | None = None) -> None:
        self._state = initial_state or AnimationState()
        self._transition_target: AnimationDefinition | None = None

    @property
    def state(self) -> AnimationState:
        """Return the current immutable animation state."""

        return self._state

    def _create_transition(
        self,
        current: AnimationDefinition,
        target: AnimationDefinition,
    ) -> AnimationDefinition:
        """Create a technology-independent transition animation."""

        return AnimationDefinition(
            name=f"transition_{current.name}_to_{target.name}",
            type=AnimationType.TRANSITION,
            duration=0.1,
            priority=max(current.priority, target.priority),
            loop=False,
            metadata={
                "from_animation": current.name,
                "to_animation": target.name,
            },
        )
    
    def submit(self, intent: AnimationIntent) -> AnimationAction:
        """Submit an animation intent.

        A new animation can replace the current one when:
        - there is no current animation
        - the current animation has stopped
        - the new animation has equal or higher priority

        A short technology-independent transition is created when an
        active animation is replaced by another animation.
        """

        current = self._state.animation
        if current is None:
            self._start(intent.animation)
            return AnimationAction.STARTED
        if self._state.playback is AnimationPlaybackState.STOPPED:
            self._start(intent.animation)
            return AnimationAction.STARTED
        if (
            intent.animation.priority < current.priority
            and not current.is_transient
        ):
            return AnimationAction.IGNORED

        transition = self._create_transition(
            current=current,
            target=intent.animation,
        )
        self._transition_target = intent.animation
        self._state = AnimationState(
            animation=transition,
            elapsed_time=0.0,
            playback=AnimationPlaybackState.PLAYING,
        )

        return AnimationAction.TRANSITIONED

    def submit_action(self, action: AvatarAction) -> AnimationAction:
        """Convert an Avatar action and submit it."""

        intent = AvatarAnimationMapper.from_action(action)
        if intent is None:
            return AnimationAction.IGNORED

        return self.submit(intent)

    def update(self, delta_time: float) -> AnimationState:
        """Advance animation playback by delta_time seconds."""

        if delta_time < 0.0:
            raise ValueError("delta_time cannot be negative.")

        animation = self._state.animation
        if animation is None:
            return self._state

        if self._state.playback is AnimationPlaybackState.STOPPED:
            return self._state

        elapsed = self._state.elapsed_time + delta_time
        if animation.duration <= 0.0:
            return self._state

        if animation.loop:
            elapsed %= animation.duration
            self._state = AnimationState(
                animation=animation,
                elapsed_time=elapsed,
                playback=AnimationPlaybackState.PLAYING,
            )
            return self._state

        if elapsed >= animation.duration:
            if (
                animation.type is AnimationType.TRANSITION
                and self._transition_target is not None
            ):
                target = self._transition_target
                self._transition_target = None
                self._start(target)
                return self._state

            self._state = AnimationState(
                animation=animation,
                elapsed_time=animation.duration,
                playback=AnimationPlaybackState.STOPPED,
            )
            return self._state

        self._state = AnimationState(
            animation=animation,
            elapsed_time=elapsed,
            playback=AnimationPlaybackState.PLAYING,
        )
        return self._state

    def stop(self) -> AnimationState:
        """Stop the current animation without removing its definition."""

        self._transition_target = None
        
        if self._state.animation is None:
            self._state = AnimationState()
            return self._state

        self._state = AnimationState(
            animation=self._state.animation,
            elapsed_time=self._state.elapsed_time,
            playback=AnimationPlaybackState.STOPPED,
        )

        return self._state

    def reset(self) -> AnimationState:
        """Reset the controller to its initial state."""

        self._transition_target = None
        self._state = AnimationState()
        return self._state

    def _start(self, animation: AnimationDefinition) -> None:
        self._state = AnimationState(
            animation=animation,
            elapsed_time=0.0,
            playback=AnimationPlaybackState.PLAYING,
        )