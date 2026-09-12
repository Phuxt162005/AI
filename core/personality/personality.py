"""Personality traits, behavior rules and response style.

This module implements the stable personality layer on top of the
emotion and mood system from ``core.personality.emotion``.

The module intentionally does not generate text. It decides how the
assistant should behave and what response style should be used.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Mapping

from .emotion import Emotion, PersonalityState


class PersonalityTrait(str, Enum):
    """Stable personality dimensions."""

    WARMTH = "warmth"
    EMPATHY = "empathy"
    HUMOR = "humor"
    PATIENCE = "patience"
    CURIOSITY = "curiosity"
    ASSERTIVENESS = "assertiveness"
    FORMALITY = "formality"
    DIRECTNESS = "directness"
    OPTIMISM = "optimism"
    OPENNESS = "openness"

class BehaviorType(str, Enum):
    """Behavioral tendencies that can be selected by the engine."""

    NEUTRAL = "neutral"
    SUPPORTIVE = "supportive"
    EMPATHETIC = "empathetic"
    ENCOURAGING = "encouraging"
    PLAYFUL = "playful"
    CURIOUS = "curious"
    INFORMATIVE = "informative"
    CLARIFYING = "clarifying"
    CALM = "calm"
    ASSERTIVE = "assertive"
    CAUTIOUS = "cautious"
    APOLOGETIC = "apologetic"
    CELEBRATORY = "celebratory"
    BOUNDARY_SETTING = "boundary_setting"

class Tone(str, Enum):
    """Overall emotional tone of a response."""

    NEUTRAL = "neutral"
    WARM = "warm"
    GENTLE = "gentle"
    SERIOUS = "serious"
    PLAYFUL = "playful"
    ENCOURAGING = "encouraging"
    CALM = "calm"
    FIRM = "firm"

class FormalityLevel(str, Enum):
    """Degree of formality."""

    CASUAL = "casual"
    BALANCED = "balanced"
    FORMAL = "formal"

class ResponseLength(str, Enum):
    """Preferred response length."""

    SHORT = "short"
    MODERATE = "moderate"
    DETAILED = "detailed"

class SituationTag(str, Enum):
    """Common situation tags understood by the behavior layer."""

    GREETING = "greeting"
    CASUAL = "casual"
    USER_HAPPY = "user_happy"
    USER_SAD = "user_sad"
    USER_ANGRY = "user_angry"
    USER_CONFUSED = "user_confused"
    PRAISE = "praise"
    NEGATIVE_FEEDBACK = "negative_feedback"
    REQUEST_HELP = "request_help"
    NEEDS_CLARIFICATION = "needs_clarification"
    GOOD_NEWS = "good_news"
    BAD_NEWS = "bad_news"
    FAILURE = "failure"
    UNCERTAINTY = "uncertainty"
    SENSITIVE = "sensitive"
    DISRESPECT = "disrespect"

@dataclass(frozen=True)
class PersonalityProfile:
    """Stable personality configuration.

    Trait values are in the range [0, 1].

    A value close to 0 means the trait is weak.
    A value close to 1 means the trait is strong.
    """

    traits: Mapping[PersonalityTrait, float] = field(
        default_factory=lambda: {
            PersonalityTrait.WARMTH: 0.80,
            PersonalityTrait.EMPATHY: 0.80,
            PersonalityTrait.HUMOR: 0.60,
            PersonalityTrait.PATIENCE: 0.80,
            PersonalityTrait.CURIOSITY: 0.70,
            PersonalityTrait.ASSERTIVENESS: 0.50,
            PersonalityTrait.FORMALITY: 0.30,
            PersonalityTrait.DIRECTNESS: 0.60,
            PersonalityTrait.OPTIMISM: 0.70,
            PersonalityTrait.OPENNESS: 0.75,
        }
    )

    def __post_init__(self) -> None:
        normalized: dict[PersonalityTrait, float] = {}
        for trait in PersonalityTrait:
            value = self.traits.get(trait, 0.5)

            if not isinstance(value, (int, float)):
                raise TypeError(f"Trait '{trait.value}' must be numeric.")

            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(f"Trait '{trait.value}' must be between 0.0 and 1.0.")
            normalized[trait] = float(value)

        object.__setattr__(self, "traits", normalized)

    def get(self, trait: PersonalityTrait) -> float:
        """Return the value of a personality trait."""

        return float(self.traits[trait])

    def with_trait(
        self,
        trait: PersonalityTrait,
        value: float,
    ) -> "PersonalityProfile":
        """Return a new profile with one modified trait."""

        if not isinstance(trait, PersonalityTrait):
            raise TypeError("trait must be a PersonalityTrait.")

        if not 0.0 <= value <= 1.0:
            raise ValueError("Trait value must be between 0.0 and 1.0.")

        updated = dict(self.traits)
        updated[trait] = float(value)

        return PersonalityProfile(traits=updated)

@dataclass(frozen=True)
class BehaviorContext:
    """Situation information supplied to the Personality layer.

    The Personality layer does not interpret raw text here.

    A previous layer can convert an interaction into a set of tags.
    New tags can be added later without changing this class.
    """

    tags: frozenset[str] = field(default_factory=frozenset)
    importance: float = 0.5
    sensitivity: float = 0.0

    def __post_init__(self) -> None:
        normalized_tags = frozenset(_normalize_tag(tag) for tag in self.tags)

        if not 0.0 <= self.importance <= 1.0:
            raise ValueError("importance must be between 0.0 and 1.0.")

        if not 0.0 <= self.sensitivity <= 1.0:
            raise ValueError("sensitivity must be between 0.0 and 1.0.")
        object.__setattr__(self, "tags", normalized_tags)

    @classmethod
    def from_tags(
        cls,
        tags: Iterable[str | SituationTag],
        importance: float = 0.5,
        sensitivity: float = 0.0,
    ) -> "BehaviorContext":
        """Create context from strings or SituationTag values."""

        normalized = frozenset(
            tag.value if isinstance(tag, SituationTag) else tag
            for tag in tags
        )

        return cls(
            tags=normalized,
            importance=importance,
            sensitivity=sensitivity,
        )

    def has(
        self,
        tag: str | SituationTag,
    ) -> bool:
        """Return whether a context tag exists."""
        value = (
            tag.value
            if isinstance(tag, SituationTag)
            else _normalize_tag(tag)
        )
        return value in self.tags

@dataclass(frozen=True)
class BehaviorRule:
    """A rule that increases or decreases a behavior tendency.

    ``required_tags``:
        Tags that must be present for the rule to contribute.

    ``excluded_tags``:
        Tags that prevent the rule from contributing.

    ``trait_weights``:
        Personality traits influencing the rule.

    ``emotion_weights``:
        Emotion influences using the emotion enum.

    ``priority``:
        Priority used when two behaviors have similar scores.
    """

    behavior: BehaviorType
    required_tags: frozenset[str] = field(default_factory=frozenset)
    excluded_tags: frozenset[str] = field(default_factory=frozenset)
    trait_weights: Mapping[PersonalityTrait, float] = field(default_factory=dict)
    emotion_weights: Mapping[Emotion, float] = field(default_factory=dict)
    mood_valence_weight: float = 0.0
    mood_arousal_weight: float = 0.0
    base_score: float = 0.0
    priority: int = 0
    reason: str = ""

    def matches(self, context: BehaviorContext) -> bool:
        """Return whether this rule applies to the situation."""

        if not self.required_tags.issubset(context.tags):
            return False

        if self.excluded_tags.intersection(context.tags):
            return False

        return True

@dataclass(frozen=True)
class BehaviorDecision:
    """Result of behavior selection."""

    behavior: BehaviorType
    strength: float
    priority: int
    reason: str

@dataclass(frozen=True)
class ResponseStyle:
    """Style instructions for the response generator."""

    tone: Tone
    formality: FormalityLevel
    length: ResponseLength
    directness: float
    warmth: float
    humor: float
    empathy: float

class BehaviorEngine:
    """Select behavior and response style from Personality + state.

    The engine is deterministic.

    It does not generate text and does not depend on an external model.
    """

    def __init__(
        self,
        personality: PersonalityProfile | None = None,
        rules: Iterable[BehaviorRule] | None = None,
    ) -> None:
        self._personality = (
            personality
            if personality is not None
            else PersonalityProfile()
        )
        self._rules = tuple(
            rules
            if rules is not None
            else default_behavior_rules()
        )

    @property
    def personality(self) -> PersonalityProfile:
        """Return the configured personality profile."""

        return self._personality

    @property
    def rules(self) -> tuple[BehaviorRule, ...]:
        """Return the configured behavior rules."""

        return self._rules

    def decide(
        self,
        context: BehaviorContext,
        state: PersonalityState,
    ) -> BehaviorDecision:
        """Select the strongest behavior for a situation."""

        if not isinstance(context, BehaviorContext):
            raise TypeError(
                "context must be a BehaviorContext."
            )
        if not isinstance(state, PersonalityState):
            raise TypeError(
                "state must be a PersonalityState."
            )
        best_decision: BehaviorDecision | None = None

        for rule in self._rules:
            if not rule.matches(context):
                continue
            score = self._score_rule(
                rule,
                context,
                state,
            )
            decision = BehaviorDecision(
                behavior=rule.behavior,
                strength=_clamp(score, 0.0, 1.0),
                priority=rule.priority,
                reason=rule.reason,
            )
            if self._is_better(decision, best_decision):
                best_decision = decision

        if best_decision is not None:
            return best_decision

        return self._default_decision(state)

    def response_style(
        self,
        context: BehaviorContext,
        state: PersonalityState,
        decision: BehaviorDecision | None = None,
    ) -> ResponseStyle:
        """Determine response style from the current state."""

        if decision is None:
            decision = self.decide(context, state)

        warmth = self._personality.get(PersonalityTrait.WARMTH)
        empathy = self._personality.get(PersonalityTrait.EMPATHY)
        humor = self._personality.get(PersonalityTrait.HUMOR)
        directness = self._personality.get(PersonalityTrait.DIRECTNESS)
        formality = self._personality.get(PersonalityTrait.FORMALITY)

        # Strong negative or sensitive situations suppress humor.
        if context.sensitivity >= 0.60:
            humor *= 0.20

        if context.has(SituationTag.USER_SAD):
            humor *= 0.10

        if context.has(SituationTag.FAILURE):
            humor *= 0.25

        # Mood affects style, but does not replace personality.
        mood_valence = state.mood.valence
        mood_arousal = state.mood.arousal
        warmth = _blend(warmth, _positive_mood_effect(mood_valence), 0.20)

        if state.emotion.emotion in {Emotion.SADNESS, Emotion.CONCERN}:
            empathy = _blend(empathy, 1.0, 0.25)

        if state.emotion.emotion in {Emotion.ANGER, Emotion.FEAR}:
            humor *= 0.25

        tone = self._select_tone(
            decision.behavior,
            warmth,
            humor,
            empathy,
            mood_arousal,
        )

        formality_level = self._select_formality(formality)

        length = self._select_length(context, state)

        return ResponseStyle(
            tone=tone,
            formality=formality_level,
            length=length,
            directness=_clamp(directness),
            warmth=_clamp(warmth),
            humor=_clamp(humor),
            empathy=_clamp(empathy),
        )

    def decide_with_style(
        self,
        context: BehaviorContext,
        state: PersonalityState,
    ) -> tuple[BehaviorDecision, ResponseStyle]:
        """Select behavior and style together."""

        decision = self.decide(context, state)
        style = self.response_style(context, state, decision)
        return decision, style

    def _score_rule(
        self,
        rule: BehaviorRule,
        context: BehaviorContext,
        state: PersonalityState,
    ) -> float:
        """Calculate a behavior score."""
        score = rule.base_score

        for trait, weight in rule.trait_weights.items():
            score += (self._personality.get(trait) * weight)

        emotion_weight = rule.emotion_weights.get(state.emotion.emotion, 0.0)
        score += (emotion_weight * state.emotion.intensity)
        score += (rule.mood_valence_weight * max(-1.0, min(1.0, state.mood.valence)))
        score += (rule.mood_arousal_weight * state.mood.arousal)

        # Importance increases the effect of a behavior when the
        # situation is important.
        score *= (0.75 + (0.25 * context.importance))

        # Sensitive situations naturally reduce playful behavior.
        if context.sensitivity > 0.0:
            if rule.behavior == BehaviorType.PLAYFUL:
                score *= (1.0 - (0.75 * context.sensitivity))
        return score

    @staticmethod
    def _is_better(
        candidate: BehaviorDecision,
        current: BehaviorDecision | None,
    ) -> bool:
        """Compare two behavior decisions."""

        if current is None:
            return True

        if candidate.strength > current.strength + 0.05:
            return True

        if abs(candidate.strength - current.strength) <= 0.05:
            return candidate.priority > current.priority

        return False

    @staticmethod
    def _default_decision(state: PersonalityState) -> BehaviorDecision:
        """Fallback behavior when no rule matches."""

        if state.emotion.emotion in {
            Emotion.SADNESS,
            Emotion.CONCERN,
        }:
            return BehaviorDecision(
                behavior=BehaviorType.SUPPORTIVE,
                strength=0.50,
                priority=0,
                reason="Default supportive behavior for a negative state.",
            )

        return BehaviorDecision(
            behavior=BehaviorType.NEUTRAL,
            strength=0.40,
            priority=0,
            reason="No specialized behavior rule matched.",
        )

    @staticmethod
    def _select_tone(
        behavior: BehaviorType,
        warmth: float,
        humor: float,
        empathy: float,
        arousal: float,
    ) -> Tone:
        """Select the dominant response tone."""

        if behavior == BehaviorType.BOUNDARY_SETTING:
            return Tone.FIRM

        if behavior == BehaviorType.ASSERTIVE:
            return Tone.FIRM

        if behavior in {BehaviorType.SUPPORTIVE, BehaviorType.EMPATHETIC}:
            return Tone.GENTLE

        if behavior == BehaviorType.ENCOURAGING:
            return Tone.ENCOURAGING

        if behavior == BehaviorType.PLAYFUL:
            return Tone.PLAYFUL

        if behavior == BehaviorType.CALM:
            return Tone.CALM

        if behavior == BehaviorType.CELEBRATORY:
            return Tone.WARM

        if humor >= 0.70 and warmth >= 0.60:
            return Tone.PLAYFUL

        if empathy >= 0.75:
            return Tone.WARM

        if arousal >= 0.75:
            return Tone.SERIOUS

        return Tone.NEUTRAL

    @staticmethod
    def _select_formality(value: float) -> FormalityLevel:
        """Convert continuous formality to a level."""

        if value < 0.35:
            return FormalityLevel.CASUAL

        if value < 0.70:
            return FormalityLevel.BALANCED
        return FormalityLevel.FORMAL

    @staticmethod
    def _select_length(context: BehaviorContext, state: PersonalityState) -> ResponseLength:
        """Select a rough response-length preference."""

        if context.has(SituationTag.GREETING):
            return ResponseLength.SHORT

        if context.has(SituationTag.CASUAL):
            return ResponseLength.SHORT

        if context.has(SituationTag.REQUEST_HELP):
            return ResponseLength.DETAILED

        if context.has(SituationTag.NEEDS_CLARIFICATION):
            return ResponseLength.MODERATE

        if state.emotion.emotion in {
            Emotion.SADNESS,
            Emotion.CONCERN,
        }:
            return ResponseLength.MODERATE
        return ResponseLength.MODERATE

def default_behavior_rules() -> tuple[BehaviorRule, ...]:
    """Return the default behavior rules.

    The rules intentionally describe tendencies rather than fixed
    responses. This keeps Personality independent from language
    generation.
    """
    return (
        BehaviorRule(
            behavior=BehaviorType.SUPPORTIVE,
            required_tags=frozenset({SituationTag.USER_SAD.value}),
            trait_weights={
                PersonalityTrait.EMPATHY: 0.60,
                PersonalityTrait.WARMTH: 0.30,
                PersonalityTrait.PATIENCE: 0.20,
            },
            emotion_weights={
                Emotion.SADNESS: 0.30,
                Emotion.CONCERN: 0.20,
            },
            priority=10,
            reason="The user appears emotionally down.",
        ),
        BehaviorRule(
            behavior=BehaviorType.EMPATHETIC,
            required_tags=frozenset(
                {
                    SituationTag.USER_SAD.value,
                    SituationTag.SENSITIVE.value,
                }
            ),
            trait_weights={
                PersonalityTrait.EMPATHY: 0.75,
                PersonalityTrait.WARMTH: 0.35,
            },
            emotion_weights={
                Emotion.CONCERN: 0.30,
                Emotion.SADNESS: 0.20,
            },
            priority=20,
            reason="A sensitive situation requires stronger empathy.",
        ),
        BehaviorRule(
            behavior=BehaviorType.CALM,
            required_tags=frozenset({SituationTag.USER_ANGRY.value}),
            trait_weights={
                PersonalityTrait.PATIENCE: 0.65,
                PersonalityTrait.EMPATHY: 0.20,
                PersonalityTrait.ASSERTIVENESS: 0.20,
            },
            emotion_weights={
                Emotion.ANGER: 0.20,
                Emotion.FEAR: 0.10,
            },
            mood_arousal_weight=-0.15,
            priority=15,
            reason="The user is angry, so the assistant should remain calm.",
        ),
        BehaviorRule(
            behavior=BehaviorType.ASSERTIVE,
            required_tags=frozenset({SituationTag.DISRESPECT.value}),
            trait_weights={
                PersonalityTrait.ASSERTIVENESS: 0.75,
                PersonalityTrait.DIRECTNESS: 0.40,
                PersonalityTrait.PATIENCE: 0.15,
            },
            priority=25,
            reason="Disrespect requires a calm but firm boundary.",
        ),
        BehaviorRule(
            behavior=BehaviorType.BOUNDARY_SETTING,
            required_tags=frozenset(
                {
                    SituationTag.DISRESPECT.value,
                    SituationTag.NEGATIVE_FEEDBACK.value,
                }
            ),
            trait_weights={
                PersonalityTrait.ASSERTIVENESS: 0.85,
                PersonalityTrait.DIRECTNESS: 0.45,
            },
            priority=30,
            reason="Repeated negative interaction requires a clear boundary.",
        ),
        BehaviorRule(
            behavior=BehaviorType.ENCOURAGING,
            required_tags=frozenset({SituationTag.FAILURE.value}),
            trait_weights={
                PersonalityTrait.OPTIMISM: 0.65,
                PersonalityTrait.EMPATHY: 0.30,
                PersonalityTrait.WARMTH: 0.25,
            },
            emotion_weights={Emotion.CONCERN: 0.15},
            priority=15,
            reason="Failure should encourage constructive continuation.",
        ),
        BehaviorRule(
            behavior=BehaviorType.CELEBRATORY,
            required_tags=frozenset({SituationTag.GOOD_NEWS.value}),
            trait_weights={
                PersonalityTrait.OPTIMISM: 0.55,
                PersonalityTrait.WARMTH: 0.40,
                PersonalityTrait.HUMOR: 0.20,
            },
            emotion_weights={
                Emotion.JOY: 0.25,
                Emotion.RELIEF: 0.20,
            },
            priority=15,
            reason="Positive events invite a positive reaction.",
        ),
        BehaviorRule(
            behavior=BehaviorType.PLAYFUL,
            required_tags=frozenset({SituationTag.CASUAL.value}),
            excluded_tags=frozenset(
                {
                    SituationTag.SENSITIVE.value,
                    SituationTag.USER_SAD.value,
                    SituationTag.FAILURE.value,
                }
            ),
            trait_weights={
                PersonalityTrait.HUMOR: 0.70,
                PersonalityTrait.WARMTH: 0.20,
                PersonalityTrait.OPENNESS: 0.20,
            },
            emotion_weights={Emotion.JOY: 0.20},
            mood_valence_weight=0.15,
            priority=5,
            reason="Casual situations allow a more playful style.",
        ),
        BehaviorRule(
            behavior=BehaviorType.CURIOUS,
            required_tags=frozenset({SituationTag.NEEDS_CLARIFICATION.value}),
            trait_weights={
                PersonalityTrait.CURIOSITY: 0.70,
                PersonalityTrait.OPENNESS: 0.30,
                PersonalityTrait.PATIENCE: 0.20,
            },
            priority=10,
            reason="Missing information should encourage clarification.",
        ),
        BehaviorRule(
            behavior=BehaviorType.CLARIFYING,
            required_tags=frozenset({SituationTag.NEEDS_CLARIFICATION.value}),
            trait_weights={
                PersonalityTrait.CURIOSITY: 0.45,
                PersonalityTrait.DIRECTNESS: 0.40,
                PersonalityTrait.PATIENCE: 0.30,
            },
            priority=15,
            reason="Clarification is needed before proceeding.",
        ),
        BehaviorRule(
            behavior=BehaviorType.CAUTIOUS,
            required_tags=frozenset({SituationTag.UNCERTAINTY.value}),
            trait_weights={
                PersonalityTrait.OPENNESS: 0.20,
                PersonalityTrait.PATIENCE: 0.20,
            },
            emotion_weights={
                Emotion.FEAR: 0.25,
                Emotion.CONCERN: 0.20,
            },
            priority=20,
            reason="Uncertainty calls for a cautious response.",
        ),
        BehaviorRule(
            behavior=BehaviorType.INFORMATIVE,
            required_tags=frozenset({SituationTag.REQUEST_HELP.value}),
            trait_weights={
                PersonalityTrait.DIRECTNESS: 0.45,
                PersonalityTrait.CURIOSITY: 0.25,
                PersonalityTrait.PATIENCE: 0.25,
            },
            priority=5,
            reason="The user requested assistance.",
        ),
        BehaviorRule(
            behavior=BehaviorType.NEUTRAL,
            required_tags=frozenset({SituationTag.GREETING.value}),
            trait_weights={
                PersonalityTrait.WARMTH: 0.30,
                PersonalityTrait.OPENNESS: 0.20,
            },
            priority=1,
            reason="A greeting normally requires a simple response.",
        ),
    )

def _normalize_tag(tag: str) -> str:
    """Normalize an arbitrary context tag."""

    if not isinstance(tag, str):
        raise TypeError("Context tags must be strings.")

    return tag.strip().lower()

def _clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 1.0,
) -> float:
    """Limit a numeric value to a range."""

    return max(minimum, min(value, maximum))

def _blend(first: float, second: float, weight: float) -> float:
    """Blend two values."""

    return first + ((second - first) * weight)

def _positive_mood_effect(mood_valence: float) -> float:
    """Map mood valence into a warmth-supporting value."""

    return _clamp(0.50 + (mood_valence * 0.50))