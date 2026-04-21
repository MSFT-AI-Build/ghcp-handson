"""FastAPI application entrypoint."""
from __future__ import annotations

import json
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .agents import get_supervisor_agent
from .mcp_client import get_mcp_manager
from .schemas import ChatRequest, ChatResponse, HealthResponse
from .tools import build_tools_overview

logger = logging.getLogger(__name__)


@asynccontextmanager
async def _lifespan(_: FastAPI):
    manager = get_mcp_manager()
    try:
        await manager.connect_all()
    except Exception as exc:  # noqa: BLE001
        logger.warning("MCP connect_all failed: %s", exc)
    try:
        yield
    finally:
        await manager.aclose()


def create_app() -> FastAPI:
    app = FastAPI(title="Agent System API", version="0.1.0", lifespan=_lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        return HealthResponse()

    @app.get("/api/tools")
    async def list_tools() -> dict:
        return build_tools_overview()

    @app.post("/api/chat", response_model=ChatResponse)
    async def chat(
        payload: ChatRequest,
        agent=Depends(get_supervisor_agent),
    ) -> ChatResponse:
        try:
            result = await agent.run(payload.message)
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        return ChatResponse(message=_extract_text(result))

    @app.post("/api/chat/stream")
    async def chat_stream(
        payload: ChatRequest,
        agent=Depends(get_supervisor_agent),
    ) -> StreamingResponse:
        return StreamingResponse(
            _sse_stream(agent, payload.message),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    return app


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


class _ToolEventAggregator:
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
                    out.append(_normalize_mcp_bridge(event))

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
        event = {
            "name": info["name"],
            "type": "function_call",
            "arguments": args,
            "result": _stringify(result),
        }
        return _normalize_mcp_bridge(event)

    def _anon_id(self) -> str:
        self._anon += 1
        return f"_anon_{self._anon}"


async def _sse_stream(agent: object, message: str) -> AsyncIterator[str]:
    """Yield SSE events streaming agent updates as text deltas + tool events."""
    aggregator = _ToolEventAggregator()
    tool_count = 0
    try:
        stream = agent.run(message, stream=True)  # type: ignore[attr-defined]
        async for update in stream:
            for event in aggregator.consume(update):
                tool_count += 1
                logger.info(
                    "tool event #%d -> %s/%s",
                    tool_count,
                    event.get("server") or "native",
                    event.get("name"),
                )
                yield _sse("tool", event)
            delta = _extract_text(update)
            if delta:
                yield _sse("delta", {"text": delta})
        for event in aggregator.flush():
            tool_count += 1
            logger.info(
                "tool event (flush) #%d -> %s/%s",
                tool_count,
                event.get("server") or "native",
                event.get("name"),
            )
            yield _sse("tool", event)
    except Exception as exc:  # noqa: BLE001
        logger.exception("stream failed")
        yield _sse("error", {"detail": str(exc)})
        return
    logger.info("stream finished, %d tool event(s) emitted", tool_count)
    yield _sse("done", {})


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
    # MCP CallToolResult / dataclass-ish objects: try common attrs.
    for attr in ("text", "value", "output"):
        v = getattr(value, attr, None)
        if v is not None:
            return _stringify(v)
    return repr(value)


def _extract_tool_events(update: object) -> list[dict]:
    """Backwards-compatible single-shot extractor used by tests."""
    return _ToolEventAggregator().consume(update)


def _normalize_mcp_bridge(event: dict) -> dict:
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


def _extract_text(result: object) -> str:
    """Best-effort extraction of assistant text from an Agent run result/update."""
    for attr in ("text", "output_text", "content", "delta"):
        value = getattr(result, attr, None)
        if isinstance(value, str) and value:
            return value
    messages = getattr(result, "messages", None)
    if messages:
        last = messages[-1]
        text = getattr(last, "text", None) or getattr(last, "content", None)
        if isinstance(text, str):
            return text
    return ""


app = create_app()
