"""Tests for MathTool."""

import pytest

from self_built.tools.math_tool import (
    MathEvaluationError,
    MathTool,
)


@pytest.fixture
def math_tool() -> MathTool:
    return MathTool()


def test_addition(math_tool: MathTool) -> None:
    assert math_tool.execute({"expression": "2 + 3"}) == 5


def test_subtraction(math_tool: MathTool) -> None:
    assert math_tool.execute({"expression": "10 - 4"}) == 6


def test_multiplication(math_tool: MathTool) -> None:
    assert math_tool.execute({"expression": "6 * 7"}) == 42


def test_division(math_tool: MathTool) -> None:
    assert math_tool.execute({"expression": "20 / 5"}) == 4


def test_modulo(math_tool: MathTool) -> None:
    assert math_tool.execute({"expression": "17 % 5"}) == 2


def test_power(math_tool: MathTool) -> None:
    assert math_tool.execute({"expression": "2 ** 8"}) == 256


def test_parentheses(math_tool: MathTool) -> None:
    assert math_tool.execute(
        {"expression": "(2 + 3) * 4"}
    ) == 20


def test_decimal(math_tool: MathTool) -> None:
    assert math_tool.execute(
        {"expression": "2.5 * 4"}
    ) == 10


def test_operator_precedence(math_tool: MathTool) -> None:
    assert math_tool.execute(
        {"expression": "2 + 3 * 4"}
    ) == 14


def test_unary_minus(math_tool: MathTool) -> None:
    assert math_tool.execute(
        {"expression": "-5 + 2"}
    ) == -3


def test_unary_parentheses(math_tool: MathTool) -> None:
    assert math_tool.execute(
        {"expression": "-(5 + 2)"}
    ) == -7


def test_right_associative_power(math_tool: MathTool) -> None:
    assert math_tool.execute(
        {"expression": "2 ** 3 ** 2"}
    ) == 512


def test_whitespace_is_supported(math_tool: MathTool) -> None:
    assert math_tool.execute(
        {"expression": " 10   +   5 "}
    ) == 15


def test_division_by_zero_fails(math_tool: MathTool) -> None:
    with pytest.raises(
        MathEvaluationError,
        match="Division by zero",
    ):
        math_tool.execute(
            {"expression": "10 / 0"}
        )


def test_modulo_by_zero_fails(math_tool: MathTool) -> None:
    with pytest.raises(
        MathEvaluationError,
        match="Modulo by zero",
    ):
        math_tool.execute(
            {"expression": "10 % 0"}
        )


def test_invalid_character_fails(math_tool: MathTool) -> None:
    with pytest.raises(
        MathEvaluationError,
        match="Unsupported character",
    ):
        math_tool.execute(
            {"expression": "2 + abc"}
        )


def test_invalid_parentheses_fail(math_tool: MathTool) -> None:
    with pytest.raises(
        MathEvaluationError,
        match="Mismatched parentheses",
    ):
        math_tool.execute(
            {"expression": "(2 + 3"}
        )


def test_invalid_expression_fails(math_tool: MathTool) -> None:
    with pytest.raises(
        MathEvaluationError,
        match="Invalid mathematical expression",
    ):
        math_tool.execute(
            {"expression": "2 +"}
        )


def test_empty_expression_fails(math_tool: MathTool) -> None:
    with pytest.raises(
        MathEvaluationError,
        match="must not be empty",
    ):
        math_tool.execute(
            {"expression": ""}
        )


def test_expression_input_must_be_string(
    math_tool: MathTool,
) -> None:
    with pytest.raises(
        TypeError,
        match="must be a string",
    ):
        math_tool.execute(
            {"expression": 123}  # type: ignore[arg-type]
        )


def test_eval_is_not_used(math_tool: MathTool) -> None:
    # The tool must reject Python expressions rather than execute them.
    with pytest.raises(MathEvaluationError):
        math_tool.execute(
            {"expression": "__import__('os')"}
        )