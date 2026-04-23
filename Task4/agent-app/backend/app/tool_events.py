"""Shared tool-event aggregation helpers used by main.py and worker_manager.py.

``ToolEventAggregator`` collapses the many partial ``function_call`` /
``function_result`` content chunks emitted by ``agent_framework`` streams into
one finalized event per ``call_id``.

``normalize_mcp_bridge`` unwraps ``mcp_call_tool`` calls so the UI sees the
*inner* MCP server/tool name rather than the bridge wrapper.
"""
from __future__ import annotations

import json
from typing import Any


def _stringify(value: object) -> object:
    """Render tool results in a UI-friendly way without losing structure."""
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (list, tuple)):
        return [_stringify(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _stringify(v) for k, v in value.items()}
    for attr in ("text", "value", "output"):
        v = getattr(value, attr, None)
        if v is not None:
            return _stringify(v)
    return repr(value)


def normalize_mcp_bridge(event: dict) -> dict:
    """If the event is a call to ``mcp_call_tool``, surface server/tool from arguments."""
    if event.get("name") != "mcp_call_tool":
        return event
    args = event.get("arguments")
    parsed: dict | None = None
    if isinstance(args, dict):
        parsed = args
    elif isinstance(args, str):
        try:
            parsed = json.loads(args)
        except (ValueError, TypeError):
            parsed = None
    if not isinstance(parsed, dict):
        return event
    server = parsed.get("server")
    tool = parsed.get("tool") or parsed.get("name")
    if not (server and tool):
        return event
    inner_args = parsed.get("arguments")
    return {
        "name": tool,
        "type": "mcp",
        "server": server,
        "arguments": inner_args,
        "result": event.get("result"),
    }


class ToolEventAggregator:
    """Collapse the many partial function_call/function_result chunks emitted by
    ``agent_framework`` streams into one finalized event per ``call_id``.
    """

    def __init__(self) -> None:
        self._calls: dict[str, dict] = {}
        self._emitted: set[str] = set()
        self._anon = 0

    def consume(self, update: object) -> list[dict]:
        out: list[dict] = []

        # Pre-aggregated sources (used by tests / non-streaming callers).
        raw = getattr(update, "tool_events", None) or getattr(
            update, "function_calls", None
        )
        if raw:
            for item in raw:
                if isinstance(item, dict) and item.get("name"):
                    event = {
                        k: item.get(k)
                        for k in ("name", "type", "server", "arguments", "result")
                        if k in item
                    }
                    out.append(normalize_mcp_bridge(event))

        # Streaming Content items from agent_framework.
        for c in getattr(update, "contents", None) or []:
            ctype = getattr(c, "type", None)
            if ctype == "function_call":
                self._absorb_call(c)
            elif ctype == "function_result":
                event = self._absorb_result(c)
                if event is not None:
                    out.append(event)
            elif getattr(c, "tool_name", None):
                # Hosted MCP tool result content.
                out.append(
                    {
                        "name": c.tool_name,
                        "type": "mcp",
                        "server": getattr(c, "server_name", None),
                        "result": _stringify(getattr(c, "output", None)),
                    }
                )
        return out

    def flush(self) -> list[dict]:
        out: list[dict] = []
        for call_id, info in self._calls.items():
            if call_id in self._emitted or not info.get("name"):
                continue
            out.append(self._finalize(info, result=None))
            self._emitted.add(call_id)
        return out

    def _absorb_call(self, content: object) -> None:
        call_id = getattr(content, "call_id", None) or self._anon_id()
        info = self._calls.setdefault(
            call_id, {"name": None, "args_buf": "", "args_obj": None}
        )
        name = getattr(content, "name", None)
        if name and not info["name"]:
            info["name"] = name
        args = getattr(content, "arguments", None)
        if isinstance(args, str):
            info["args_buf"] += args
        elif isinstance(args, dict):
            info["args_obj"] = args

    def _absorb_result(self, content: object) -> dict | None:
        call_id = getattr(content, "call_id", None) or self._anon_id()
        info = self._calls.setdefault(
            call_id, {"name": None, "args_buf": "", "args_obj": None}
        )
        if not info["name"]:
            info["name"] = getattr(content, "name", None)
        result = getattr(content, "result", None)
        if call_id in self._emitted or not info.get("name"):
            return None
        self._emitted.add(call_id)
        return self._finalize(info, result=result)

    def _finalize(self, info: dict, result: object) -> dict:
        args = info["args_obj"]
        if args is None and info["args_buf"]:
            try:
                args = json.loads(info["args_buf"])
            except (ValueError, TypeError):
                args = info["args_buf"]
        event: dict[str, Any] = {
            "name": info["name"],
            "type": "function_call",
            "arguments": args,
            "result": _stringify(result),
        }
        return normalize_mcp_bridge(event)

    def _anon_id(self) -> str:
        self._anon += 1
        return f"_anon_{self._anon}"
