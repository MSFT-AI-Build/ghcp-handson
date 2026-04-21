"""Tests for the FastAPI app with a mocked supervisor agent."""
from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.agents import get_supervisor_agent
from app.main import app


class _FakeAgent:
    def __init__(self, reply: str = "hello from fake agent") -> None:
        self.reply = reply
        self.calls: list[str] = []
        self.stream_chunks: list[str] = ["hello", " from", " fake", " stream"]

    def run(self, message: str, *, stream: bool = False):
        self.calls.append(message)
        if stream:
            chunks = self.stream_chunks

            async def _gen():
                for c in chunks:
                    yield SimpleNamespace(text=c)

            return _gen()

        async def _await():
            return SimpleNamespace(text=self.reply)

        return _await()


@pytest.fixture
def fake_agent():
    fake = _FakeAgent()
    app.dependency_overrides[get_supervisor_agent] = lambda: fake
    yield fake
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


def test_health_returns_ok(client: TestClient) -> None:
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_chat_success(client: TestClient, fake_agent: _FakeAgent) -> None:
    res = client.post("/api/chat", json={"message": "hi"})
    assert res.status_code == 200
    body = res.json()
    assert body == {"role": "assistant", "message": "hello from fake agent"}
    assert fake_agent.calls == ["hi"]


def test_chat_rejects_empty_message(client: TestClient, fake_agent: _FakeAgent) -> None:
    res = client.post("/api/chat", json={"message": ""})
    assert res.status_code == 422


def test_chat_rejects_missing_field(client: TestClient, fake_agent: _FakeAgent) -> None:
    res = client.post("/api/chat", json={})
    assert res.status_code == 422


def test_chat_invalid_json(client: TestClient, fake_agent: _FakeAgent) -> None:
    res = client.post(
        "/api/chat",
        content="not-json",
        headers={"content-type": "application/json"},
    )
    assert res.status_code == 422


def test_chat_propagates_agent_failure(client: TestClient) -> None:
    class _Boom:
        def run(self, message: str, *, stream: bool = False):
            async def _raise():
                raise RuntimeError("upstream failure")

            return _raise()

    app.dependency_overrides[get_supervisor_agent] = lambda: _Boom()
    try:
        res = client.post("/api/chat", json={"message": "hi"})
        assert res.status_code == 502
        assert "upstream failure" in res.json()["detail"]
    finally:
        app.dependency_overrides.clear()


def test_chat_stream_emits_deltas(client: TestClient, fake_agent: _FakeAgent) -> None:
    with client.stream(
        "POST", "/api/chat/stream", json={"message": "hi"}
    ) as res:
        assert res.status_code == 200
        assert res.headers["content-type"].startswith("text/event-stream")
        body = "".join(res.iter_text())

    assert "event: delta" in body
    assert "event: done" in body
    for chunk in fake_agent.stream_chunks:
        assert chunk in body
    assert fake_agent.calls == ["hi"]
