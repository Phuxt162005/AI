"""Personality system package."""

from .emotion import (
    Emotion,
    EmotionEvent,
    EmotionMoodEngine,
    EmotionState,
    MoodState,
    MoodType,
    PersonalityState,
)

from .personality import (
    BehaviorContext,
    BehaviorDecision,
    BehaviorEngine,
    BehaviorRule,
    BehaviorType,
    FormalityLevel,
    PersonalityProfile,
    PersonalityTrait,
    ResponseLength,
    ResponseStyle,
    SituationTag,
    Tone,
    default_behavior_rules,
)

__all__ = [
    "Emotion",
    "EmotionEvent",
    "EmotionMoodEngine",
    "EmotionState",
    "MoodState",
    "MoodType",
    "PersonalityState",
    "BehaviorContext",
    "BehaviorDecision",
    "BehaviorEngine",
    "BehaviorRule",
    "BehaviorType",
    "FormalityLevel",
    "PersonalityProfile",
    "PersonalityTrait",
    "ResponseLength",
    "ResponseStyle",
    "SituationTag",
    "Tone",
    "default_behavior_rules",
]