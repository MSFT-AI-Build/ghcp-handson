"""Tests for the FastAPI app with a mocked supervisor agent."""
from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.agents import get_supervisor_agent
from app.main import app
from app.mcp_client import MCPClientManager, reset_mcp_manager, set_mcp_manager


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
def test_chat_stream_emits_tool_events(client: TestClient) -> None:
    class _ToolAgent:
        def __init__(self) -> None:
            self.calls: list[str] = []

        def run(self, message: str, *, stream: bool = False):
            self.calls.append(message)

            async def _gen():
                yield SimpleNamespace(
                    text="",
                    tool_events=[
                        {
                            "name": "calculate",
                            "type": "native",
                            "arguments": {"expression": "1+1"},
                            "result": "2",
                        }
                    ],
                )
                yield SimpleNamespace(text="ok")

            return _gen()

    agent = _ToolAgent()
    app.dependency_overrides[get_supervisor_agent] = lambda: agent
    try:
        with client.stream("POST", "/api/chat/stream", json={"message": "hi"}) as res:
            assert res.status_code == 200
            body = "".join(res.iter_text())
    finally:
        app.dependency_overrides.clear()

    assert "event: tool" in body
    assert "calculate" in body
    assert "event: delta" in body


def test_chat_stream_extracts_function_call_contents(client: TestClient) -> None:
    """Streaming updates with agent_framework-style ``contents`` are surfaced."""

    class _ContentAgent:
        def run(self, message: str, *, stream: bool = False):
            async def _gen():
                yield SimpleNamespace(
                    text="",
                    contents=[
                        SimpleNamespace(
                            type="function_call",
                            name="calculate",
                            arguments={"expression": "2*3"},
                            result=None,
                        )
                    ],
                )
                yield SimpleNamespace(text="six")

            return _gen()

    app.dependency_overrides[get_supervisor_agent] = lambda: _ContentAgent()
    try:
        with client.stream("POST", "/api/chat/stream", json={"message": "hi"}) as res:
            body = "".join(res.iter_text())
    finally:
        app.dependency_overrides.clear()

    assert "event: tool" in body
    assert "calculate" in body
    assert "2*3" in body


def test_chat_stream_normalizes_mcp_bridge_call(client: TestClient) -> None:
    """A call to ``mcp_call_tool`` is rewritten so server + tool are surfaced."""

    class _BridgeAgent:
        def run(self, message: str, *, stream: bool = False):
            async def _gen():
                yield SimpleNamespace(
                    text="",
                    tool_events=[
                        {
                            "name": "mcp_call_tool",
                            "type": "function_call",
                            "arguments": {
                                "server": "notion",
                                "tool": "search",
                                "arguments": {"query": "roadmap"},
                            },
                        }
                    ],
                )
                yield SimpleNamespace(text="done")

            return _gen()

    app.dependency_overrides[get_supervisor_agent] = lambda: _BridgeAgent()
    try:
        with client.stream("POST", "/api/chat/stream", json={"message": "hi"}) as res:
            body = "".join(res.iter_text())
    finally:
        app.dependency_overrides.clear()

    assert "event: tool" in body
    assert '"server": "notion"' in body
    assert '"name": "search"' in body
    assert '"type": "mcp"' in body
    # Original wrapper name must not leak through
    assert "mcp_call_tool" not in body


def test_chat_stream_aggregates_streamed_tool_call(client: TestClient) -> None:
    """Partial function_call/function_result chunks collapse into one event."""

    class _StreamingAgent:
        def run(self, message: str, *, stream: bool = False):
            async def _gen():
                # Name + opening of args
                yield SimpleNamespace(
                    text="",
                    contents=[
                        SimpleNamespace(
                            type="function_call",
                            call_id="c1",
                            name="calculate",
                            arguments='{"expression":',
                        )
                    ],
                )
                # Continuation of args
                yield SimpleNamespace(
                    text="",
                    contents=[
                        SimpleNamespace(
                            type="function_call",
                            call_id="c1",
                            name=None,
                            arguments='"2*3"}',
                        )
                    ],
                )
                # Result for the same call
                yield SimpleNamespace(
                    text="",
                    contents=[
                        SimpleNamespace(
                            type="function_result",
                            call_id="c1",
                            name="calculate",
                            result="6",
                        )
                    ],
                )
                yield SimpleNamespace(text="six")

            return _gen()

    app.dependency_overrides[get_supervisor_agent] = lambda: _StreamingAgent()
    try:
        with client.stream("POST", "/api/chat/stream", json={"message": "hi"}) as res:
            body = "".join(res.iter_text())
    finally:
        app.dependency_overrides.clear()

    # Exactly one tool event for call_id c1, with merged args + result.
    assert body.count("event: tool") == 1
    assert '"expression": "2*3"' in body
    assert '"result": "6"' in body


def test_list_tools_endpoint(client: TestClient) -> None:
    class _RegistryFake(MCPClientManager):
        def __init__(self) -> None:
            super().__init__({"mcpServers": {"notion": {"command": "npx"}}})
            self._status["notion"] = "connected"
            self._tool_cache["notion"] = [
                {"name": "search", "description": "search pages"}
            ]

    set_mcp_manager(_RegistryFake())
    try:
        res = client.get("/api/tools")
    finally:
        reset_mcp_manager()

    assert res.status_code == 200
    body = res.json()
    names = [t["name"] for t in body["tools"]]
    assert "calculate" in names
    assert "mcp_list_tools" in names
    assert "mcp_call_tool" in names
    servers = {s["name"]: s for s in body["mcp_servers"]}
    assert servers["notion"]["status"] == "connected"
    assert servers["notion"]["tools"][0]["name"] == "search"
