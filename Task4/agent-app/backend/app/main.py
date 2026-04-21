"""FastAPI application entrypoint."""
from __future__ import annotations

import json
from typing import AsyncIterator

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .agents import get_supervisor_agent
from .schemas import ChatRequest, ChatResponse, HealthResponse


def create_app() -> FastAPI:
    app = FastAPI(title="Agent System API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        return HealthResponse()

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


async def _sse_stream(agent: object, message: str) -> AsyncIterator[str]:
    """Yield SSE events streaming agent updates as text deltas."""
    try:
        stream = agent.run(message, stream=True)  # type: ignore[attr-defined]
        async for update in stream:
            delta = _extract_text(update)
            if delta:
                yield _sse("delta", {"text": delta})
    except Exception as exc:  # noqa: BLE001
        yield _sse("error", {"detail": str(exc)})
        return
    yield _sse("done", {})


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
