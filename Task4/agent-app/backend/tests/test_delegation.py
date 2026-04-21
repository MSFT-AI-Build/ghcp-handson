"""Tests for the Supervisor delegation native tools."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.tools.delegation import (
    cancel_worker,
    check_workers,
    delegate_task,
    get_active_worker_manager,
    reset_active_worker_manager,
    set_active_worker_manager,
)
from app.worker_manager import WorkerManager


class FakeWorker:
    def __init__(self, reply: str) -> None:
        self.reply = reply

    def run(self, message: str):
        async def _run():
            return type("R", (), {"text": self.reply})()

        return _run()


@pytest.fixture
def manager(tmp_path: Path):
    mgr = WorkerManager(lambda *_: FakeWorker("done"), work_dirs_root=tmp_path)
    token = set_active_worker_manager(mgr)
    yield mgr
    reset_active_worker_manager(token)


async def test_delegate_task_returns_worker_result(manager) -> None:
    out = await delegate_task.func(
        task="say hi", role="Greeter", instructions="be polite"
    )
    assert out == "done"


async def test_check_workers_returns_json_list(manager) -> None:
    await delegate_task.func(task="t1", role="r1", instructions="i1")
    out = await check_workers.func()
    body = json.loads(out)
    assert "workers" in body
    assert len(body["workers"]) == 1
    snap = body["workers"][0]
    assert snap["status"] == "completed"
    assert snap["role"] == "r1"


async def test_cancel_worker_unknown_id(manager) -> None:
    out = await cancel_worker.func(worker_id="nope")
    body = json.loads(out)
    assert "error" in body
    assert "nope" in body["error"]


async def test_tools_require_active_manager() -> None:
    """Without an active manager bound to context, tools must raise."""
    with pytest.raises(RuntimeError):
        get_active_worker_manager()


def test_supervisor_does_not_register_mcp_bridge_tools() -> None:
    """Architecture: Supervisor must not have mcp_list_tools / mcp_call_tool."""
    from app.tools import SUPERVISOR_TOOLS

    names = {getattr(t, "name", None) or getattr(t, "__name__", "") for t in SUPERVISOR_TOOLS}
    assert "delegate_task" in names
    assert "check_workers" in names
    assert "cancel_worker" in names
    assert "mcp_list_tools" not in names
    assert "mcp_call_tool" not in names
    assert "calculate" not in names


def test_worker_tool_set_includes_native_and_mcp() -> None:
    from app.tools import WORKER_TOOLS

    names = {getattr(t, "name", None) or getattr(t, "__name__", "") for t in WORKER_TOOLS}
    assert names == {"calculate", "mcp_list_tools", "mcp_call_tool"}
