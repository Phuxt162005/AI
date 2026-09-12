"""Context-aware response planning for the Personality system.

This module combines contextual information, memory signals,
emotion, mood and personality into a response plan.

It does not generate natural-language responses.
It only decides how the response should behave and be expressed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping

from .emotion import PersonalityState
from .personality import (
    BehaviorContext,
    BehaviorDecision,
    BehaviorEngine,
    FormalityLevel,
    ResponseLength,
    ResponseStyle,
    SituationTag,
    Tone,
)

@dataclass(frozen=True)
class MemoryContext:
    """Explicit memory signals relevant to the current response.

    The Personality layer does not access a database or memory store
    directly. A memory subsystem can convert its stored information
    into this lightweight representation.

    This keeps Personality independent from the implementation of
    the Memory system.
    """

    relevant_topics: frozenset[str] = field(default_factory=frozenset)
    has_relevant_memory: bool = False
    relationship_familiarity: float = 0.5
    preferred_formality: FormalityLevel | None = None
    preferred_length: ResponseLength | None = None
    preferred_tone: Tone | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        normalized_topics = frozenset(
            _normalize_topic(topic)
            for topic in self.relevant_topics
        )

        if not 0.0 <= self.relationship_familiarity <= 1.0:
            raise ValueError("relationship_familiarity must be between 0.0 and 1.0.")
        
        object.__setattr__(self, "relevant_topics", normalized_topics)
        object.__setattr__(self, "metadata", dict(self.metadata))

    @classmethod
    def from_topics(
        cls,
        topics: Iterable[str],
        *,
        has_relevant_memory: bool = True,
        relationship_familiarity: float = 0.5,
        preferred_formality: FormalityLevel | None = None,
        preferred_length: ResponseLength | None = None,
        preferred_tone: Tone | None = None,
        metadata: Mapping[str, object] | None = None,
    ) -> "MemoryContext":
        """Create memory context from relevant topics."""

        return cls(
            relevant_topics=frozenset(topics),
            has_relevant_memory=has_relevant_memory,
            relationship_familiarity=relationship_familiarity,
            preferred_formality=preferred_formality,
            preferred_length=preferred_length,
            preferred_tone=preferred_tone,
            metadata=metadata or {},
        )

    def has_topic(self, topic: str) -> bool:
        """Return whether a topic exists in relevant memory."""

        return _normalize_topic(topic) in self.relevant_topics

@dataclass(frozen=True)
class ConversationContext:
    """Context describing the current interaction.

    This is a higher-level representation used by 3.5.3.

    ``BehaviorContext`` remains responsible for the behavioral
    situation itself. This class adds conversational information
    without modifying the existing BehaviorContext API.
    """

    behavior_context: BehaviorContext
    turn_index: int = 0
    conversation_id: str | None = None
    user_message_present: bool = True
    topic: str | None = None
    memory: MemoryContext = field(default_factory=MemoryContext)
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.turn_index < 0:
            raise ValueError("turn_index must not be negative.")

        if self.topic is not None:
            object.__setattr__(self, "topic", _normalize_topic(self.topic))

        object.__setattr__(self, "metadata", dict(self.metadata))

@dataclass(frozen=True)
class ResponsePlan:
    """Complete response plan produced by the Personality layer.

    The plan describes behavior and style but intentionally contains
    no generated natural-language response.
    """

    behavior: BehaviorDecision
    style: ResponseStyle
    topic: str | None
    has_relevant_memory: bool
    memory_used: bool
    context_tags: frozenset[str]
    confidence: float
    notes: tuple[str, ...] = field(default_factory=tuple)

class ContextAwareResponder:
    """Build response plans from the complete Personality state.

    The responder is intentionally deterministic.

    It combines:

        Memory
        + Context
        + Emotion
        + Mood
        + Personality
        -> Behavior
        -> Response Style
        -> Response Plan

    It does not generate text and does not call an external model.
    """

    def __init__(
        self,
        behavior_engine: BehaviorEngine | None = None,
    ) -> None:
        self._behavior_engine = (
            behavior_engine
            if behavior_engine is not None
            else BehaviorEngine()
        )

    @property
    def behavior_engine(self) -> BehaviorEngine:
        """Return the BehaviorEngine used by this responder."""

        return self._behavior_engine

    def build_plan(
        self,
        context: ConversationContext,
        state: PersonalityState,
    ) -> ResponsePlan:
        """Build a response plan from context and personality state."""

        if not isinstance(context, ConversationContext):
            raise TypeError("context must be a ConversationContext.")

        if not isinstance(state, PersonalityState):
            raise TypeError("state must be a PersonalityState.")

        behavior_context = context.behavior_context
        decision = self._behavior_engine.decide(behavior_context, state)
        style = self._behavior_engine.response_style(behavior_context, state, decision)
        style = self._apply_memory_preferences(style, context.memory, behavior_context)
        confidence = self._calculate_confidence(context, decision)
        notes = self._build_notes(context, decision, style)
        memory_used = self._memory_affects_plan(context.memory, style)

        return ResponsePlan(
            behavior=decision,
            style=style,
            topic=context.topic,
            has_relevant_memory=(
                context.memory.has_relevant_memory
            ),
            memory_used=memory_used,
            context_tags=behavior_context.tags,
            confidence=confidence,
            notes=notes,
        )

    def build_plan_from_context(
        self,
        behavior_context: BehaviorContext,
        state: PersonalityState,
        *,
        topic: str | None = None,
        turn_index: int = 0,
        conversation_id: str | None = None,
        memory: MemoryContext | None = None,
    ) -> ResponsePlan:
        """Convenience method for creating a conversation context."""

        context = ConversationContext(
            behavior_context=behavior_context,
            turn_index=turn_index,
            conversation_id=conversation_id,
            topic=topic,
            memory=(
                memory
                if memory is not None
                else MemoryContext()
            ),
        )

        return self.build_plan(context, state)

    @staticmethod
    def _apply_memory_preferences(
        style: ResponseStyle,
        memory: MemoryContext,
        behavior_context: BehaviorContext,
    ) -> ResponseStyle:
        """Apply explicit memory preferences to response style.

        Memory preferences are intentionally limited to explicit
        preferences. The system does not guess user preferences
        from arbitrary stored data.

        Sensitive situations still take priority over humor.
        """

        tone = style.tone
        formality = style.formality
        length = style.length

        if memory.preferred_tone is not None:
            tone = memory.preferred_tone

        if memory.preferred_formality is not None:
            formality = memory.preferred_formality

        if memory.preferred_length is not None:
            length = memory.preferred_length

        # Safety of emotional behavior has higher priority than
        # an ordinary remembered preference.
        if behavior_context.sensitivity >= 0.60:
            if tone == Tone.PLAYFUL:
                tone = Tone.GENTLE

        if behavior_context.has(SituationTag.USER_SAD):
            if tone == Tone.PLAYFUL:
                tone = Tone.GENTLE

        return ResponseStyle(
            tone=tone,
            formality=formality,
            length=length,
            directness=style.directness,
            warmth=style.warmth,
            humor=style.humor,
            empathy=style.empathy,
        )

    @staticmethod
    def _calculate_confidence(
        context: ConversationContext,
        decision: BehaviorDecision,
    ) -> float:
        """Estimate confidence in the selected response behavior."""

        confidence = 0.40

        if context.behavior_context.tags:
            confidence += 0.20

        if context.topic is not None:
            confidence += 0.10

        if context.memory.has_relevant_memory:
            confidence += 0.10

        confidence += (0.20 * decision.strength)

        return _clamp(confidence)

    @staticmethod
    def _build_notes(
        context: ConversationContext,
        decision: BehaviorDecision,
        style: ResponseStyle,
    ) -> tuple[str, ...]:
        """Build transparent reasoning notes for observability."""

        notes: list[str] = []

        if context.memory.has_relevant_memory:
            notes.append("Relevant memory was available.")

        if context.memory.preferred_tone is not None:
            notes.append("An explicit remembered tone preference was applied.")

        if context.memory.preferred_formality is not None:
            notes.append("An explicit remembered formality preference was applied.")

        if context.memory.preferred_length is not None:
            notes.append("An explicit remembered response-length preference was applied.")

        if context.behavior_context.sensitivity >= 0.60:
            notes.append("Sensitive context was given priority over ordinary style preferences.")

        notes.append(f"Selected behavior: {decision.behavior.value}.")
        notes.append(f"Selected tone: {style.tone.value}.")

        return tuple(notes)

    @staticmethod
    def _memory_affects_plan(memory: MemoryContext, style: ResponseStyle) -> bool:
        """Return whether memory supplied an actionable signal."""

        return any(
            (
                memory.has_relevant_memory,
                memory.preferred_tone is not None,
                memory.preferred_formality is not None,
                memory.preferred_length is not None,
            )
        )

def _normalize_topic(topic: str) -> str:
    """Normalize a topic name."""

    if not isinstance(topic, str):
        raise TypeError("Topic must be a string.")

    return topic.strip().lower()

def _clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 1.0,
) -> float:
    """Clamp a value into a range."""

    return max(minimum, min(value, maximum))