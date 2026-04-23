"""Tests for native tool implementations."""
from __future__ import annotations

import pytest

from app.tools.native import _evaluate, calculate


class TestEvaluate:
    def test_basic_arithmetic(self) -> None:
        assert _evaluate("1 + 2 * 3") == 7

    def test_true_division(self) -> None:
        assert _evaluate("10 / 4") == 2.5

    def test_floor_division(self) -> None:
        assert _evaluate("10 // 3") == 3

    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError):
            _evaluate("")

    def test_function_call_rejected(self) -> None:
        with pytest.raises(ValueError):
            _evaluate("foo()")

    def test_division_by_zero(self) -> None:
        with pytest.raises(ZeroDivisionError):
            _evaluate("1/0")


class TestCalculateTool:
    def test_happy_path(self) -> None:
        assert calculate(expression="2+2") == "4"

    def test_empty_returns_error(self) -> None:
        assert calculate(expression="").startswith("error:")

    def test_division_by_zero_returns_error(self) -> None:
        assert calculate(expression="1/0") == "error: division by zero"
