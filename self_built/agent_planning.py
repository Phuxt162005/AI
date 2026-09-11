"""Self-built understanding and planning components for ProjectAI Agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import re
from typing import Any

from core.types import InputData, InputType

class Intent(str, Enum):
    """High-level intent understood from a user request."""

    CHAT = "chat"
    QUESTION = "question"
    CALCULATION = "calculation"
    SEARCH = "search"
    MULTI_STEP = "multi_step"
    UNKNOWN = "unknown"

class Complexity(str, Enum):
    """Estimated complexity of a user request."""

    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"

class ActionType(str, Enum):
    """Possible actions selected by the decision component."""

    DIRECT = "direct"
    AI_CORE = "ai_core"
    TOOL = "tool"
    CLARIFY = "clarify"

class StepStatus(str, Enum):
    """Execution status reserved for later Agent Loop integration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass(frozen=True)
class Understanding:
    """Structured interpretation of one user request."""

    intent: Intent
    goal: str
    complexity: Complexity
    input_type: InputType
    requires_tool: bool = False
    requires_ai_core: bool = False
    requires_memory: bool = False
    confidence: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class TaskStep:
    """One executable step in a planned task."""

    step_id: int
    description: str
    action: ActionType
    status: StepStatus = StepStatus.PENDING
    tool_name: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class Plan:
    """Ordered plan generated from an understood request."""

    goal: str
    steps: list[TaskStep] = field(default_factory=list)
    current_step: int = 0
    completed: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_step(
        self,
        description: str,
        action: ActionType,
        tool_name: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> TaskStep:
        """Append a new step to the plan."""

        step = TaskStep(
            step_id=len(self.steps),
            description=description,
            action=action,
            tool_name=tool_name,
            metadata=dict(metadata or {}),
        )
        self.steps.append(step)
        return step

    @property
    def is_empty(self) -> bool:
        """Return whether the plan contains no steps."""
        return not self.steps

    @property
    def is_finished(self) -> bool:
        """Return whether all plan steps have completed."""
        return self.completed or (
            bool(self.steps)
            and all(step.status == StepStatus.COMPLETED for step in self.steps)
        )

    def mark_current_completed(self) -> None:
        """Mark the current step as completed and advance the cursor."""
        if self.current_step >= len(self.steps):
            self.completed = True
            return

        self.steps[self.current_step].status = StepStatus.COMPLETED
        self.current_step += 1

        if self.current_step >= len(self.steps):
            self.completed = True

class RequestUnderstanding:
    """Rule-based request understanding for the initial Agent implementation.

    This component intentionally uses lightweight deterministic rules.
    A future model-based implementation can replace it while preserving
    the Understanding data contract.
    """

    _SEARCH_KEYWORDS = (
        "search",
        "find",
        "look up",
        "lookup",
        "find information",
        "tìm",
        "tìm kiếm",
        "tra cứu",
        "tìm thông tin",
    )

    _CALCULATION_KEYWORDS = (
        "calculate",
        "calculation",
        "compute",
        "sum",
        "subtract",
        "multiply",
        "divide",
        "tính",
        "tính toán",
        "cộng",
        "trừ",
        "nhân",
        "chia",
    )
    
    _CHAT_KEYWORDS = (
    "hello",
    "hi",
    "hey",
    "how are you",
    "how are things",
    "how's it going",
    "xin chào",
    "chào",
    "bạn khỏe không",
    )

    _QUESTION_KEYWORDS = (
    "what",
    "why",
    "when",
    "where",
    "who",
    "how",
    "what is",
    "what are",
    "do you remember",
    "did you remember",
    "bạn có nhớ",
    "bạn còn nhớ",
    "là gì",
    "tại sao",
    "khi nào",
    "ở đâu",
    "ai là",
    "như thế nào",
    "thế nào",
    "thì sao",
    )

    _MULTI_STEP_MARKERS = (
        "then",
        "after that",
        "and then",
        "first",
        "next",
        "finally",
        "sau đó",
        "tiếp theo",
        "cuối cùng",
        "rồi",
        "và tính",
        "và tìm",
    )

    _MEMORY_KEYWORDS = (
        "remember",
        "previous",
        "earlier",
        "last time",
        "nhớ",
        "lần trước",
        "trước đó",
    )

    def understand(self, input_data: InputData) -> Understanding:
        """Understand an InputData instance."""

        goal = self._extract_goal(input_data)
        normalized = goal.casefold().strip()

        if not normalized:
            return Understanding(
                intent=Intent.UNKNOWN,
                goal=goal,
                complexity=Complexity.SIMPLE,
                input_type=input_data.type,
                confidence=1.0,
                metadata={"reason": "empty_request"},
            )

        multi_step = self._contains_any(
            normalized,
            self._MULTI_STEP_MARKERS,
        )

        if multi_step:
            intent = Intent.MULTI_STEP
            confidence = 0.95
        elif self._contains_any(normalized, self._CALCULATION_KEYWORDS):
            intent = Intent.CALCULATION
            confidence = 0.90
        elif self._contains_any(normalized, self._SEARCH_KEYWORDS):
            intent = Intent.SEARCH
            confidence = 0.90
        elif self._contains_any(normalized, self._CHAT_KEYWORDS):
            intent = Intent.CHAT
            confidence = 0.90
        elif self._contains_any(normalized, self._QUESTION_KEYWORDS):
            intent = Intent.QUESTION
            confidence = 0.85
        else:
            intent = Intent.CHAT
            confidence = 0.60

        complexity = self._estimate_complexity(
            normalized,
            intent,
            input_data,
        )

        requires_tool = intent in {
            Intent.CALCULATION,
            Intent.SEARCH,
            Intent.MULTI_STEP,
        }

        requires_ai_core = intent in {
            Intent.CHAT,
            Intent.QUESTION,
            Intent.MULTI_STEP,
        }

        requires_memory = self._contains_any(
            normalized,
            self._MEMORY_KEYWORDS,
        )

        return Understanding(
            intent=intent,
            goal=goal,
            complexity=complexity,
            input_type=input_data.type,
            requires_tool=requires_tool,
            requires_ai_core=requires_ai_core,
            requires_memory=requires_memory,
            confidence=confidence,
        )

    @staticmethod
    def _extract_goal(input_data: InputData) -> str:
        """Extract a textual goal from supported input data."""

        if input_data.type == InputType.TEXT:
            if not isinstance(input_data.content, str):
                raise TypeError("TEXT input content must be a string.")
            return input_data.content.strip()

        # Voice and image are intentionally represented without trying to
        # perform speech or vision processing in this component.
        if input_data.content is None:
            return ""

        return str(input_data.content).strip()

    @staticmethod
    def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
        """Return whether text contains one of the supplied words or phrases."""

        for keyword in keywords:
            pattern = rf"(?<!\w){re.escape(keyword)}(?!\w)"

            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    @staticmethod
    def _estimate_complexity(
        text: str,
        intent: Intent,
        input_data: InputData,
    ) -> Complexity:
        """Estimate request complexity using lightweight deterministic rules."""

        if not text:
            return Complexity.SIMPLE

        word_count = len(text.split())

        if intent == Intent.MULTI_STEP:
            return Complexity.COMPLEX

        if input_data.type != InputType.TEXT:
            return Complexity.MODERATE

        if word_count > 30:
            return Complexity.COMPLEX

        if intent in {
            Intent.SEARCH,
            Intent.CALCULATION,
            Intent.QUESTION,
        }:
            return Complexity.MODERATE

        return Complexity.SIMPLE


class TaskDecomposer:
    """Convert an Understanding into an ordered task plan."""

    def decompose(self, understanding: Understanding) -> Plan:
        """Create a plan appropriate for the understood intent."""

        plan = Plan(goal=understanding.goal)

        if understanding.intent == Intent.UNKNOWN:
            plan.add_step(
                description="Request clarification from the user.",
                action=ActionType.CLARIFY,
            )
            return plan

        if understanding.intent == Intent.CHAT:
            plan.add_step(
                description="Generate a conversational response.",
                action=ActionType.AI_CORE,
            )
            return plan

        if understanding.intent == Intent.QUESTION:
            if understanding.requires_memory:
                plan.add_step(
                    description="Retrieve relevant remembered context.",
                    action=ActionType.DIRECT,
                    metadata={"resource": "memory"},
                )

            plan.add_step(
                description="Generate an answer to the question.",
                action=ActionType.AI_CORE,
            )
            return plan

        if understanding.intent == Intent.CALCULATION:
            plan.add_step(
                description="Evaluate the requested calculation.",
                action=ActionType.TOOL,
                tool_name="math",
            )
            plan.add_step(
                description="Present the calculation result.",
                action=ActionType.AI_CORE,
            )
            return plan

        if understanding.intent == Intent.SEARCH:
            plan.add_step(
                description="Search for information relevant to the request.",
                action=ActionType.TOOL,
                tool_name="search",
            )
            plan.add_step(
                description="Process and present the search result.",
                action=ActionType.AI_CORE,
            )
            return plan

        if understanding.intent == Intent.MULTI_STEP:
            self._decompose_multi_step(understanding, plan)
            return plan

        plan.add_step(
            description="Process the request with the AI Core.",
            action=ActionType.AI_CORE,
        )
        return plan

    def _decompose_multi_step(
        self,
        understanding: Understanding,
        plan: Plan,
    ) -> None:
        """Create a minimal ordered plan for a multi-step request."""

        text = understanding.goal.casefold()

        if self._contains_any(
            text,
            RequestUnderstanding._SEARCH_KEYWORDS,
        ):
            plan.add_step(
                description="Search for the required information.",
                action=ActionType.TOOL,
                tool_name="search",
            )

        if self._contains_any(
            text,
            RequestUnderstanding._CALCULATION_KEYWORDS,
        ):
            plan.add_step(
                description="Perform the requested calculation.",
                action=ActionType.TOOL,
                tool_name="math",
            )

        plan.add_step(
            description="Process the intermediate results.",
            action=ActionType.AI_CORE,
        )

        # A multi-step request should never produce an empty plan.
        if plan.is_empty:
            plan.add_step(
                description="Process the multi-step request with the AI Core.",
                action=ActionType.AI_CORE,
            )

    @staticmethod
    def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
        """Return whether text contains one of the supplied words or phrases."""

        for keyword in keywords:
            pattern = rf"(?<!\w){re.escape(keyword)}(?!\w)"

            if re.search(pattern, text, re.IGNORECASE):
                return True 
        return False

class DecisionEngine:
    """Select the next high-level action from understanding and plan state."""

    def decide(
        self,
        understanding: Understanding,
        plan: Plan | None = None,
    ) -> dict[str, Any]:
        """Return a structured decision for the next Agent action."""

        if understanding.intent == Intent.UNKNOWN:
            return {
                "action": ActionType.CLARIFY.value,
                "reason": "The request could not be understood reliably.",
            }

        if plan is None or plan.is_empty:
            return {
                "action": ActionType.CLARIFY.value,
                "reason": "No executable plan is available.",
            }

        if plan.is_finished:
            return {
                "action": ActionType.DIRECT.value,
                "reason": "The current plan has already completed.",
            }

        current = plan.steps[plan.current_step]

        return {
            "action": current.action.value,
            "reason": f"Execute plan step {current.step_id}.",
            "step_id": current.step_id,
            "description": current.description,
            "tool_name": current.tool_name,
        }

class AgentPlanner:
    """Facade combining understanding, decomposition, and decision."""

    def __init__(
        self,
        understanding: RequestUnderstanding | None = None,
        decomposer: TaskDecomposer | None = None,
        decision_engine: DecisionEngine | None = None,
    ) -> None:
        self.understanding = understanding or RequestUnderstanding()
        self.decomposer = decomposer or TaskDecomposer()
        self.decision_engine = decision_engine or DecisionEngine()

    def analyze(self, input_data: InputData) -> Understanding:
        """Understand an input request."""

        return self.understanding.understand(input_data)

    def create_plan(self, understanding: Understanding) -> Plan:
        """Create a plan from an understanding result."""

        return self.decomposer.decompose(understanding)

    def decide(
        self,
        understanding: Understanding,
        plan: Plan,
    ) -> dict[str, Any]:
        """Select the next action from the current plan."""

        return self.decision_engine.decide(understanding, plan)

    def process(self, input_data: InputData) -> dict[str, Any]:
        """Run the complete Understanding & Planning stage."""

        understanding = self.analyze(input_data)
        plan = self.create_plan(understanding)
        decision = self.decide(understanding, plan)

        return {
            "understanding": understanding,
            "plan": plan,
            "decision": decision,
        }