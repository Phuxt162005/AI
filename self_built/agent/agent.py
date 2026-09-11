"""Main Agent implementation for ProjectAI."""

from __future__ import annotations

from typing import Any

from core.ai_core import AICoreService
from core.interfaces import AgentInterface, MemoryInterface
from core.types import InputData, OutputData, OutputType

from self_built.agent_planning import (
    ActionType,
    AgentPlanner,
    Plan,
    Understanding,
)
from self_built.tools import ToolExecutor

from .state import (
    AgentState,
    AgentTermination,
    Observation,
    ObservationStatus,
)

class ProjectAgent(AgentInterface):
    """Coordinate understanding, planning, AI Core, memory, and tools."""

    def __init__(
        self,
        planner: AgentPlanner,
        tool_executor: ToolExecutor,
        ai_core: AICoreService | None = None,
        memory: MemoryInterface | None = None,
        model_name: str | None = None,
        max_steps: int = 10,
        output_type: OutputType = OutputType.TEXT,
    ) -> None:
        if not isinstance(planner, AgentPlanner):
            raise TypeError("planner must be an AgentPlanner.")
        
        if not isinstance(tool_executor, ToolExecutor):
            raise TypeError("tool_executor must be a ToolExecutor.")
        
        if ai_core is not None and not isinstance(ai_core, AICoreService):
            raise TypeError("ai_core must be an AICoreService or None.")
        
        if memory is not None and not isinstance(memory, MemoryInterface):
            raise TypeError("memory must implement MemoryInterface.")
        
        if model_name is not None:
            if not isinstance(model_name, str):
                raise TypeError("model_name must be a string or None.")
            if not model_name.strip():
                raise ValueError("model_name must not be empty.")

        if (
            isinstance(max_steps, bool)
            or not isinstance(max_steps, int)
        ):
            raise TypeError("max_steps must be an integer.")

        if max_steps <= 0:
            raise ValueError("max_steps must be greater than zero.")

        if not isinstance(output_type, OutputType):
            raise TypeError("output_type must be an OutputType.")

        self._planner = planner
        self._tool_executor = tool_executor
        self._ai_core = ai_core
        self._memory = memory
        self._model_name = model_name
        self._max_steps = max_steps
        self._output_type = output_type
        self._last_state: AgentState | None = None

    @property
    def planner(self) -> AgentPlanner:
        """Return the Agent planner."""

        return self._planner

    @property
    def tool_executor(self) -> ToolExecutor:
        """Return the Tool executor."""

        return self._tool_executor

    @property
    def ai_core(self) -> AICoreService | None:
        """Return the configured AI Core service."""

        return self._ai_core

    @property
    def memory(self) -> MemoryInterface | None:
        """Return the configured memory."""

        return self._memory

    @property
    def model_name(self) -> str | None:
        """Return the configured model name."""

        return self._model_name

    @property
    def max_steps(self) -> int:
        """Return the maximum number of Agent steps."""

        return self._max_steps

    @property
    def last_state(self) -> AgentState | None:
        """Return the state of the most recent execution."""

        return self._last_state

    def process(self, input_data: InputData) -> OutputData:
        """Run the complete Agent loop."""

        if not isinstance(input_data, InputData):
            raise TypeError("input_data must be an InputData.")

        state = AgentState(input_data=input_data)
        self._last_state = state

        try:
            understanding = self._planner.analyze(input_data)
            state.understanding = understanding
            state.add_history(
                {
                    "event": "understanding",
                    "intent": understanding.intent.value,
                    "goal": understanding.goal,
                    "complexity": understanding.complexity.value,
                }
            )

            plan = self._planner.create_plan(understanding)
            state.plan = plan
            state.add_history(
                {
                    "event": "plan_created",
                    "step_count": len(plan.steps),
                }
            )

            while state.can_continue(self._max_steps):
                decision = self.decide(
                    {
                        "understanding": understanding,
                        "plan": plan,
                        "state": state,
                    }
                )
                state.add_history(
                    {
                        "event": "decision",
                        **decision,
                    }
                )
                action = decision.get("action")
                if action == ActionType.CLARIFY.value:
                    state.fail(
                        result=decision.get("reason", "The request requires clarification."),
                        termination=AgentTermination.NO_VALID_ACTION,
                    )
                    break

                if action == ActionType.DIRECT.value:
                    self._execute_direct(state, decision)
                elif action == ActionType.TOOL.value:
                    self._execute_tool(state, decision)
                elif action == ActionType.AI_CORE.value:
                    self._execute_ai_core(state, decision)
                else:
                    state.fail(
                        result=f"Unsupported action: {action}",
                        termination=AgentTermination.NO_VALID_ACTION,
                    )

                if state.completed or state.failed:
                    break

                if state.plan is None:
                    state.fail(
                        result="Agent plan is unavailable.",
                        termination=AgentTermination.NO_VALID_ACTION,
                    )
                    break

                if state.plan.is_finished:
                    state.complete(
                        result=self._latest_result(state),
                    )
                    break

            if (
                not state.completed
                and not state.failed
                and state.step_count >= self._max_steps
            ):
                state.fail(
                    result="Agent reached the maximum step limit.",
                    termination=AgentTermination.MAX_STEPS,
                )

        except Exception as exc:
            state.fail(
                result=str(exc),
                termination=AgentTermination.ERROR,
            )

        if state.completed:
            return self.respond(state.result)

        return self.respond(self._failure_response(state))

    def decide(
        self,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Decide the next Agent action."""

        if not isinstance(context, dict):
            raise TypeError("Agent decision context must be a dictionary.")

        understanding = context.get("understanding")
        plan = context.get("plan")

        if not isinstance(understanding, Understanding):
            raise TypeError("Decision context must contain Understanding.")

        if not isinstance(plan, Plan):
            raise TypeError("Decision context must contain Plan.")

        return self._planner.decide(understanding, plan)

    def respond(self, result: Any) -> OutputData:
        """Convert an Agent result into standardized output."""

        if isinstance(result, OutputData):
            return result

        return OutputData(type=self._output_type, content=result)

    def _execute_direct(
        self,
        state: AgentState,
        decision: dict[str, Any],
    ) -> None:
        """Execute a direct internal action such as memory retrieval."""

        if state.plan is None:
            self._record_error(
                state,
                decision,
                "Agent plan is unavailable.",
            )
            return

        step_id = decision.get("step_id")

        if step_id is None:
            self._record_error(
                state,
                decision,
                "Direct action does not have a step ID.",
            )
            return

        step = state.plan.steps[step_id]
        resource = step.metadata.get("resource")

        if resource == "memory":
            self._execute_memory(
                state,
                step_id,
            )
            return

        self._record_error(
            state,
            decision,
            "Unknown direct action resource.",
        )

    def _execute_memory(
        self,
        state: AgentState,
        step_id: int,
    ) -> None:
        """Retrieve remembered context."""

        if self._memory is None:
            self._record_error(
                state,
                {"step_id": step_id},
                "Memory is not configured.",
            )
            return

        try:
            result = self._memory.retrieve("last_input")
            observation = Observation(
                action=ActionType.DIRECT.value,
                status=ObservationStatus.SUCCESS,
                result=result,
                step_id=step_id,
                metadata={
                    "resource": "memory",
                    "key": "last_input",
                },
            )

            state.add_observation(observation)
            state.result = result
            state.step_count += 1
            state.add_history(
                {
                    "event": "memory",
                    "step_id": step_id,
                    "status": ObservationStatus.SUCCESS.value,
                }
            )
            self._complete_current_step(state)

        except Exception as exc:
            self._record_error(
                state,
                {
                    "step_id": step_id,
                    "resource": "memory",
                },
                str(exc),
            )

    def _execute_tool(
        self,
        state: AgentState,
        decision: dict[str, Any],
    ) -> None:
        """Execute the selected Tool."""

        tool_name = decision.get("tool_name")
        step_id = decision.get("step_id")

        if not isinstance(tool_name, str) or not tool_name:
            self._record_error(
                state,
                decision,
                "Tool action does not specify a tool name.",
            )
            return

        if step_id is None:
            self._record_error(
                state,
                decision,
                "Tool action does not have a step ID.",
            )
            return
        inputs = self._build_tool_inputs(state, tool_name)

        try:
            result = self._tool_executor.execute(tool_name, inputs)
            observation = Observation(
                action=ActionType.TOOL.value,
                status=ObservationStatus.SUCCESS,
                result=result,
                step_id=step_id,
                metadata={
                    "tool_name": tool_name,
                    "inputs": inputs,
                },
            )

            state.add_observation(observation)
            state.result = result
            state.step_count += 1
            state.add_history(
                {
                    "event": "tool_execution",
                    "step_id": step_id,
                    "tool_name": tool_name,
                    "status": ObservationStatus.SUCCESS.value,
                }
            )
            self._complete_current_step(state)

        except Exception as exc:
            self._record_error(
                state,
                {
                    "step_id": step_id,
                    "tool_name": tool_name,
                },
                str(exc),
            )

    def _execute_ai_core(
        self,
        state: AgentState,
        decision: dict[str, Any],
    ) -> None:
        """Execute the current step through AI Core."""

        if self._ai_core is None:
            self._record_error(
                state,
                decision,
                "AI Core is not configured.",
            )
            return

        if self._model_name is None:
            self._record_error(
                state,
                decision,
                "AI Core model name is not configured.",
            )
            return

        step_id = decision.get("step_id")

        if step_id is None:
            self._record_error(
                state,
                decision,
                "AI Core action does not have a step ID.",
            )
            return

        content = self._build_ai_core_input(state)

        ai_input = InputData(
            type=state.input_data.type,
            content=content,
            metadata={
                "agent": True,
                "step_id": step_id,
            },
        )

        try:
            result = self._ai_core.run(self._model_name, ai_input)
            observation = Observation(
                action=ActionType.AI_CORE.value,
                status=ObservationStatus.SUCCESS,
                result=result,
                step_id=step_id,
            )

            state.add_observation(observation)
            state.result = result
            state.step_count += 1
            state.add_history(
                {
                    "event": "ai_core_execution",
                    "step_id": step_id,
                    "status": ObservationStatus.SUCCESS.value,
                }
            )

            self._complete_current_step(state)

        except Exception as exc:
            self._record_error(state, {"step_id": step_id}, str(exc))

    def _build_tool_inputs(
        self,
        state: AgentState,
        tool_name: str,
    ) -> dict[str, Any]:
        """Build inputs for a Tool from the current Agent state."""

        goal = state.input_data.content
        if tool_name == "math":
            if not isinstance(goal, str):
                raise TypeError(
                    "Math Tool requires a textual expression."
                )
            expression = self._extract_math_expression(goal)
            return {"expression": expression}

        if tool_name == "search":
            if not isinstance(goal, str):
                raise TypeError(
                    "Search Tool requires a textual query."
                )
            query = self._extract_search_query(goal)
            return {"query": query, "max_results": 5}

        raise ValueError(f"No input adapter is available for tool '{tool_name}'.")

    @staticmethod
    def _extract_math_expression(text: str) -> str:
        """Extract a basic mathematical expression from user text."""

        expression = text.strip()
        prefixes = (
            "calculate ",
            "compute ",
            "tính ",
            "tính toán ",
        )
        normalized = expression.casefold()

        for prefix in prefixes:
            if normalized.startswith(prefix):
                return expression[len(prefix):].strip()

        return expression

    @staticmethod
    def _extract_search_query(text: str) -> str:
        """Extract a search query from user text."""

        query = text.strip()
        prefixes = (
            "search for ",
            "search ",
            "look up ",
            "lookup ",
            "find information about ",
            "find ",
            "tìm kiếm ",
            "tìm thông tin về ",
            "tìm ",
            "tra cứu ",
        )
        normalized = query.casefold()

        for prefix in prefixes:
            if normalized.startswith(prefix):
                return query[len(prefix):].strip()

        return query

    def _build_ai_core_input(
        self,
        state: AgentState,
    ) -> str:
        """Build AI Core input from the original goal and observations."""

        original = str(state.input_data.content)
        if not state.observations:
            return original

        lines = [
            f"Original request: {original}",
            "",
            "Observed results:",
        ]

        for index, observation in enumerate(
            state.observations,
            start=1,
        ):
            if observation.status == ObservationStatus.SUCCESS:
                lines.append(f"{index}. {observation.result}")
            else:
                lines.append(f"{index}. Error: {observation.error}")

        lines.append("")
        lines.append("Use the observations above to produce the final response.")
        return "\n".join(lines)

    def _complete_current_step(self, state: AgentState) -> None:
        """Mark the current plan step as completed."""

        if state.plan is None:
            state.fail(
                result="Agent plan is unavailable.",
                termination=AgentTermination.NO_VALID_ACTION,
            )
            return

        state.plan.mark_current_completed()
        if state.plan.is_finished:
            state.complete(result=state.result)

    def _record_error(
        self,
        state: AgentState,
        context: dict[str, Any],
        error: str,
    ) -> None:
        """Record an execution error and terminate safely."""

        step_id = context.get("step_id")
        observation = Observation(
            action=str(
                context.get(
                    "tool_name",
                    context.get(
                        "resource",
                        context.get(
                            "action",
                            "unknown",
                        ),
                    ),
                )
            ),
            status=ObservationStatus.ERROR,
            error=error,
            step_id=step_id,
        )
        state.add_observation(observation)
        state.step_count += 1
        state.add_history(
            {
                "event": "error",
                "step_id": step_id,
                "error": error,
            }
        )
        state.fail(result=error, termination=AgentTermination.ERROR)

    @staticmethod
    def _latest_result(state: AgentState) -> Any:
        """Return the most recent successful result."""

        for observation in reversed(state.observations):
            if observation.status == ObservationStatus.SUCCESS:
                return observation.result

        return state.result

    @staticmethod
    def _failure_response(state: AgentState) -> dict[str, Any]:
        """Build a structured failure response."""

        return {
            "error": state.result,
            "termination": state.termination.value,
            "steps": state.step_count,
        }