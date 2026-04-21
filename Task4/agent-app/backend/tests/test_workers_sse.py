"""Tests for the worker SSE events on /api/chat/stream and /api/agents."""
from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.agents import get_supervisor_agent
from app.main import app


class _FakeAgent:
    """Stub supervisor agent that triggers a worker via the contextvar bound
    by the chat_stream handler."""

    def __init__(self, after_run=None) -> None:
        self.after_run = after_run

    def run(self, message: str, *, stream: bool = False):
        async def _gen():
            yield SimpleNamespace(text="hi")
            if self.after_run is not None:
                await self.after_run()

        return _gen()


@pytest.fixture
def client():
    return TestClient(app)


def test_chat_stream_emits_worker_status_events(client: TestClient) -> None:
    """When the supervisor delegates, status events flow to the SSE channel."""
    from app.tools.delegation import get_active_worker_manager

    async def trigger() -> None:
        mgr = get_active_worker_manager()
        # Replace factory so we don't hit real OpenAIChatClient.
        mgr._factory = lambda *_: _StubWorker()  # type: ignore[attr-defined]
        await mgr.delegate(task="research", role="Researcher", instructions="dig in")

    fake = _FakeAgent(after_run=trigger)
    app.dependency_overrides[get_supervisor_agent] = lambda: fake
    try:
        with client.stream("POST", "/api/chat/stream", json={"message": "hi"}) as res:
            body = "".join(res.iter_text())
    finally:
        app.dependency_overrides.clear()

    assert "event: worker" in body
    assert "Researcher" in body
    # All three key transitions appear in the stream
    assert '"status": "pending"' in body
    assert '"status": "running"' in body
    assert '"status": "completed"' in body
    assert "event: done" in body


class _StubWorker:
    def run(self, message: str):
        async def _await():
            return type("R", (), {"text": "research-done"})()

        return _await()


def test_agents_endpoint_returns_supervisor_info(client: TestClient) -> None:
    res = client.get("/api/agents")
    assert res.status_code == 200
    body = res.json()
    assert body["supervisor"]["id"] == "supervisor"
    assert "delegate_task" in body["supervisor"]["tools"]
    assert "supervisor" in body["supervisor"]["work_dir"]
    assert body["workers"] == []
