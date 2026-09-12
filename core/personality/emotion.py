"""Emotion and mood state system for the AI Personality layer.

This module implements the internal emotional state of the assistant.
It intentionally uses only Python's standard library so that the
core personality logic remains self-built and easy to inspect.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class Emotion(str, Enum):
    """Primary emotional states supported by the assistant."""

    NEUTRAL = "neutral"
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    TRUST = "trust"
    ANTICIPATION = "anticipation"
    CURIOSITY = "curiosity"
    CONCERN = "concern"
    RELIEF = "relief"

class MoodType(str, Enum):
    """Longer-lasting background mood states."""

    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"

@dataclass(frozen=True)
class EmotionProfile:
    """Stable characteristics of one emotion.

    valence:
        How pleasant or unpleasant the emotion is.
        Range: -1.0 to 1.0.
    arousal:
        How activated or energized the emotion is.
        Range: 0.0 to 1.0.
    """
    valence: float
    arousal: float

EMOTION_PROFILES: dict[Emotion, EmotionProfile] = {
    Emotion.NEUTRAL: EmotionProfile(0.0, 0.10),
    Emotion.JOY: EmotionProfile(0.80, 0.70),
    Emotion.SADNESS: EmotionProfile(-0.70, 0.25),
    Emotion.ANGER: EmotionProfile(-0.75, 0.85),
    Emotion.FEAR: EmotionProfile(-0.65, 0.90),
    Emotion.SURPRISE: EmotionProfile(0.00, 0.85),
    Emotion.DISGUST: EmotionProfile(-0.65, 0.65),
    Emotion.TRUST: EmotionProfile(0.60, 0.35),
    Emotion.ANTICIPATION: EmotionProfile(0.35, 0.65),
    Emotion.CURIOSITY: EmotionProfile(0.35, 0.60),
    Emotion.CONCERN: EmotionProfile(-0.35, 0.55),
    Emotion.RELIEF: EmotionProfile(0.65, 0.35),
}

@dataclass
class EmotionState:
    """Current short-term emotional state."""

    emotion: Emotion = Emotion.NEUTRAL
    intensity: float = 0.0

    def __post_init__(self) -> None:
        self.intensity = _clamp(self.intensity, 0.0, 1.0)

    @property
    def valence(self) -> float:
        """Return the emotional pleasantness adjusted by intensity."""

        profile = EMOTION_PROFILES[self.emotion]
        return profile.valence * self.intensity

    @property
    def arousal(self) -> float:
        """Return the emotional activation adjusted by intensity."""

        profile = EMOTION_PROFILES[self.emotion]
        return profile.arousal * self.intensity

    def copy(self) -> "EmotionState":
        """Return an independent copy of the state."""

        return EmotionState(emotion=self.emotion, intensity=self.intensity)

@dataclass
class MoodState:
    """Longer-lasting background mood.

    Mood is represented continuously rather than as a fixed label.
    valence:
        Pleasantness of the current mood, range [-1, 1].
    arousal:
        General activation level, range [0, 1].
    """
    valence: float = 0.0
    arousal: float = 0.20

    def __post_init__(self) -> None:
        self.valence = _clamp(self.valence, -1.0, 1.0)
        self.arousal = _clamp(self.arousal, 0.0, 1.0)

    @property
    def mood_type(self) -> MoodType:
        """Convert continuous mood dimensions into a human-readable label."""

        if self.valence <= -0.60:
            return MoodType.VERY_NEGATIVE

        if self.valence <= -0.20:
            return MoodType.NEGATIVE

        if self.valence < 0.20:
            return MoodType.NEUTRAL

        if self.valence < 0.60:
            return MoodType.POSITIVE

        return MoodType.VERY_POSITIVE

    def copy(self) -> "MoodState":
        """Return an independent copy of the mood."""

        return MoodState(valence=self.valence, arousal=self.arousal)

@dataclass(frozen=True)
class EmotionEvent:
    """An event capable of changing the internal emotional state.

    The event is deliberately independent from NLP or the AI Core.
    Another module can translate a user situation into this event.

    emotion:
        Emotion suggested by the interpreted situation.

    intensity:
        Strength of the emotional stimulus.

    mood_impact:
        How strongly the event should affect longer-term mood.

    arousal:
        Optional explicit activation level of the event.
        If omitted, the emotion's default profile is used.

    source:
        Optional source description for debugging and logging.
    """

    emotion: Emotion
    intensity: float
    mood_impact: float = 0.20
    arousal: Optional[float] = None
    source: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.emotion, Emotion):
            raise TypeError("emotion must be an Emotion.")

        if not 0.0 <= self.intensity <= 1.0:
            raise ValueError("intensity must be between 0.0 and 1.0.")

        if not 0.0 <= self.mood_impact <= 1.0:
            raise ValueError("mood_impact must be between 0.0 and 1.0.")

        if self.arousal is not None and not 0.0 <= self.arousal <= 1.0:
            raise ValueError("arousal must be between 0.0 and 1.0.")

@dataclass
class PersonalityState:
    """Complete internal state exposed by the Personality layer."""

    emotion: EmotionState = field(default_factory=EmotionState)
    mood: MoodState = field(default_factory=MoodState)

    def copy(self) -> "PersonalityState":
        """Return an independent copy of the complete state."""

        return PersonalityState(
            emotion=self.emotion.copy(),
            mood=self.mood.copy(),
        )

class EmotionMoodEngine:
    """Maintain and update the assistant's emotion and mood.

    The engine separates:
        - short-term emotion,
        - longer-term mood,
        - temporal decay.

    This allows the assistant to react strongly to a situation without
    permanently changing its overall personality state.
    """

    def __init__(
        self,
        initial_emotion: Emotion = Emotion.NEUTRAL,
        initial_emotion_intensity: float = 0.0,
        initial_mood_valence: float = 0.0,
        initial_mood_arousal: float = 0.20,
        emotion_decay_rate: float = 0.25,
        mood_decay_rate: float = 0.05,
    ) -> None:
        if not isinstance(initial_emotion, Emotion):
            raise TypeError("initial_emotion must be an Emotion.")

        if not 0.0 <= initial_emotion_intensity <= 1.0:
            raise ValueError("initial_emotion_intensity must be between 0.0 and 1.0.")

        if not 0.0 <= emotion_decay_rate <= 1.0:
            raise ValueError("emotion_decay_rate must be between 0.0 and 1.0.")

        if not 0.0 <= mood_decay_rate <= 1.0:
            raise ValueError("mood_decay_rate must be between 0.0 and 1.0.")

        self._state = PersonalityState(
            emotion=EmotionState(
                emotion=initial_emotion,
                intensity=initial_emotion_intensity,
            ),
            mood=MoodState(
                valence=initial_mood_valence,
                arousal=initial_mood_arousal,
            ),
        )

        self._emotion_decay_rate = emotion_decay_rate
        self._mood_decay_rate = mood_decay_rate

    @property
    def state(self) -> PersonalityState:
        """Return a copy of the current personality state."""

        return self._state.copy()

    @property
    def emotion(self) -> EmotionState:
        """Return the current emotion."""

        return self._state.emotion.copy()

    @property
    def mood(self) -> MoodState:
        """Return the current mood."""

        return self._state.mood.copy()

    def apply_event(self, event: EmotionEvent) -> PersonalityState:
        """Apply an emotional event and return the new state."""

        if not isinstance(event, EmotionEvent):
            raise TypeError("event must be an EmotionEvent.")

        self._update_emotion(event)
        self._update_mood(event)

        return self.state

    def advance_time(self, steps: float = 1.0) -> PersonalityState:
        """Move the internal state forward in time.

        Emotion decays faster than mood.

        ``steps`` is an abstract time unit rather than a wall-clock
        measurement. This keeps the state engine deterministic and easy
        to test.
        """

        if steps < 0.0:
            raise ValueError("steps must not be negative.")

        if steps == 0.0:
            return self.state

        emotion_factor = _decay_factor(self._emotion_decay_rate, steps)
        mood_factor = _decay_factor(self._mood_decay_rate, steps)
        self._state.emotion.intensity *= emotion_factor

        if self._state.emotion.intensity < 0.01:
            self._state.emotion.intensity = 0.0
            if self._state.emotion.emotion != Emotion.NEUTRAL:
                self._state.emotion.emotion = Emotion.NEUTRAL
        self._state.mood.valence *= mood_factor

        neutral_arousal = 0.20
        self._state.mood.arousal = (
            neutral_arousal
            + (self._state.mood.arousal - neutral_arousal) * mood_factor
        )
        self._state.mood.valence = _clamp(
            self._state.mood.valence,
            -1.0,
            1.0,
        )
        self._state.mood.arousal = _clamp(
            self._state.mood.arousal,
            0.0,
            1.0,
        )
        return self.state

    def reset(
        self,
        emotion: Emotion = Emotion.NEUTRAL,
        mood_valence: float = 0.0,
        mood_arousal: float = 0.20,
    ) -> PersonalityState:
        """Reset the current emotional state."""

        if not isinstance(emotion, Emotion):
            raise TypeError("emotion must be an Emotion.")

        self._state = PersonalityState(
            emotion=EmotionState(emotion=emotion, intensity=0.0),
            mood=MoodState(valence=mood_valence, arousal=mood_arousal),
        )
        return self.state

    def _update_emotion(self, event: EmotionEvent) -> None:
        """Update short-term emotion."""

        current = self._state.emotion
        same_emotion = current.emotion == event.emotion

        if same_emotion:
            current.intensity = _clamp(
                current.intensity
                + event.intensity * (1.0 - current.intensity),
                0.0,
                1.0,
            )
            return
        current_strength = current.intensity

        # A strong new event can replace the current emotion.
        # A weak event is blended with the existing state instead.
        replacement_threshold = 0.35

        if event.intensity >= current_strength + replacement_threshold:
            current.emotion = event.emotion
            current.intensity = event.intensity
            return

        new_strength = event.intensity * 0.70
        retained_strength = current_strength * 0.30

        if new_strength >= retained_strength:
            current.emotion = event.emotion
            current.intensity = _clamp(
                max(event.intensity, current_strength * 0.50),
                0.0,
                1.0,
            )
        else:
            current.intensity = _clamp(current_strength * 0.85, 0.0, 1.0)

    def _update_mood(self, event: EmotionEvent) -> None:
        """Update the slower background mood."""

        profile = EMOTION_PROFILES[event.emotion]
        event_valence = profile.valence

        if event.intensity > 0.0:
            event_valence *= event.intensity

        impact = event.mood_impact
        self._state.mood.valence += (event_valence * impact)
        event_arousal = (
            event.arousal
            if event.arousal is not None
            else profile.arousal
        )
        self._state.mood.arousal += (
            (event_arousal - self._state.mood.arousal)
            * impact
        )
        self._state.mood.valence = _clamp(
            self._state.mood.valence,
            -1.0,
            1.0,
        )
        self._state.mood.arousal = _clamp(
            self._state.mood.arousal,
            0.0,
            1.0,
        )

def _clamp(value: float, minimum: float, maximum: float) -> float:
    """Limit a numeric value to a specified range."""

    return max(minimum, min(value, maximum))

def _decay_factor(rate: float, steps: float) -> float:
    """Calculate a deterministic exponential-like decay factor."""

    return (1.0 - rate) ** steps