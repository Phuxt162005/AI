"""Self-built mathematical Tool for ProjectAI."""

from __future__ import annotations

import math
import re
from typing import Any

from core.interfaces import ToolInterface

class MathEvaluationError(ValueError):
    """Raised when a mathematical expression cannot be evaluated."""

class MathTool(ToolInterface):
    """Safely evaluate basic mathematical expressions."""

    _NUMBER_PATTERN = re.compile(
        r"""
        (?:(?:\d+(?:\.\d*)?) | (?:\.\d+))
        """,
        re.VERBOSE,
    )

    _OPERATORS = {
        "+": {
            "precedence": 1,
            "associativity": "left",
            "arity": 2,
        },
        "-": {
            "precedence": 1,
            "associativity": "left",
            "arity": 2,
        },
        "*": {
            "precedence": 2,
            "associativity": "left",
            "arity": 2,
        },
        "/": {
            "precedence": 2,
            "associativity": "left",
            "arity": 2,
        },
        "%": {
            "precedence": 2,
            "associativity": "left",
            "arity": 2,
        },
        "**": {
            "precedence": 3,
            "associativity": "right",
            "arity": 2,
        },
        "u+": {
            "precedence": 4,
            "associativity": "right",
            "arity": 1,
        },
        "u-": {
            "precedence": 4,
            "associativity": "right",
            "arity": 1,
        },
    }

    @property
    def name(self) -> str:
        return "math"

    @property
    def description(self) -> str:
        return (
            "Safely evaluates basic mathematical expressions "
            "using +, -, *, /, %, ** and parentheses."
        )

    def execute(self, inputs: dict[str, Any]) -> float | int:
        """Evaluate a mathematical expression."""

        if not isinstance(inputs, dict):
            raise TypeError("Math inputs must be a dictionary.")

        expression = inputs.get("expression")
        if not isinstance(expression, str):
            raise TypeError("Math input 'expression' must be a string.")

        expression = expression.strip()
        if not expression:
            raise MathEvaluationError("Mathematical expression must not be empty.")

        return self._evaluate(expression)

    def _evaluate(self, expression: str) -> float | int:
        tokens = self._tokenize(expression)
        rpn = self._to_rpn(tokens)
        return self._evaluate_rpn(rpn)

    def _tokenize(self, expression: str) -> list[str]:
        """Convert an expression into safe tokens."""

        tokens: list[str] = []
        index = 0
        while index < len(expression):
            character = expression[index]
            if character.isspace():
                index += 1
                continue

            number_match = self._NUMBER_PATTERN.match(
                expression,
                index,
            )
            if number_match:
                tokens.append(number_match.group(0))
                index = number_match.end()
                continue

            if expression.startswith("**", index):
                tokens.append("**")
                index += 2
                continue

            if character in "+-*/%()":
                tokens.append(character)
                index += 1
                continue

            raise MathEvaluationError(
                f"Unsupported character '{character}'."
            )

        if not tokens:
            raise MathEvaluationError("Mathematical expression contains no valid tokens.")

        return self._resolve_unary_operators(tokens)

    def _resolve_unary_operators(
        self,
        tokens: list[str],
    ) -> list[str]:
        """Convert unary + and - into explicit operators."""

        resolved: list[str] = []
        previous: str | None = None

        for token in tokens:
            if token in {"+", "-"}:
                is_unary = (
                    previous is None
                    or previous in self._OPERATORS
                    or previous == "("
                )
                if is_unary:
                    token = "u+" if token == "+" else "u-"

            resolved.append(token)
            previous = token

        return resolved

    def _to_rpn(self, tokens: list[str]) -> list[str]:
        """Convert infix tokens to Reverse Polish Notation."""

        output: list[str] = []
        operators: list[str] = []

        for token in tokens:
            if self._is_number(token):
                output.append(token)
                continue

            if token == "(":
                operators.append(token)
                continue

            if token == ")":
                while operators and operators[-1] != "(":
                    output.append(operators.pop())

                if not operators:
                    raise MathEvaluationError("Mismatched parentheses.")

                operators.pop()
                continue

            if token not in self._OPERATORS:
                raise MathEvaluationError(f"Unsupported operator '{token}'.")

            while operators and operators[-1] != "(":
                top = operators[-1]

                if self._should_pop_operator(token, top):
                    output.append(operators.pop())
                else:
                    break

            operators.append(token)

        while operators:
            operator = operators.pop()
            if operator in {"(", ")"}:
                raise MathEvaluationError("Mismatched parentheses.")
            output.append(operator)

        return output

    def _should_pop_operator(
        self,
        current: str,
        top: str,
    ) -> bool:
        """Determine operator precedence behavior."""

        current_info = self._OPERATORS[current]
        top_info = self._OPERATORS[top]

        current_precedence = current_info["precedence"]
        top_precedence = top_info["precedence"]

        if current_info["associativity"] == "left":
            return current_precedence <= top_precedence

        return current_precedence < top_precedence

    def _evaluate_rpn(self, tokens: list[str]) -> float | int:
        """Evaluate Reverse Polish Notation."""

        stack: list[float | int] = []

        for token in tokens:
            if self._is_number(token):
                stack.append(self._parse_number(token))
                continue

            operator = self._OPERATORS[token]
            arity = operator["arity"]

            if len(stack) < arity:
                raise MathEvaluationError("Invalid mathematical expression.")
            if arity == 1:
                value = stack.pop()
                
                if token == "u+":
                    stack.append(+value)
                elif token == "u-":
                    stack.append(-value)
                else:
                    raise MathEvaluationError(f"Unsupported unary operator '{token}'.")

                continue

            right = stack.pop()
            left = stack.pop()
            stack.append(
                self._apply_binary_operator(
                    token,
                    left,
                    right,
                )
            )

        if len(stack) != 1:
            raise MathEvaluationError("Invalid mathematical expression.")

        result = stack[0]

        if isinstance(result, float) and result.is_integer():
            return int(result)

        return result

    @staticmethod
    def _apply_binary_operator(
        operator: str,
        left: float | int,
        right: float | int,
    ) -> float | int:
        """Apply an allowed binary operator."""

        if operator == "+":
            return left + right
        if operator == "-":
            return left - right
        if operator == "*":
            return left * right
        if operator == "/":
            if right == 0:
                raise MathEvaluationError("Division by zero is not allowed.")
            return left / right
        if operator == "%":
            if right == 0:
                raise MathEvaluationError("Modulo by zero is not allowed.")
            return left % right
        if operator == "**":
            try:
                result = left**right
            except (OverflowError, ValueError) as exc:
                raise MathEvaluationError("Power operation failed.") from exc

            if isinstance(result, complex):
                raise MathEvaluationError("Complex results are not supported.")

            if not math.isfinite(float(result)):
                raise MathEvaluationError("Result is outside the supported numeric range.")

            return result

        raise MathEvaluationError(f"Unsupported operator '{operator}'.")

    @staticmethod
    def _is_number(token: str) -> bool:
        return bool(
            re.fullmatch(r"(?:\d+(?:\.\d*)?|\.\d+)", token)
        )

    @staticmethod
    def _parse_number(token: str) -> float | int:
        value = float(token)
        if value.is_integer() and "." not in token:
            return int(value)

        return value