"""FastAPI application entrypoint."""
from __future__ import annotations

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .agents import (
    AGENT_ID,
    SUPERVISOR_INSTRUCTIONS,
    append_supervisor_memory,
    build_worker_agent,
    extract_memory_saves,
    get_supervisor_agent,
    inject_memory_into_message,
    load_supervisor_memory,
)
from .mcp_client import get_mcp_manager
from .schemas import ChatRequest, ChatResponse, HealthResponse
from .tool_events import ToolEventAggregator, normalize_mcp_bridge
from .tools import (
    build_tools_overview,
    reset_active_worker_manager,
    set_active_worker_manager,
)
from .work_dir import WORK_DIRS_ROOT
from .worker_manager import WorkerManager

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

    @app.get("/api/agents")
    async def list_agents() -> dict:
        return {
            "supervisor": {
                "id": AGENT_ID,
                "role": "Supervisor Agent",
                "work_dir": str(WORK_DIRS_ROOT / AGENT_ID),
                "tools": ["delegate_task", "check_workers", "cancel_worker"],
            },
            # Workers are short-lived (per request); their snapshots are
            # streamed live over /api/chat/stream as ``event: worker``.
            "workers": [],
        }

    @app.post("/api/chat", response_model=ChatResponse)
    async def chat(
        payload: ChatRequest,
        agent=Depends(get_supervisor_agent),
    ) -> ChatResponse:
        manager = WorkerManager(worker_factory=build_worker_agent)
        token = set_active_worker_manager(manager)
        try:
            memory = load_supervisor_memory()
            user_msg = inject_memory_into_message(payload.message, memory)
            try:
                result = await agent.run(user_msg)
            except Exception as exc:  # noqa: BLE001
                raise HTTPException(status_code=502, detail=str(exc)) from exc
            text = _extract_text(result)
            visible, saves = extract_memory_saves(text)
            if saves:
                try:
                    append_supervisor_memory(saves)
                except OSError as exc:
                    logger.warning("Failed to persist supervisor memory: %s", exc)
            return ChatResponse(message=visible)
        finally:
            reset_active_worker_manager(token)

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


# Sentinel object used to signal the SSE output queue that streaming is done.
_SSE_DONE_SENTINEL: object = object()


class _ToolEventAggregator(ToolEventAggregator):
    """Backwards-compat alias kept so existing tests that reference the private
    name continue to work.  New code should import ``ToolEventAggregator``
    from ``.tool_events`` directly.
    """


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
    """Yield SSE events streaming agent updates as text deltas + tool/worker events.

    A background *pump_workers* task runs concurrently with the main agent
    stream so that worker status transitions (pending → running → completed)
    are forwarded to the client in real-time, even while ``delegate_task``
    is blocking the agent stream awaiting a worker result.
    """
    aggregator = _ToolEventAggregator()
    worker_manager = WorkerManager(worker_factory=build_worker_agent)
    token = set_active_worker_manager(worker_manager)
    full_text_chunks: list[str] = []
    tool_count = 0
    error_occurred = False

    # Shared output queue written by both run_main and pump_workers.
    out: asyncio.Queue[object] = asyncio.Queue()
    main_done = asyncio.Event()

    async def run_main() -> None:
        nonlocal tool_count, error_occurred
        try:
            memory = load_supervisor_memory()
            user_msg = inject_memory_into_message(message, memory)
            stream = agent.run(user_msg, stream=True)  # type: ignore[attr-defined]
            async for update in stream:
                for event in aggregator.consume(update):
                    tool_count += 1
                    logger.info(
                        "tool event #%d -> %s/%s",
                        tool_count,
                        event.get("server") or "native",
                        event.get("name"),
                    )
                    await out.put(_sse("tool", event))
                delta = _extract_text(update)
                if delta:
                    full_text_chunks.append(delta)
                    await out.put(_sse("delta", {"text": delta}))
            for event in aggregator.flush():
                tool_count += 1
                await out.put(_sse("tool", event))
        except Exception as exc:  # noqa: BLE001
            logger.exception("stream failed")
            await out.put(_sse("error", {"detail": str(exc)}))
            error_occurred = True
        finally:
            main_done.set()

    async def pump_workers() -> None:
        """Forward worker events to the output queue until main stream is done.

        Runs concurrently with *run_main* so that pending→running→completed
        status transitions reach the client while ``delegate_task`` is still
        blocking the agent loop awaiting the worker result.

        Worker tool-call events (``type == "worker_tool"``) are forwarded as
        ``event: worker_tool`` SSE frames so the client can render them
        separately from worker status cards.
        """
        while True:
            if main_done.is_set():
                # Main stream finished — drain any remaining events and stop.
                for w_evt in worker_manager.drain_events():
                    sse_type = "worker_tool" if w_evt.get("type") == "worker_tool" else "worker"
                    await out.put(_sse(sse_type, w_evt))
                break
            w_evt = await worker_manager.next_event(timeout=0.05)
            if w_evt is not None:
                sse_type = "worker_tool" if w_evt.get("type") == "worker_tool" else "worker"
                await out.put(_sse(sse_type, w_evt))
        await out.put(_SSE_DONE_SENTINEL)

    main_task = asyncio.create_task(run_main())
    pump_task = asyncio.create_task(pump_workers())

    try:
        while True:
            item = await out.get()
            if item is _SSE_DONE_SENTINEL:
                break
            yield item  # type: ignore[misc]
    finally:
        # Cancel background tasks (no-op if they already completed normally).
        main_task.cancel()
        pump_task.cancel()
        reset_active_worker_manager(token)
        await asyncio.gather(main_task, pump_task, return_exceptions=True)

    if error_occurred:
        return

    # Persist any [MEMORY_SAVE] markers from the accumulated assistant text.
    full_text = "".join(full_text_chunks)
    _, saves = extract_memory_saves(full_text)
    if saves:
        try:
            append_supervisor_memory(saves)
        except OSError as exc:
            logger.warning("Failed to persist supervisor memory: %s", exc)
    logger.info("stream finished, %d tool event(s) emitted", tool_count)
    yield _sse("done", {})


def _stringify(value: object) -> object:
    """Render tool results in a UI-friendly way without losing structure.

    Kept here for backwards-compatibility with any callers that import it from
    this module.  New code should use ``tool_events._stringify`` directly via
    the aggregator.
    """
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


def _extract_tool_events(update: object) -> list[dict]:
    """Backwards-compatible single-shot extractor used by tests."""
    return ToolEventAggregator().consume(update)


def _normalize_mcp_bridge(event: dict) -> dict:
    """Backwards-compat shim; delegates to the shared implementation."""
    return normalize_mcp_bridge(event)


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
