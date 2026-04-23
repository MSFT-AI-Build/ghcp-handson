"""Native tools registered directly with the agent."""
from __future__ import annotations

import ast
import operator as op
from typing import Annotated

from agent_framework import tool

_BIN_OPS: dict[type[ast.operator], object] = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.FloorDiv: op.floordiv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
}
_UNARY_OPS: dict[type[ast.unaryop], object] = {
    ast.UAdd: op.pos,
    ast.USub: op.neg,
}


def _safe_eval(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
        return _BIN_OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))  # type: ignore[operator]
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_safe_eval(node.operand))  # type: ignore[operator]
    raise ValueError("Unsupported expression element")


def _evaluate(expression: str) -> float:
    expression = (expression or "").strip()
    if not expression:
        raise ValueError("expression is empty")
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"invalid expression: {exc.msg}") from exc
    return _safe_eval(tree)


@tool(
    name="calculate",
    description=(
        "Evaluate a basic arithmetic expression "
        "(supports + - * / // % ** and parentheses)."
    ),
)
def calculate(
    expression: Annotated[
        str, "Arithmetic expression to evaluate, e.g. '1 + 2 * (3 - 4)'."
    ],
) -> str:
    """Return the numeric result of the expression as a string."""
    try:
        value = _evaluate(expression)
    except ZeroDivisionError:
        return "error: division by zero"
    except ValueError as exc:
        return f"error: {exc}"
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return str(value)
