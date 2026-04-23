"""Worker agent runtime + status tracking.

The Supervisor delegates tasks via the ``delegate_task`` native tool. Each
delegation spawns a *Worker* agent with a custom role/instructions defined
by the Supervisor. Workers run in their own asyncio Task so that the
Supervisor can spawn several in parallel and the UI can subscribe to status
transitions over SSE.

State machine:

    pending --> running --> completed
                       \\--> failed
                       \\--> cancelled
"""
from __future__ import annotations

import asyncio
import logging
import secrets
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Awaitable, Callable

from .tool_events import ToolEventAggregator
from .work_dir import WORK_DIRS_ROOT, ensure_agent_work_dir

logger = logging.getLogger(__name__)

# Status string union used in events / API responses.
WorkerStatus = str  # "pending" | "running" | "completed" | "failed" | "cancelled"

# A worker factory takes (worker_id, role, instructions) and returns an
# *agent-like* object exposing ``async run(message: str) -> object``.
WorkerAgentFactory = Callable[[str, str, str], Any]


@dataclass
class WorkerRecord:
    id: str
    role: str
    task: str
    instructions: str
    status: WorkerStatus = "pending"
    work_dir: Path | None = None
    result: str | None = None
    error: str | None = None
    started_at: float = field(default_factory=time.time)
    finished_at: float | None = None

    def snapshot(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "role": self.role,
            "task": self.task,
            "instructions": self.instructions,
            "status": self.status,
            "work_dir": str(self.work_dir) if self.work_dir else None,
            "result": self.result,
            "error": self.error,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
        }


class WorkerManager:
    """Tracks worker agents for a single chat turn.

    Designed to be created **per request** so concurrency is naturally
    isolated. ``main.py`` binds the active manager to a contextvar before
    invoking the supervisor agent.
    """

    def __init__(
        self,
        worker_factory: WorkerAgentFactory,
        *,
        work_dirs_root: Path | None = None,
        id_prefix: str = "worker",
    ) -> None:
        self._factory = worker_factory
        self._work_dirs_root = work_dirs_root if work_dirs_root is not None else WORK_DIRS_ROOT
        self._id_prefix = id_prefix
        self._workers: dict[str, WorkerRecord] = {}
        self._tasks: dict[str, asyncio.Task[Any]] = {}
        self._events: asyncio.Queue[dict[str, Any]] = asyncio.Queue()

    # ------------------------------------------------------------------
    # Public API used by delegation tools
    # ------------------------------------------------------------------
    async def delegate(self, task: str, role: str, instructions: str) -> str:
        """Create a Worker, run the task to completion, return the result."""
        record = self._create_worker(task=task, role=role, instructions=instructions)
        await self._publish(record, status="pending")
        coro = self._run_worker(record)
        worker_task = asyncio.create_task(coro, name=f"worker-{record.id}")
        self._tasks[record.id] = worker_task
        try:
            return await worker_task
        except asyncio.CancelledError:
            # If the parent (delegate caller) is cancelled, propagate.
            raise

    def list_workers(self) -> list[dict[str, Any]]:
        return [w.snapshot() for w in self._workers.values()]

    def cancel(self, worker_id: str) -> dict[str, Any]:
        record = self._workers.get(worker_id)
        if record is None:
            raise KeyError(worker_id)
        if record.status in ("completed", "failed", "cancelled"):
            return record.snapshot()
        task = self._tasks.get(worker_id)
        if task is not None and not task.done():
            task.cancel()
        record.status = "cancelled"
        record.finished_at = time.time()
        # Synchronously enqueue so callers observing the queue see the
        # cancellation even before the task finishes.
        self._events.put_nowait({"type": "worker", "event": "status", **record.snapshot()})
        return record.snapshot()

    # ------------------------------------------------------------------
    # SSE plumbing
    # ------------------------------------------------------------------
    async def next_event(self, timeout: float | None = None) -> dict[str, Any] | None:
        try:
            if timeout is None:
                return await self._events.get()
            return await asyncio.wait_for(self._events.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None

    def drain_events(self) -> list[dict[str, Any]]:
        """Non-blocking drain of all currently queued events."""
        out: list[dict[str, Any]] = []
        while True:
            try:
                out.append(self._events.get_nowait())
            except asyncio.QueueEmpty:
                return out

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _new_worker_id(self) -> str:
        return f"{self._id_prefix}-{secrets.token_hex(3)}"

    def _create_worker(self, *, task: str, role: str, instructions: str) -> WorkerRecord:
        worker_id = self._new_worker_id()
        work_dir = ensure_agent_work_dir(
            worker_id,
            work_dirs_root=self._work_dirs_root,
            role=role,
            instructions=instructions,
            capabilities=[
                "Native tools: calculate",
                "MCP bridge tools: mcp_list_tools, mcp_call_tool",
            ],
            overwrite_agent_md=True,
        )
        record = WorkerRecord(
            id=worker_id,
            role=role,
            task=task,
            instructions=instructions,
            work_dir=work_dir,
        )
        self._workers[worker_id] = record
        return record

    async def _run_worker(self, record: WorkerRecord) -> str:
        record.status = "running"
        await self._publish(record, status="running")

        async def _on_tool(event: dict) -> None:
            """Forward a worker tool-call event to the SSE queue."""
            await self._events.put({
                "type": "worker_tool",
                "worker_id": record.id,
                "worker_role": record.role,
                **event,
            })

        try:
            agent = self._factory(record.id, record.role, record.instructions)
            result = await _run_agent(agent, record.task, on_tool=_on_tool)
        except asyncio.CancelledError:
            record.status = "cancelled"
            record.finished_at = time.time()
            await self._publish(record, status="cancelled")
            raise
        except Exception as exc:  # noqa: BLE001
            record.status = "failed"
            record.error = str(exc)
            record.finished_at = time.time()
            await self._publish(record, status="failed")
            logger.exception("worker %s failed", record.id)
            return f"[worker {record.id} failed: {exc}]"
        record.status = "completed"
        record.result = _stringify_result(result)
        record.finished_at = time.time()
        await self._publish(record, status="completed")
        return record.result or ""

    async def _publish(self, record: WorkerRecord, *, status: WorkerStatus) -> None:
        event = {"type": "worker", "event": "status", **record.snapshot()}
        # ``snapshot`` already contains ``status``, but make sure it matches the
        # most recent transition (in case caller mutated record afterwards).
        event["status"] = status
        await self._events.put(event)


async def _run_agent(
    agent: Any,
    message: str,
    on_tool: Callable[..., Any] | None = None,
) -> Any:
    """Run an agent supporting either ``await agent.run`` or async iter stream.

    When *on_tool* is provided and the agent is streaming, each finalized
    tool-call event is forwarded to the callback so callers can publish it
    to the SSE queue in real-time.
    """
    out = agent.run(message)
    if hasattr(out, "__await__"):
        return await out
    if hasattr(out, "__aiter__"):
        aggregator = ToolEventAggregator()
        chunks: list[str] = []
        async for upd in out:
            if on_tool is not None:
                for evt in aggregator.consume(upd):
                    await on_tool(evt)
            text = getattr(upd, "text", None) or getattr(upd, "delta", None)
            if isinstance(text, str):
                chunks.append(text)
        if on_tool is not None:
            for evt in aggregator.flush():
                await on_tool(evt)
        return "".join(chunks)
    return out


def _stringify_result(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    for attr in ("text", "output_text", "content"):
        v = getattr(value, attr, None)
        if isinstance(v, str) and v:
            return v
    messages = getattr(value, "messages", None)
    if messages:
        last = messages[-1]
        text = getattr(last, "text", None) or getattr(last, "content", None)
        if isinstance(text, str):
            return text
    return str(value)
