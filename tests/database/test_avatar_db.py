import pytest

from database.models.avatar import (
    Animation,
    Audio,
    Avatar,
    Expression,
    VisualState,
    Voice,
)


def test_avatar_entity():
    avatar = Avatar(
        avatar_id=None,
        user_id=10,
        name="Assistant Avatar",
        model_reference="models/avatar.vrm",
    )

    assert avatar.user_id == 10
    assert avatar.model_reference == "models/avatar.vrm"


def test_expression_entity():
    expression = Expression(
        expression_id=None,
        avatar_id=1,
        name="happy",
        emotion="happy",
        parameters={"mouth": 0.8},
    )

    assert expression.emotion == "happy"


def test_animation_entity():
    animation = Animation(
        animation_id=None,
        avatar_id=1,
        name="idle",
        intent="idle",
        loop=True,
        duration_ms=1000,
        transition_ms=200,
    )

    assert animation.loop is True
    assert animation.duration_ms == 1000


def test_voice_entity():
    voice = Voice(
        voice_id=None,
        avatar_id=1,
        external_voice_id="voice-01",
        model="tts-model",
        language="vi-VN",
    )

    assert voice.language == "vi-VN"


def test_audio_entity():
    audio = Audio(
        audio_id=None,
        avatar_id=1,
        asset_reference="storage/audio/hello.wav",
        duration_ms=1500,
    )

    assert audio.asset_reference.endswith(".wav")


def test_visual_state_entity():
    state = VisualState(
        visual_state_id=None,
        avatar_id=1,
        expression_id=2,
        animation_id=3,
        pose="talk",
        visible=True,
    )

    assert state.pose == "talk"
    assert state.visible is True


def test_invalid_avatar():
    with pytest.raises(ValueError):
        Avatar(
            avatar_id=None,
            user_id=0,
            name="Avatar",
        )


def test_invalid_audio():
    with pytest.raises(ValueError):
        Audio(
            audio_id=None,
            avatar_id=1,
            asset_reference="",
        )