"""Tests for the 3.5.2 Personality & Behavior system."""

from core.personality import (
    BehaviorContext,
    BehaviorEngine,
    BehaviorType,
    Emotion,
    EmotionState,
    MoodState,
    PersonalityProfile,
    PersonalityState,
    PersonalityTrait,
    ResponseLength,
    SituationTag,
    Tone,
)


def neutral_state() -> PersonalityState:
    """Create a neutral personality state for tests."""

    return PersonalityState(
        emotion=EmotionState(
            emotion=Emotion.NEUTRAL,
            intensity=0.0,
        ),
        mood=MoodState(
            valence=0.0,
            arousal=0.20,
        ),
    )


def test_default_personality_has_all_traits():
    profile = PersonalityProfile()

    for trait in PersonalityTrait:
        assert trait in profile.traits
        assert 0.0 <= profile.get(trait) <= 1.0


def test_personality_trait_can_be_changed_without_mutating_original():
    original = PersonalityProfile()

    modified = original.with_trait(
        PersonalityTrait.HUMOR,
        0.95,
    )

    assert original.get(PersonalityTrait.HUMOR) != 0.95
    assert modified.get(PersonalityTrait.HUMOR) == 0.95


def test_personality_trait_rejects_invalid_value():
    profile = PersonalityProfile()

    try:
        profile.with_trait(
            PersonalityTrait.HUMOR,
            1.5,
        )
        assert False
    except ValueError:
        pass


def test_personality_trait_rejects_non_numeric_value():
    try:
        PersonalityProfile(
            traits={
                PersonalityTrait.HUMOR: "high",
            }
        )
        assert False
    except TypeError:
        pass


def test_sad_user_selects_supportive_behavior():
    engine = BehaviorEngine()

    context = BehaviorContext.from_tags(
        [
            SituationTag.USER_SAD,
        ],
        sensitivity=0.7,
    )

    decision = engine.decide(
        context,
        neutral_state(),
    )

    assert decision.behavior in {
        BehaviorType.SUPPORTIVE,
        BehaviorType.EMPATHETIC,
    }


def test_sensitive_sad_situation_prefers_empathy():
    engine = BehaviorEngine()

    context = BehaviorContext.from_tags(
        [
            SituationTag.USER_SAD,
            SituationTag.SENSITIVE,
        ],
        sensitivity=0.9,
    )

    decision = engine.decide(
        context,
        neutral_state(),
    )

    assert decision.behavior == BehaviorType.EMPATHETIC


def test_disrespect_can_produce_assertive_behavior():
    engine = BehaviorEngine()

    context = BehaviorContext.from_tags(
        [
            SituationTag.DISRESPECT,
        ],
        sensitivity=0.5,
    )

    decision = engine.decide(
        context,
        neutral_state(),
    )

    assert decision.behavior == BehaviorType.ASSERTIVE


def test_repeated_negative_interaction_can_set_boundary():
    engine = BehaviorEngine()

    context = BehaviorContext.from_tags(
        [
            SituationTag.DISRESPECT,
            SituationTag.NEGATIVE_FEEDBACK,
        ],
        sensitivity=0.7,
    )

    decision = engine.decide(
        context,
        neutral_state(),
    )

    assert decision.behavior == BehaviorType.BOUNDARY_SETTING


def test_failure_selects_encouraging_behavior():
    engine = BehaviorEngine()

    context = BehaviorContext.from_tags(
        [
            SituationTag.FAILURE,
        ]
    )

    decision = engine.decide(
        context,
        neutral_state(),
    )

    assert decision.behavior == BehaviorType.ENCOURAGING


def test_good_news_can_select_celebratory_behavior():
    engine = BehaviorEngine()

    context = BehaviorContext.from_tags(
        [
            SituationTag.GOOD_NEWS,
        ]
    )

    state = PersonalityState(
        emotion=EmotionState(
            emotion=Emotion.JOY,
            intensity=0.8,
        ),
        mood=MoodState(
            valence=0.5,
            arousal=0.5,
        ),
    )

    decision = engine.decide(
        context,
        state,
    )

    assert decision.behavior == BehaviorType.CELEBRATORY


def test_casual_context_can_select_playful_behavior():
    personality = PersonalityProfile(
        traits={
            PersonalityTrait.HUMOR: 0.95,
            PersonalityTrait.WARMTH: 0.85,
            PersonalityTrait.OPENNESS: 0.85,
        }
    )

    engine = BehaviorEngine(
        personality=personality,
    )

    context = BehaviorContext.from_tags(
        [
            SituationTag.CASUAL,
        ]
    )

    decision = engine.decide(
        context,
        neutral_state(),
    )

    assert decision.behavior == BehaviorType.PLAYFUL


def test_sensitive_context_suppresses_playful_behavior():
    personality = PersonalityProfile(
        traits={
            PersonalityTrait.HUMOR: 1.0,
            PersonalityTrait.WARMTH: 0.80,
            PersonalityTrait.OPENNESS: 0.80,
        }
    )

    engine = BehaviorEngine(
        personality=personality,
    )

    context = BehaviorContext.from_tags(
        [
            SituationTag.CASUAL,
            SituationTag.SENSITIVE,
        ],
        sensitivity=1.0,
    )

    decision = engine.decide(
        context,
        neutral_state(),
    )

    assert decision.behavior != BehaviorType.PLAYFUL


def test_request_help_prefers_informative_behavior():
    engine = BehaviorEngine()

    context = BehaviorContext.from_tags(
        [
            SituationTag.REQUEST_HELP,
        ]
    )

    decision = engine.decide(
        context,
        neutral_state(),
    )

    assert decision.behavior == BehaviorType.INFORMATIVE


def test_clarification_context_can_select_clarifying_behavior():
    engine = BehaviorEngine()

    context = BehaviorContext.from_tags(
        [
            SituationTag.NEEDS_CLARIFICATION,
        ]
    )

    decision = engine.decide(
        context,
        neutral_state(),
    )

    assert decision.behavior in {
        BehaviorType.CURIOUS,
        BehaviorType.CLARIFYING,
    }


def test_emotion_changes_response_style():
    engine = BehaviorEngine()

    context = BehaviorContext.from_tags(
        [
            SituationTag.REQUEST_HELP,
        ]
    )

    neutral = neutral_state()

    sad = PersonalityState(
        emotion=EmotionState(
            emotion=Emotion.SADNESS,
            intensity=0.9,
        ),
        mood=MoodState(
            valence=-0.4,
            arousal=0.25,
        ),
    )

    neutral_style = engine.response_style(
        context,
        neutral,
    )

    sad_style = engine.response_style(
        context,
        sad,
    )

    assert sad_style.empathy > neutral_style.empathy
    assert sad_style.humor < neutral_style.humor


def test_sad_context_suppresses_humor():
    personality = PersonalityProfile(
        traits={
            PersonalityTrait.HUMOR: 1.0,
            PersonalityTrait.EMPATHY: 0.8,
        }
    )

    engine = BehaviorEngine(
        personality=personality,
    )

    context = BehaviorContext.from_tags(
        [
            SituationTag.USER_SAD,
        ],
        sensitivity=0.8,
    )

    style = engine.response_style(
        context,
        neutral_state(),
    )

    assert style.humor < 0.20


def test_greeting_prefers_short_response():
    engine = BehaviorEngine()

    context = BehaviorContext.from_tags(
        [
            SituationTag.GREETING,
        ]
    )

    style = engine.response_style(
        context,
        neutral_state(),
    )

    assert style.length == ResponseLength.SHORT


def test_supportive_behavior_uses_gentle_tone():
    engine = BehaviorEngine()

    context = BehaviorContext.from_tags(
        [
            SituationTag.USER_SAD,
        ]
    )

    decision = engine.decide(
        context,
        neutral_state(),
    )

    style = engine.response_style(
        context,
        neutral_state(),
        decision,
    )

    assert style.tone == Tone.GENTLE


def test_boundary_behavior_uses_firm_tone():
    engine = BehaviorEngine()

    context = BehaviorContext.from_tags(
        [
            SituationTag.DISRESPECT,
            SituationTag.NEGATIVE_FEEDBACK,
        ]
    )

    state = neutral_state()

    decision = engine.decide(
        context,
        state,
    )

    style = engine.response_style(
        context,
        state,
        decision,
    )

    assert style.tone == Tone.FIRM


def test_behavior_engine_does_not_modify_personality_state():
    engine = BehaviorEngine()

    context = BehaviorContext.from_tags(
        [
            SituationTag.USER_SAD,
        ]
    )

    state = neutral_state()
    before = state.copy()

    engine.decide(
        context,
        state,
    )

    assert state.emotion.emotion == before.emotion.emotion
    assert state.emotion.intensity == before.emotion.intensity
    assert state.mood.valence == before.mood.valence
    assert state.mood.arousal == before.mood.arousal


def test_custom_behavior_rules_can_be_used():
    from core.personality import BehaviorRule

    custom_rule = BehaviorRule(
        behavior=BehaviorType.CELEBRATORY,
        required_tags=frozenset(
            {
                SituationTag.PRAISE.value,
            }
        ),
        trait_weights={
            PersonalityTrait.WARMTH: 1.0,
        },
        priority=100,
        reason="Custom praise behavior.",
    )

    engine = BehaviorEngine(
        rules=[custom_rule],
    )

    context = BehaviorContext.from_tags(
        [
            SituationTag.PRAISE,
        ]
    )

    decision = engine.decide(
        context,
        neutral_state(),
    )

    assert decision.behavior == BehaviorType.CELEBRATORY
    assert decision.priority == 100


def test_different_personalities_can_produce_different_behavior_tendencies():
    humorous = PersonalityProfile(
        traits={
            PersonalityTrait.HUMOR: 1.0,
            PersonalityTrait.WARMTH: 0.9,
        }
    )

    serious = PersonalityProfile(
        traits={
            PersonalityTrait.HUMOR: 0.0,
            PersonalityTrait.WARMTH: 0.4,
        }
    )

    context = BehaviorContext.from_tags(
        [
            SituationTag.CASUAL,
        ]
    )

    humorous_decision = BehaviorEngine(
        personality=humorous,
    ).decide(
        context,
        neutral_state(),
    )

    serious_decision = BehaviorEngine(
        personality=serious,
    ).decide(
        context,
        neutral_state(),
    )

    assert humorous_decision.behavior == BehaviorType.PLAYFUL
    assert serious_decision.behavior != BehaviorType.PLAYFUL