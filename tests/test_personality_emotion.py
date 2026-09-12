"""Tests for the 3.5.1 Emotion & Mood system."""

from core.personality import (
    Emotion,
    EmotionEvent,
    EmotionMoodEngine,
    MoodType,
)


def test_default_state_is_neutral():
    engine = EmotionMoodEngine()

    state = engine.state

    assert state.emotion.emotion == Emotion.NEUTRAL
    assert state.emotion.intensity == 0.0

    assert state.mood.mood_type == MoodType.NEUTRAL


def test_positive_event_changes_emotion():
    engine = EmotionMoodEngine()

    engine.apply_event(
        EmotionEvent(
            emotion=Emotion.JOY,
            intensity=0.8,
            mood_impact=0.3,
        )
    )

    state = engine.state

    assert state.emotion.emotion == Emotion.JOY
    assert state.emotion.intensity > 0.0
    assert state.mood.valence > 0.0


def test_stronger_event_can_replace_current_emotion():
    engine = EmotionMoodEngine()

    engine.apply_event(
        EmotionEvent(
            emotion=Emotion.JOY,
            intensity=0.8,
        )
    )

    engine.apply_event(
        EmotionEvent(
            emotion=Emotion.ANGER,
            intensity=0.95,
        )
    )

    state = engine.state

    assert state.emotion.emotion == Emotion.ANGER
    assert state.emotion.intensity >= 0.9


def test_weak_event_does_not_always_replace_strong_emotion():
    engine = EmotionMoodEngine()

    engine.apply_event(
        EmotionEvent(
            emotion=Emotion.JOY,
            intensity=0.9,
        )
    )

    engine.apply_event(
        EmotionEvent(
            emotion=Emotion.SADNESS,
            intensity=0.1,
        )
    )

    state = engine.state

    assert state.emotion.intensity > 0.0


def test_repeated_same_emotion_increases_strength():
    engine = EmotionMoodEngine()

    engine.apply_event(
        EmotionEvent(
            emotion=Emotion.JOY,
            intensity=0.4,
        )
    )

    first_intensity = engine.emotion.intensity

    engine.apply_event(
        EmotionEvent(
            emotion=Emotion.JOY,
            intensity=0.4,
        )
    )

    second_intensity = engine.emotion.intensity

    assert second_intensity > first_intensity


def test_emotion_decays_faster_than_mood():
    engine = EmotionMoodEngine(
        emotion_decay_rate=0.40,
        mood_decay_rate=0.05,
    )

    engine.apply_event(
        EmotionEvent(
            emotion=Emotion.JOY,
            intensity=0.9,
            mood_impact=0.5,
        )
    )

    emotion_before = engine.emotion.intensity
    mood_before = engine.mood.valence

    engine.advance_time(1.0)

    emotion_after = engine.emotion.intensity
    mood_after = engine.mood.valence

    emotion_change = emotion_before - emotion_after
    mood_change = mood_before - mood_after

    assert emotion_change > mood_change


def test_emotion_event_can_raise_arousal():
    engine = EmotionMoodEngine()

    initial_arousal = engine.mood.arousal

    engine.apply_event(
        EmotionEvent(
            emotion=Emotion.ANGER,
            intensity=0.9,
            mood_impact=0.5,
        )
    )

    assert engine.mood.arousal > initial_arousal


def test_negative_event_reduces_mood_valence():
    engine = EmotionMoodEngine()

    engine.apply_event(
        EmotionEvent(
            emotion=Emotion.SADNESS,
            intensity=0.8,
            mood_impact=0.5,
        )
    )

    assert engine.mood.valence < 0.0


def test_state_is_returned_as_copy():
    engine = EmotionMoodEngine()

    state = engine.state
    state.emotion.intensity = 1.0

    assert engine.emotion.intensity != 1.0


def test_reset_returns_to_neutral_state():
    engine = EmotionMoodEngine()
    engine.apply_event(
        EmotionEvent(
            emotion=Emotion.ANGER,
            intensity=0.9,
        )
    )

    engine.reset()
    state = engine.state

    assert state.emotion.emotion == Emotion.NEUTRAL
    assert state.emotion.intensity == 0.0
    assert state.mood.mood_type == MoodType.NEUTRAL