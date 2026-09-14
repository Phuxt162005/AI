"""Mapping Personality state to technology-independent Avatar actions.

This module translates emotion, mood, behavior and response style
into Avatar actions.

It does not generate natural-language responses, perform reasoning,
or depend on a specific VTuber model or renderer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from core.personality import (
    BehaviorDecision,
    BehaviorType,
    EmotionState,
    MoodState,
    PersonalityState,
    ResponseStyle,
    Tone,
)

from .state import (
    AvatarAction,
    AvatarActionType,
    AvatarActivity,
    AvatarExpression,
    AvatarPose,
)

@dataclass(frozen=True)
class AvatarMappingResult:
    """Result produced by the Avatar mapping layer.
    The result contains only technology-independent Avatar actions.
    """

    actions: tuple[AvatarAction, ...] = field(default_factory=tuple)
    expression: AvatarExpression = AvatarExpression.NEUTRAL
    activity: AvatarActivity = AvatarActivity.IDLE
    pose: AvatarPose = AvatarPose.DEFAULT
    expression_intensity: float = 0.0
    notes: tuple[str, ...] = field(default_factory=tuple)
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not 0.0 <= self.expression_intensity <= 1.0:
            raise ValueError("expression_intensity must be between 0.0 and 1.0.")

        object.__setattr__(self,"actions", tuple(self.actions))
        object.__setattr__(self, "notes", tuple(str(note) for note in self.notes))
        object.__setattr__(self, "metadata", dict(self.metadata))

class AvatarMapper:
    """Translate Personality state into Avatar state/actions.

    The mapper is deterministic. The same Personality input produces
    the same Avatar mapping result.

    Personality remains the source of behavioral decisions.
    AvatarMapper only translates those decisions into visual intent.
    """

    def map(
        self,
        personality_state: PersonalityState,
        behavior: BehaviorDecision | None = None,
        response_style: ResponseStyle | None = None,
    ) -> AvatarMappingResult:
        """Map Personality state to Avatar actions."""

        expression = self._map_emotion_to_expression(personality_state.emotion)
        activity = self._map_behavior_to_activity(behavior)
        pose = self._map_behavior_and_mood_to_pose(behavior=behavior, mood=personality_state.mood)
        expression_intensity = self._calculate_expression_intensity(
            emotion=personality_state.emotion,
            mood=personality_state.mood,
            response_style=response_style,
        )
        actions = (
            AvatarAction(
                type=AvatarActionType.SET_EXPRESSION,
                value=expression,
            ),
            AvatarAction(
                type=AvatarActionType.SET_ACTIVITY,
                value=activity,
            ),
            AvatarAction(
                type=AvatarActionType.SET_POSE,
                value=pose,
            ),
            AvatarAction(
                type=AvatarActionType.SET_PARAMETER,
                parameter_name="expression_intensity",
                value=expression_intensity,
            ),
        )
        notes = self._build_notes(
            personality_state=personality_state,
            behavior=behavior,
            response_style=response_style,
            expression=expression,
            activity=activity,
            pose=pose,
        )

        return AvatarMappingResult(
            actions=actions,
            expression=expression,
            activity=activity,
            pose=pose,
            expression_intensity=expression_intensity,
            notes=notes,
            metadata={
                "emotion": personality_state.emotion.emotion.value,
                "emotion_intensity": personality_state.emotion.intensity,
                "mood_type": personality_state.mood.mood_type.value,
                "mood_valence": personality_state.mood.valence,
                "mood_arousal": personality_state.mood.arousal,
                "behavior": (
                    behavior.behavior.value
                    if behavior is not None
                    else None
                ),
                "tone": (
                    response_style.tone.value
                    if response_style is not None
                    else None
                ),
            },
        )

    @staticmethod
    def _map_emotion_to_expression(emotion: EmotionState) -> AvatarExpression:
        """Map a Personality emotion to an Avatar expression."""

        mapping = {
            "neutral": AvatarExpression.NEUTRAL,
            "joy": AvatarExpression.HAPPY,
            "sadness": AvatarExpression.SAD,
            "anger": AvatarExpression.ANGRY,
            "fear": AvatarExpression.FEARFUL,
            "surprise": AvatarExpression.SURPRISED,
            "disgust": AvatarExpression.DISGUSTED,
            "trust": AvatarExpression.NEUTRAL,
            "anticipation": AvatarExpression.CURIOUS,
            "curiosity": AvatarExpression.CURIOUS,
            "concern": AvatarExpression.CONCERNED,
            "relief": AvatarExpression.RELIEVED,
        }

        return mapping.get(emotion.emotion.value, AvatarExpression.NEUTRAL)

    @staticmethod
    def _map_behavior_to_activity(behavior: BehaviorDecision | None) -> AvatarActivity:
        """Map Personality behavior to Avatar activity."""

        if behavior is None:
            return AvatarActivity.IDLE

        mapping = {
            BehaviorType.NEUTRAL: AvatarActivity.IDLE,
            BehaviorType.SUPPORTIVE: AvatarActivity.REACTING,
            BehaviorType.EMPATHETIC: AvatarActivity.REACTING,
            BehaviorType.ENCOURAGING: AvatarActivity.REACTING,
            BehaviorType.PLAYFUL: AvatarActivity.REACTING,
            BehaviorType.CURIOUS: AvatarActivity.THINKING,
            BehaviorType.INFORMATIVE: AvatarActivity.TALKING,
            BehaviorType.CLARIFYING: AvatarActivity.TALKING,
            BehaviorType.CALM: AvatarActivity.IDLE,
            BehaviorType.ASSERTIVE: AvatarActivity.TALKING,
            BehaviorType.CAUTIOUS: AvatarActivity.THINKING,
            BehaviorType.APOLOGETIC: AvatarActivity.REACTING,
            BehaviorType.CELEBRATORY: AvatarActivity.REACTING,
            BehaviorType.BOUNDARY_SETTING: AvatarActivity.TALKING,
        }

        return mapping.get(behavior.behavior, AvatarActivity.IDLE)

    @staticmethod
    def _map_behavior_and_mood_to_pose(behavior: BehaviorDecision | None, mood: MoodState) -> AvatarPose:
        """Map behavior and mood into a high-level Avatar pose."""

        if behavior is not None:
            behavior_to_pose = {
                BehaviorType.PLAYFUL: AvatarPose.EXCITED,
                BehaviorType.CELEBRATORY: AvatarPose.EXCITED,
                BehaviorType.ENCOURAGING: AvatarPose.ATTENTIVE,
                BehaviorType.SUPPORTIVE: AvatarPose.RELAXED,
                BehaviorType.EMPATHETIC: AvatarPose.RELAXED,
                BehaviorType.CALM: AvatarPose.RELAXED,
                BehaviorType.CURIOUS: AvatarPose.THINKING,
                BehaviorType.CAUTIOUS: AvatarPose.THINKING,
                BehaviorType.INFORMATIVE: AvatarPose.ATTENTIVE,
                BehaviorType.CLARIFYING: AvatarPose.ATTENTIVE,
                BehaviorType.ASSERTIVE: AvatarPose.ATTENTIVE,
                BehaviorType.BOUNDARY_SETTING: AvatarPose.ATTENTIVE,
                BehaviorType.APOLOGETIC: AvatarPose.RELAXED,
                BehaviorType.NEUTRAL: AvatarPose.DEFAULT,
            }

            if behavior.behavior in behavior_to_pose:
                return behavior_to_pose[behavior.behavior]

        if mood.valence < -0.5:
            return AvatarPose.SAD
        if mood.arousal > 0.7 and mood.valence > 0.3:
            return AvatarPose.EXCITED
        if mood.arousal < 0.3:
            return AvatarPose.RELAXED

        return AvatarPose.DEFAULT

    @staticmethod
    def _calculate_expression_intensity(
        emotion: EmotionState,
        mood: MoodState,
        response_style: ResponseStyle | None,
    ) -> float:
        """Calculate normalized visual expression intensity."""

        intensity = emotion.intensity
        # Mood arousal can slightly strengthen visual expression.
        intensity = intensity * (0.75 + 0.25 * mood.arousal)

        if response_style is not None:
            # Empathy/warmth should not create a new emotion.
            # They only slightly influence how strongly the existing
            # emotion is presented.
            style_factor = (
                0.9
                + 0.05 * response_style.warmth
                + 0.05 * response_style.empathy
            )
            intensity *= style_factor

        return max(0.0, min(1.0, intensity))

    @staticmethod
    def _build_notes(
        personality_state: PersonalityState,
        behavior: BehaviorDecision | None,
        response_style: ResponseStyle | None,
        expression: AvatarExpression,
        activity: AvatarActivity,
        pose: AvatarPose,
    ) -> tuple[str, ...]:
        """Build human-readable mapping information for observability."""

        notes = [
            (
                f"emotion={personality_state.emotion.emotion.value}"
                f" mapped to expression={expression.value}"
            ),
            (
                f"activity={activity.value}, "
                f"pose={pose.value}"
            ),
        ]

        if behavior is not None:
            notes.append(f"behavior={behavior.behavior.value}")

        if response_style is not None:
            notes.append(f"tone={response_style.tone.value}")

        return tuple(notes)