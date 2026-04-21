"""Tests for the WorkerManager."""
from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from app.worker_manager import WorkerManager


class FakeWorkerAgent:
    def __init__(self, reply: str = "ok", *, raises: Exception | None = None) -> None:
        self.reply = reply
        self.raises = raises
        self.calls: list[str] = []

    def run(self, message: str):
        self.calls.append(message)

        async def _await():
            if self.raises is not None:
                raise self.raises
            return type("R", (), {"text": self.reply})()

        return _await()


class HangingWorkerAgent:
    def run(self, message: str):
        async def _hang():
            await asyncio.Event().wait()  # never returns

        return _hang()


@pytest.mark.asyncio
async def test_delegate_creates_workdir_and_runs(tmp_path: Path) -> None:
    factory_calls: list[tuple[str, str, str]] = []

    def factory(worker_id: str, role: str, instructions: str):
        factory_calls.append((worker_id, role, instructions))
        return FakeWorkerAgent(reply="hello")

    mgr = WorkerManager(factory, work_dirs_root=tmp_path)
    out = await mgr.delegate(task="say hi", role="Greeter", instructions="be polite")

    assert out == "hello"
    assert len(factory_calls) == 1
    worker_id = factory_calls[0][0]
    assert worker_id.startswith("worker-")

    # Workdir + AGENT.md written with role/instructions
    work_dir = tmp_path / worker_id
    assert work_dir.is_dir()
    agent_md = (work_dir / "AGENT.md").read_text(encoding="utf-8")
    assert "Greeter" in agent_md
    assert "be polite" in agent_md
    assert (work_dir / "MEMORY.md").exists()

    # check_workers reflects completion
    snaps = mgr.list_workers()
    assert len(snaps) == 1
    snap = snaps[0]
    assert snap["status"] == "completed"
    assert snap["result"] == "hello"
    assert snap["role"] == "Greeter"
    assert snap["task"] == "say hi"


@pytest.mark.asyncio
async def test_delegate_failure_marks_worker_failed(tmp_path: Path) -> None:
    def factory(worker_id, role, instructions):
        return FakeWorkerAgent(raises=RuntimeError("boom"))

    mgr = WorkerManager(factory, work_dirs_root=tmp_path)
    out = await mgr.delegate(task="t", role="r", instructions="i")
    assert "failed" in out
    snap = mgr.list_workers()[0]
    assert snap["status"] == "failed"
    assert "boom" in snap["error"]


@pytest.mark.asyncio
async def test_cancel_worker_unknown_id(tmp_path: Path) -> None:
    mgr = WorkerManager(lambda *_: FakeWorkerAgent(), work_dirs_root=tmp_path)
    with pytest.raises(KeyError):
        mgr.cancel("worker-does-not-exist")


@pytest.mark.asyncio
async def test_cancel_running_worker(tmp_path: Path) -> None:
    mgr = WorkerManager(lambda *_: HangingWorkerAgent(), work_dirs_root=tmp_path)
    delegate = asyncio.create_task(
        mgr.delegate(task="t", role="r", instructions="i")
    )
    # Wait for it to enter running
    for _ in range(50):
        await asyncio.sleep(0.01)
        snaps = mgr.list_workers()
        if snaps and snaps[0]["status"] == "running":
            worker_id = snaps[0]["id"]
            break
    else:  # pragma: no cover
        pytest.fail("worker never reached running state")

    snap = mgr.cancel(worker_id)
    assert snap["status"] == "cancelled"
    with pytest.raises(asyncio.CancelledError):
        await delegate


@pytest.mark.asyncio
async def test_emits_status_events(tmp_path: Path) -> None:
    mgr = WorkerManager(lambda *_: FakeWorkerAgent(reply="done"), work_dirs_root=tmp_path)
    await mgr.delegate(task="t", role="r", instructions="i")
    events = mgr.drain_events()
    statuses = [e["status"] for e in events if e["event"] == "status"]
    assert statuses[:3] == ["pending", "running", "completed"]
    # Each event carries the worker id
    assert all(e["id"].startswith("worker-") for e in events)
