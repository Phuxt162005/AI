"""Tests for the 3.5.3 Context-aware Response system."""

from core.personality import (
    BehaviorContext,
    BehaviorEngine,
    BehaviorType,
    ContextAwareResponder,
    Emotion,
    EmotionState,
    FormalityLevel,
    MemoryContext,
    MoodState,
    PersonalityProfile,
    PersonalityState,
    PersonalityTrait,
    ResponseLength,
    SituationTag,
    Tone,
    ConversationContext,
)


def neutral_state() -> PersonalityState:
    """Create a neutral personality state."""

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


def test_memory_context_can_store_relevant_information():
    memory = MemoryContext.from_topics(
        [
            "machine learning",
            "project",
        ],
        has_relevant_memory=True,
        relationship_familiarity=0.8,
    )

    assert memory.has_relevant_memory is True
    assert memory.has_topic("machine learning")
    assert memory.has_topic("PROJECT")
    assert memory.relationship_familiarity == 0.8


def test_memory_context_rejects_invalid_familiarity():
    try:
        MemoryContext(
            relationship_familiarity=1.5,
        )
        assert False
    except ValueError:
        pass


def test_conversation_context_normalizes_topic():
    behavior_context = BehaviorContext.from_tags(
        [
            SituationTag.CASUAL,
        ]
    )

    context = ConversationContext(
        behavior_context=behavior_context,
        topic="  Machine Learning  ",
    )

    assert context.topic == "machine learning"


def test_context_aware_responder_builds_response_plan():
    responder = ContextAwareResponder()

    behavior_context = BehaviorContext.from_tags(
        [
            SituationTag.REQUEST_HELP,
        ]
    )

    context = ConversationContext(
        behavior_context=behavior_context,
        topic="python",
    )

    plan = responder.build_plan(
        context,
        neutral_state(),
    )

    assert plan.behavior.behavior == BehaviorType.INFORMATIVE
    assert plan.topic == "python"
    assert plan.style.length == ResponseLength.DETAILED
    assert 0.0 <= plan.confidence <= 1.0


def test_response_plan_contains_context_information():
    responder = ContextAwareResponder()

    behavior_context = BehaviorContext.from_tags(
        [
            SituationTag.USER_SAD,
            SituationTag.SENSITIVE,
        ],
        sensitivity=0.9,
    )

    context = ConversationContext(
        behavior_context=behavior_context,
        topic="study",
    )

    plan = responder.build_plan(
        context,
        neutral_state(),
    )

    assert SituationTag.USER_SAD.value in plan.context_tags
    assert SituationTag.SENSITIVE.value in plan.context_tags
    assert plan.topic == "study"


def test_memory_can_supply_explicit_response_preferences():
    responder = ContextAwareResponder()

    behavior_context = BehaviorContext.from_tags(
        [
            SituationTag.REQUEST_HELP,
        ]
    )

    memory = MemoryContext(
        has_relevant_memory=True,
        preferred_formality=FormalityLevel.CASUAL,
        preferred_length=ResponseLength.SHORT,
        preferred_tone=Tone.WARM,
    )

    context = ConversationContext(
        behavior_context=behavior_context,
        memory=memory,
    )

    plan = responder.build_plan(
        context,
        neutral_state(),
    )

    assert plan.memory_used is True
    assert plan.has_relevant_memory is True
    assert plan.style.formality == FormalityLevel.CASUAL
    assert plan.style.length == ResponseLength.SHORT
    assert plan.style.tone == Tone.WARM


def test_sensitive_context_has_priority_over_playful_memory_preference():
    personality = PersonalityProfile(
        traits={
            PersonalityTrait.HUMOR: 1.0,
            PersonalityTrait.WARMTH: 0.9,
        }
    )

    responder = ContextAwareResponder(
        behavior_engine=BehaviorEngine(
            personality=personality,
        )
    )

    behavior_context = BehaviorContext.from_tags(
        [
            SituationTag.CASUAL,
            SituationTag.SENSITIVE,
        ],
        sensitivity=1.0,
    )

    memory = MemoryContext(
        has_relevant_memory=True,
        preferred_tone=Tone.PLAYFUL,
    )

    context = ConversationContext(
        behavior_context=behavior_context,
        memory=memory,
    )

    plan = responder.build_plan(
        context,
        neutral_state(),
    )

    assert plan.style.tone != Tone.PLAYFUL


def test_sad_emotion_affects_context_aware_response():
    responder = ContextAwareResponder()

    behavior_context = BehaviorContext.from_tags(
        [
            SituationTag.REQUEST_HELP,
        ]
    )

    context = ConversationContext(
        behavior_context=behavior_context,
    )

    neutral_plan = responder.build_plan(
        context,
        neutral_state(),
    )

    sad_state = PersonalityState(
        emotion=EmotionState(
            emotion=Emotion.SADNESS,
            intensity=0.9,
        ),
        mood=MoodState(
            valence=-0.5,
            arousal=0.25,
        ),
    )

    sad_plan = responder.build_plan(
        context,
        sad_state,
    )

    assert (
        sad_plan.style.empathy
        > neutral_plan.style.empathy
    )

    assert (
        sad_plan.style.humor
        < neutral_plan.style.humor
    )


def test_personality_changes_context_aware_behavior():
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

    behavior_context = BehaviorContext.from_tags(
        [
            SituationTag.CASUAL,
        ]
    )

    context = ConversationContext(
        behavior_context=behavior_context,
    )

    humorous_responder = ContextAwareResponder(
        behavior_engine=BehaviorEngine(
            personality=humorous,
        )
    )

    serious_responder = ContextAwareResponder(
        behavior_engine=BehaviorEngine(
            personality=serious,
        )
    )

    humorous_plan = humorous_responder.build_plan(
        context,
        neutral_state(),
    )

    serious_plan = serious_responder.build_plan(
        context,
        neutral_state(),
    )

    assert (
        humorous_plan.behavior.behavior
        == BehaviorType.PLAYFUL
    )

    assert (
        serious_plan.behavior.behavior
        != BehaviorType.PLAYFUL
    )


def test_context_changes_behavior_with_same_personality():
    responder = ContextAwareResponder()

    casual_context = ConversationContext(
        behavior_context=BehaviorContext.from_tags(
            [
                SituationTag.CASUAL,
            ]
        )
    )

    help_context = ConversationContext(
        behavior_context=BehaviorContext.from_tags(
            [
                SituationTag.REQUEST_HELP,
            ]
        )
    )

    casual_plan = responder.build_plan(
        casual_context,
        neutral_state(),
    )

    help_plan = responder.build_plan(
        help_context,
        neutral_state(),
    )

    assert (
        casual_plan.behavior.behavior
        != help_plan.behavior.behavior
    )


def test_memory_topic_does_not_directly_override_behavior():
    responder = ContextAwareResponder()

    behavior_context = BehaviorContext.from_tags(
        [
            SituationTag.REQUEST_HELP,
        ]
    )

    memory = MemoryContext.from_topics(
        [
            "casual conversation",
        ],
        has_relevant_memory=True,
    )

    context = ConversationContext(
        behavior_context=behavior_context,
        memory=memory,
    )

    plan = responder.build_plan(
        context,
        neutral_state(),
    )

    assert plan.behavior.behavior == BehaviorType.INFORMATIVE


def test_relevant_memory_is_recorded_in_response_plan():
    responder = ContextAwareResponder()

    behavior_context = BehaviorContext.from_tags(
        [
            SituationTag.REQUEST_HELP,
        ]
    )

    memory = MemoryContext(
        has_relevant_memory=True,
    )

    context = ConversationContext(
        behavior_context=behavior_context,
        memory=memory,
    )

    plan = responder.build_plan(
        context,
        neutral_state(),
    )

    assert plan.has_relevant_memory is True
    assert plan.memory_used is True
    assert any(
        "Relevant memory" in note
        for note in plan.notes
    )


def test_no_memory_produces_no_memory_dependency():
    responder = ContextAwareResponder()

    behavior_context = BehaviorContext.from_tags(
        [
            SituationTag.REQUEST_HELP,
        ]
    )

    context = ConversationContext(
        behavior_context=behavior_context,
    )

    plan = responder.build_plan(
        context,
        neutral_state(),
    )

    assert plan.has_relevant_memory is False
    assert plan.memory_used is False


def test_build_plan_from_context_is_equivalent_api():
    responder = ContextAwareResponder()

    behavior_context = BehaviorContext.from_tags(
        [
            SituationTag.FAILURE,
        ]
    )

    memory = MemoryContext(
        has_relevant_memory=True,
        preferred_tone=Tone.ENCOURAGING,
    )

    plan = responder.build_plan_from_context(
        behavior_context,
        neutral_state(),
        topic="exam",
        turn_index=3,
        conversation_id="conversation-1",
        memory=memory,
    )

    assert plan.topic == "exam"
    assert plan.has_relevant_memory is True
    assert plan.style.tone == Tone.ENCOURAGING
    assert plan.behavior.behavior == BehaviorType.ENCOURAGING


def test_response_plan_does_not_contain_generated_text():
    responder = ContextAwareResponder()

    context = ConversationContext(
        behavior_context=BehaviorContext.from_tags(
            [
                SituationTag.GREETING,
            ]
        )
    )

    plan = responder.build_plan(
        context,
        neutral_state(),
    )

    assert not hasattr(plan, "response")
    assert not hasattr(plan, "text")
    assert not hasattr(plan, "generated_text")


def test_behavior_state_is_not_mutated():
    responder = ContextAwareResponder()

    state = neutral_state()

    context = ConversationContext(
        behavior_context=BehaviorContext.from_tags(
            [
                SituationTag.REQUEST_HELP,
            ]
        )
    )

    before = state.copy()

    responder.build_plan(
        context,
        state,
    )

    assert state.emotion.emotion == before.emotion.emotion
    assert state.emotion.intensity == before.emotion.intensity
    assert state.mood.valence == before.mood.valence
    assert state.mood.arousal == before.mood.arousal


def test_response_plan_has_reasoning_notes():
    responder = ContextAwareResponder()

    context = ConversationContext(
        behavior_context=BehaviorContext.from_tags(
            [
                SituationTag.REQUEST_HELP,
            ]
        )
    )

    plan = responder.build_plan(
        context,
        neutral_state(),
    )

    assert len(plan.notes) > 0
    assert any(
        "Selected behavior" in note
        for note in plan.notes
    )


def test_sensitive_context_generates_observability_note():
    responder = ContextAwareResponder()

    context = ConversationContext(
        behavior_context=BehaviorContext.from_tags(
            [
                SituationTag.USER_SAD,
                SituationTag.SENSITIVE,
            ],
            sensitivity=0.9,
        )
    )

    plan = responder.build_plan(
        context,
        neutral_state(),
    )

    assert any(
        "Sensitive context" in note
        for note in plan.notes
    )