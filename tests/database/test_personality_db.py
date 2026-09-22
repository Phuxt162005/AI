import pytest

from database.models.personality import (
    Emotion,
    Mood,
    Personality,
    Relationship,
)


def test_personality_entity():
    personality = Personality(
        personality_id=None,
        user_id=10,
        name="Assistant",
        speaking_style="friendly",
        traits={"friendly": 0.8},
        behaviors={"greeting": "warm"},
    )

    assert personality.user_id == 10
    assert personality.traits["friendly"] == 0.8


def test_emotion_entity():
    emotion = Emotion(
        emotion_id=None,
        personality_id=1,
        name="happy",
        intensity=0.8,
        valence=0.9,
        context="successful task",
    )

    assert emotion.intensity == 0.8


def test_mood_entity():
    mood = Mood(
        mood_id=None,
        personality_id=1,
        state="calm",
        intensity=0.5,
    )

    assert mood.state == "calm"


def test_relationship_entity():
    relationship = Relationship(
        relationship_id=None,
        personality_id=1,
        target_user_id=10,
        relationship_type="user",
        strength=0.7,
    )

    assert relationship.target_user_id == 10


def test_invalid_personality_user():
    with pytest.raises(ValueError):
        Personality(
            personality_id=None,
            user_id=0,
            name="Assistant",
        )


def test_invalid_emotion_intensity():
    with pytest.raises(ValueError):
        Emotion(
            emotion_id=None,
            personality_id=1,
            name="happy",
            intensity=2.0,
        )