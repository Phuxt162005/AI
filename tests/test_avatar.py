"""Tests for the technology-independent Avatar subsystem."""

from dataclasses import FrozenInstanceError

import pytest

from core.avatar import (
    AnimationAction,
    AnimationController,
    AnimationPlaybackState,
    AnimationType,
    Avatar,
    AvatarAction,
    AvatarActionType,
    AvatarActivity,
    AvatarAnimationMapper,
    AvatarExpression,
    AvatarMapper,
    AvatarPose,
    AvatarRuntime,
    AvatarRuntimeState,
    AvatarState,
    AvatarVisibility,
    MockAvatarRenderer,
    MockVTuberModel,
    ModelExpression,
    ModelPose,
)
from core.personality import (
    Emotion,
    EmotionState,
    MoodState,
    PersonalityState,
)


# ---------------------------------------------------------------------------
# Avatar State
# ---------------------------------------------------------------------------


def test_avatar_state_defaults():
    state = AvatarState()

    assert state.activity is AvatarActivity.IDLE
    assert state.expression is AvatarExpression.NEUTRAL
    assert state.pose is AvatarPose.DEFAULT
    assert state.visibility is AvatarVisibility.VISIBLE
    assert state.parameters == {}


def test_avatar_state_is_immutable():
    state = AvatarState()

    with pytest.raises(FrozenInstanceError):
        state.activity = AvatarActivity.TALKING


def test_avatar_state_parameter_range():
    state = AvatarState()

    with pytest.raises(ValueError):
        state.with_parameter("mouth_open", 1.1)

    with pytest.raises(ValueError):
        state.with_parameter("mouth_open", -1.1)


def test_avatar_state_with_methods_create_new_state():
    original = AvatarState()

    updated = original.with_expression(AvatarExpression.HAPPY)

    assert original.expression is AvatarExpression.NEUTRAL
    assert updated.expression is AvatarExpression.HAPPY
    assert updated.activity is original.activity
    assert updated.pose is original.pose
    assert updated.visibility is original.visibility


@pytest.mark.parametrize(
    "action",
    [
        AvatarAction(
            type=AvatarActionType.SET_ACTIVITY,
            value=AvatarActivity.TALKING,
        ),
        AvatarAction(
            type=AvatarActionType.SET_EXPRESSION,
            value=AvatarExpression.HAPPY,
        ),
        AvatarAction(
            type=AvatarActionType.SET_POSE,
            value=AvatarPose.EXCITED,
        ),
        AvatarAction(
            type=AvatarActionType.SET_VISIBILITY,
            value=AvatarVisibility.HIDDEN,
        ),
        AvatarAction(
            type=AvatarActionType.SET_PARAMETER,
            parameter_name="mouth_open",
            value=0.5,
        ),
        AvatarAction(type=AvatarActionType.RESET),
    ],
)
def test_avatar_accepts_all_action_types(action):
    avatar = Avatar()

    state = avatar.apply(action)

    assert isinstance(state, AvatarState)


def test_avatar_action_validation():
    with pytest.raises(TypeError):
        AvatarAction(
            type=AvatarActionType.SET_EXPRESSION,
            value="happy",
        )

    with pytest.raises(ValueError):
        AvatarAction(
            type=AvatarActionType.SET_PARAMETER,
            value=0.5,
        )

    with pytest.raises(ValueError):
        AvatarAction(
            type=AvatarActionType.SET_PARAMETER,
            parameter_name="mouth_open",
            value=2.0,
        )


def test_avatar_reset():
    avatar = Avatar()

    avatar.set_activity(AvatarActivity.TALKING)
    avatar.set_expression(AvatarExpression.HAPPY)
    avatar.set_pose(AvatarPose.EXCITED)
    avatar.set_visibility(AvatarVisibility.HIDDEN)
    avatar.set_parameter("mouth_open", 0.75)

    state = avatar.reset()

    assert state == AvatarState()


# ---------------------------------------------------------------------------
# Avatar Mapping
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "emotion, expected_expression",
    [
        (Emotion.NEUTRAL, AvatarExpression.NEUTRAL),
        (Emotion.JOY, AvatarExpression.HAPPY),
        (Emotion.SADNESS, AvatarExpression.SAD),
        (Emotion.ANGER, AvatarExpression.ANGRY),
        (Emotion.FEAR, AvatarExpression.FEARFUL),
        (Emotion.SURPRISE, AvatarExpression.SURPRISED),
        (Emotion.DISGUST, AvatarExpression.DISGUSTED),
        (Emotion.TRUST, AvatarExpression.NEUTRAL),
        (Emotion.ANTICIPATION, AvatarExpression.CURIOUS),
        (Emotion.CURIOSITY, AvatarExpression.CURIOUS),
        (Emotion.CONCERN, AvatarExpression.CONCERNED),
        (Emotion.RELIEF, AvatarExpression.RELIEVED),
    ],
)
def test_avatar_mapper_emotion_to_expression(
    emotion,
    expected_expression,
):
    personality_state = PersonalityState(
        emotion=EmotionState(
            emotion=emotion,
            intensity=1.0,
        ),
        mood=MoodState(
            valence=0.0,
            arousal=0.5,
        ),
    )

    result = AvatarMapper().map(personality_state)

    assert result.expression is expected_expression


def test_avatar_mapper_default_activity_and_pose():
    personality_state = PersonalityState(
        emotion=EmotionState(
            emotion=Emotion.JOY,
            intensity=0.8,
        ),
        mood=MoodState(
            valence=0.5,
            arousal=0.6,
        ),
    )

    result = AvatarMapper().map(personality_state)

    assert result.activity is AvatarActivity.IDLE
    assert result.pose is AvatarPose.DEFAULT


def test_avatar_mapper_expression_intensity_is_normalized():
    personality_state = PersonalityState(
        emotion=EmotionState(
            emotion=Emotion.JOY,
            intensity=1.0,
        ),
        mood=MoodState(
            valence=0.5,
            arousal=1.0,
        ),
    )

    result = AvatarMapper().map(personality_state)

    assert 0.0 <= result.expression_intensity <= 1.0

    intensity_actions = [
        action
        for action in result.actions
        if action.type is AvatarActionType.SET_PARAMETER
    ]

    assert len(intensity_actions) == 1
    assert intensity_actions[0].parameter_name == "expression_intensity"


# ---------------------------------------------------------------------------
# Animation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "activity, expected_animation, expected_type",
    [
        (AvatarActivity.IDLE, "idle", AnimationType.IDLE),
        (AvatarActivity.LISTENING, "listen", AnimationType.LISTEN),
        (AvatarActivity.THINKING, "think", AnimationType.THINK),
        (AvatarActivity.TALKING, "talk", AnimationType.TALK),
        (AvatarActivity.REACTING, "react", AnimationType.REACT),
    ],
)
def test_animation_mapper_activity(
    activity,
    expected_animation,
    expected_type,
):
    action = AvatarAction(
        type=AvatarActionType.SET_ACTIVITY,
        value=activity,
    )

    intent = AvatarAnimationMapper.from_action(action)

    assert intent is not None
    assert intent.animation.name == expected_animation
    assert intent.animation.type is expected_type
    assert intent.source_action == action


def test_animation_mapper_expression():
    action = AvatarAction(
        type=AvatarActionType.SET_EXPRESSION,
        value=AvatarExpression.HAPPY,
    )

    intent = AvatarAnimationMapper.from_action(action)

    assert intent is not None
    assert intent.animation.name == "emotion_happy"
    assert intent.animation.type is AnimationType.EMOTION
    assert intent.animation.duration == 0.5
    assert intent.animation.priority == 60
    assert intent.animation.loop is False


def test_animation_mapper_pose():
    action = AvatarAction(
        type=AvatarActionType.SET_POSE,
        value=AvatarPose.EXCITED,
    )

    intent = AvatarAnimationMapper.from_action(action)

    assert intent is not None
    assert intent.animation.name == "pose_excited"
    assert intent.animation.type is AnimationType.POSE
    assert intent.animation.loop is True


def test_animation_mapper_ignores_parameter_action():
    action = AvatarAction(
        type=AvatarActionType.SET_PARAMETER,
        parameter_name="mouth_open",
        value=0.5,
    )

    assert AvatarAnimationMapper.from_action(action) is None


def test_animation_controller_starts_animation():
    controller = AnimationController()

    action = AvatarAction(
        type=AvatarActionType.SET_ACTIVITY,
        value=AvatarActivity.IDLE,
    )

    result = controller.submit_action(action)

    assert result is AnimationAction.STARTED
    assert controller.state.animation is not None
    assert controller.state.animation.name == "idle"
    assert controller.state.playback is AnimationPlaybackState.PLAYING


def test_animation_controller_transition():
    controller = AnimationController()

    controller.submit_action(
        AvatarAction(
            type=AvatarActionType.SET_ACTIVITY,
            value=AvatarActivity.IDLE,
        )
    )

    result = controller.submit_action(
        AvatarAction(
            type=AvatarActionType.SET_ACTIVITY,
            value=AvatarActivity.TALKING,
        )
    )

    assert result is AnimationAction.TRANSITIONED
    assert controller.state.animation is not None
    assert controller.state.animation.type is AnimationType.TRANSITION

    controller.update(0.1)

    assert controller.state.animation is not None
    assert controller.state.animation.name == "talk"


def test_animation_controller_loop():
    controller = AnimationController()

    controller.submit_action(
        AvatarAction(
            type=AvatarActionType.SET_ACTIVITY,
            value=AvatarActivity.IDLE,
        )
    )

    controller.update(1.0)

    assert controller.state.playback is AnimationPlaybackState.PLAYING
    assert controller.state.animation.name == "idle"


def test_animation_controller_transient_animation_finishes():
    controller = AnimationController()

    controller.submit_action(
        AvatarAction(
            type=AvatarActionType.SET_EXPRESSION,
            value=AvatarExpression.HAPPY,
        )
    )

    controller.update(0.5)

    assert controller.state.playback is AnimationPlaybackState.STOPPED
    assert controller.state.elapsed_time == 0.5


def test_animation_controller_rejects_negative_delta():
    controller = AnimationController()

    with pytest.raises(ValueError):
        controller.update(-0.1)


# ---------------------------------------------------------------------------
# VTuber Model
# ---------------------------------------------------------------------------


def test_mock_model_lifecycle():
    model = MockVTuberModel()

    assert model.is_loaded is False

    model.load()

    assert model.is_loaded is True

    model.unload()

    assert model.is_loaded is False


def test_mock_model_rejects_mutation_before_load():
    model = MockVTuberModel()

    with pytest.raises(RuntimeError):
        model.set_expression(ModelExpression.HAPPY)

    with pytest.raises(RuntimeError):
        model.set_pose(ModelPose.EXCITED)

    with pytest.raises(RuntimeError):
        model.set_visibility(False)

    with pytest.raises(RuntimeError):
        model.set_parameter("mouth_open", 0.5)


def test_mock_model_expression_pose_visibility():
    model = MockVTuberModel()
    model.load()

    model.set_expression(ModelExpression.HAPPY)
    model.set_pose(ModelPose.EXCITED)
    model.set_visibility(False)

    snapshot = model.snapshot

    assert snapshot.expression is ModelExpression.HAPPY
    assert snapshot.pose is ModelPose.EXCITED
    assert snapshot.visible is False
    assert snapshot.loaded is True


def test_mock_model_parameter_range():
    model = MockVTuberModel()
    model.load()

    model.set_parameter("mouth_open", 2.0)

    assert model.snapshot.parameters["mouth_open"] == 1.0

    model.set_parameter("mouth_open", -2.0)

    assert model.snapshot.parameters["mouth_open"] == -1.0


def test_mock_model_unknown_parameter():
    model = MockVTuberModel()
    model.load()

    with pytest.raises(KeyError):
        model.set_parameter("unknown_parameter", 0.5)


def test_mock_model_reset():
    model = MockVTuberModel()
    model.load()

    model.set_expression(ModelExpression.HAPPY)
    model.set_pose(ModelPose.EXCITED)
    model.set_visibility(False)
    model.set_parameter("mouth_open", 0.8)

    model.reset()

    snapshot = model.snapshot

    assert snapshot.expression is ModelExpression.NEUTRAL
    assert snapshot.pose is ModelPose.DEFAULT
    assert snapshot.visible is True
    assert snapshot.parameters["mouth_open"] == 0.0


# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------


def test_mock_renderer_lifecycle():
    renderer = MockAvatarRenderer()

    assert renderer.is_initialized is False

    renderer.initialize()

    assert renderer.is_initialized is True

    renderer.shutdown()

    assert renderer.is_initialized is False


def test_mock_renderer_render():
    model = MockVTuberModel()
    model.load()

    renderer = MockAvatarRenderer()
    renderer.initialize()

    renderer.render(model.snapshot)

    assert renderer.render_count == 1
    assert renderer.last_rendered_model == model.snapshot


def test_mock_renderer_requires_initialization():
    model = MockVTuberModel()
    model.load()

    renderer = MockAvatarRenderer()

    with pytest.raises(RuntimeError):
        renderer.render(model.snapshot)


# ---------------------------------------------------------------------------
# Avatar Runtime
# ---------------------------------------------------------------------------


@pytest.fixture
def runtime_components():
    avatar = Avatar()
    model = MockVTuberModel()
    renderer = MockAvatarRenderer()

    runtime = AvatarRuntime(
        avatar=avatar,
        model=model,
        renderer=renderer,
    )

    return runtime, avatar, model, renderer


def test_runtime_initial_state(runtime_components):
    runtime, _, model, renderer = runtime_components

    assert runtime.state is AvatarRuntimeState.STOPPED
    assert runtime.is_running is False
    assert model.is_loaded is False
    assert renderer.is_initialized is False


def test_runtime_start(runtime_components):
    runtime, _, model, renderer = runtime_components

    runtime.start()

    assert runtime.state is AvatarRuntimeState.RUNNING
    assert runtime.is_running is True
    assert model.is_loaded is True
    assert renderer.is_initialized is True


def test_runtime_start_is_idempotent(runtime_components):
    runtime, _, model, renderer = runtime_components

    runtime.start()
    runtime.start()

    assert runtime.is_running is True
    assert model.is_loaded is True
    assert renderer.is_initialized is True


def test_runtime_stop(runtime_components):
    runtime, _, model, renderer = runtime_components

    runtime.start()
    runtime.stop()

    assert runtime.state is AvatarRuntimeState.STOPPED
    assert runtime.is_running is False
    assert model.is_loaded is False
    assert renderer.is_initialized is False


def test_runtime_stop_is_idempotent(runtime_components):
    runtime, _, model, renderer = runtime_components

    runtime.stop()

    assert runtime.state is AvatarRuntimeState.STOPPED
    assert model.is_loaded is False
    assert renderer.is_initialized is False


def test_runtime_rejects_apply_before_start(runtime_components):
    runtime, _, _, _ = runtime_components

    action = AvatarAction(
        type=AvatarActionType.SET_EXPRESSION,
        value=AvatarExpression.HAPPY,
    )

    with pytest.raises(RuntimeError):
        runtime.apply(action)


def test_runtime_rejects_update_before_start(runtime_components):
    runtime, _, _, _ = runtime_components

    with pytest.raises(RuntimeError):
        runtime.update(0.1)


def test_runtime_rejects_render_before_start(runtime_components):
    runtime, _, _, _ = runtime_components

    with pytest.raises(RuntimeError):
        runtime.render()


def test_runtime_apply_synchronizes_avatar_and_model(runtime_components):
    runtime, avatar, model, _ = runtime_components

    runtime.start()

    action = AvatarAction(
        type=AvatarActionType.SET_EXPRESSION,
        value=AvatarExpression.HAPPY,
    )

    state = runtime.apply(action)

    assert state.expression is AvatarExpression.HAPPY
    assert avatar.state.expression is AvatarExpression.HAPPY
    assert model.snapshot.expression is ModelExpression.HAPPY


def test_runtime_apply_synchronizes_pose(runtime_components):
    runtime, _, model, _ = runtime_components

    runtime.start()

    runtime.apply(
        AvatarAction(
            type=AvatarActionType.SET_POSE,
            value=AvatarPose.EXCITED,
        )
    )

    assert model.snapshot.pose is ModelPose.EXCITED


def test_runtime_apply_synchronizes_visibility(runtime_components):
    runtime, _, model, _ = runtime_components

    runtime.start()

    runtime.apply(
        AvatarAction(
            type=AvatarActionType.SET_VISIBILITY,
            value=AvatarVisibility.HIDDEN,
        )
    )

    assert model.snapshot.visible is False


def test_runtime_apply_synchronizes_supported_parameter(runtime_components):
    runtime, _, model, _ = runtime_components

    runtime.start()

    runtime.apply(
        AvatarAction(
            type=AvatarActionType.SET_PARAMETER,
            parameter_name="mouth_open",
            value=0.5,
        )
    )

    assert model.snapshot.parameters["mouth_open"] == pytest.approx(0.75)


def test_runtime_ignores_unsupported_avatar_parameter(runtime_components):
    runtime, _, model, _ = runtime_components

    runtime.start()

    runtime.apply(
        AvatarAction(
            type=AvatarActionType.SET_PARAMETER,
            parameter_name="expression_intensity",
            value=1.0,
        )
    )

    # expression_intensity is an Avatar-level parameter but is not
    # part of the MockVTuberModel parameter set.
    assert "expression_intensity" not in model.snapshot.parameters


def test_runtime_update_delegates_to_animation(runtime_components):
    runtime, _, _, _ = runtime_components

    runtime.start()

    runtime.apply(
        AvatarAction(
            type=AvatarActionType.SET_EXPRESSION,
            value=AvatarExpression.HAPPY,
        )
    )

    before = runtime.animation_controller.state.elapsed_time

    runtime.update(0.1)

    after = runtime.animation_controller.state.elapsed_time

    assert after > before


def test_runtime_rejects_negative_update(runtime_components):
    runtime, _, _, _ = runtime_components

    runtime.start()

    with pytest.raises(ValueError):
        runtime.update(-0.1)


def test_runtime_render(runtime_components):
    runtime, _, model, renderer = runtime_components

    runtime.start()

    runtime.apply(
        AvatarAction(
            type=AvatarActionType.SET_EXPRESSION,
            value=AvatarExpression.HAPPY,
        )
    )

    runtime.render()

    assert renderer.render_count == 1
    assert renderer.last_rendered_model == model.snapshot


def test_runtime_reset(runtime_components):
    runtime, avatar, model, renderer = runtime_components

    runtime.start()

    runtime.apply(
        AvatarAction(
            type=AvatarActionType.SET_EXPRESSION,
            value=AvatarExpression.HAPPY,
        )
    )
    runtime.apply(
        AvatarAction(
            type=AvatarActionType.SET_POSE,
            value=AvatarPose.EXCITED,
        )
    )
    runtime.apply(
        AvatarAction(
            type=AvatarActionType.SET_VISIBILITY,
            value=AvatarVisibility.HIDDEN,
        )
    )
    runtime.apply(
        AvatarAction(
            type=AvatarActionType.SET_PARAMETER,
            parameter_name="mouth_open",
            value=0.8,
        )
    )

    runtime.reset()

    assert avatar.state == AvatarState()

    assert model.snapshot.expression is ModelExpression.NEUTRAL
    assert model.snapshot.pose is ModelPose.DEFAULT
    assert model.snapshot.visible is True
    assert model.snapshot.parameters["mouth_open"] == 0.0

    assert runtime.animation_controller.state.animation is None
    assert renderer.is_initialized is True
    assert model.is_loaded is True


def test_runtime_stop_resets_animation(runtime_components):
    runtime, _, _, _ = runtime_components

    runtime.start()

    runtime.apply(
        AvatarAction(
            type=AvatarActionType.SET_EXPRESSION,
            value=AvatarExpression.HAPPY,
        )
    )

    assert runtime.animation_controller.state.animation is not None

    runtime.stop()

    assert runtime.animation_controller.state.animation is None
    assert runtime.animation_controller.state.playback is AnimationPlaybackState.STOPPED


# ---------------------------------------------------------------------------
# End-to-end integration
# ---------------------------------------------------------------------------


def test_personality_to_avatar_to_model_to_renderer(runtime_components):
    runtime, avatar, model, renderer = runtime_components

    personality_state = PersonalityState(
        emotion=EmotionState(
            emotion=Emotion.JOY,
            intensity=0.9,
        ),
        mood=MoodState(
            valence=0.6,
            arousal=0.7,
        ),
    )

    mapping = AvatarMapper().map(personality_state)

    runtime.start()

    for action in mapping.actions:
        runtime.apply(action)

    runtime.render()

    # Personality → Avatar mapping
    assert mapping.expression is AvatarExpression.HAPPY

    # Avatar state
    assert avatar.state.expression is AvatarExpression.HAPPY

    # Avatar → Model
    assert model.snapshot.expression is ModelExpression.HAPPY

    # Avatar → Animation
    assert runtime.animation_controller.state.animation is not None

    # Model → Renderer
    assert renderer.render_count == 1
    assert renderer.last_rendered_model == model.snapshot


def test_full_avatar_reset_after_end_to_end_flow(runtime_components):
    runtime, avatar, model, renderer = runtime_components

    personality_state = PersonalityState(
        emotion=EmotionState(
            emotion=Emotion.SADNESS,
            intensity=0.8,
        ),
        mood=MoodState(
            valence=-0.7,
            arousal=0.4,
        ),
    )

    mapping = AvatarMapper().map(personality_state)

    runtime.start()

    for action in mapping.actions:
        runtime.apply(action)

    runtime.render()

    runtime.reset()

    assert avatar.state == AvatarState()
    assert model.snapshot.expression is ModelExpression.NEUTRAL
    assert model.snapshot.pose is ModelPose.DEFAULT
    assert model.snapshot.visible is True
    assert runtime.animation_controller.state.animation is None

    runtime.render()

    assert renderer.render_count == 2