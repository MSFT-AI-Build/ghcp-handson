"""Supervisor-only delegation tools.

These native tools let the Supervisor spawn Worker agents on demand. The
active :class:`WorkerManager` is bound to a ``contextvars.ContextVar`` by
``main.py`` for the duration of a chat request so each request operates on
its own isolated worker pool.
"""
from __future__ import annotations

import contextvars
import json
from typing import Annotated, Any

from agent_framework import tool

from ..worker_manager import WorkerManager

_active_manager: contextvars.ContextVar[WorkerManager | None] = contextvars.ContextVar(
    "active_worker_manager", default=None
)


def set_active_worker_manager(manager: WorkerManager | None) -> contextvars.Token:
    """Bind a :class:`WorkerManager` to the current async context.

    Returns the contextvar token so callers can ``reset`` it afterwards.
    """
    return _active_manager.set(manager)


def reset_active_worker_manager(token: contextvars.Token) -> None:
    _active_manager.reset(token)


def get_active_worker_manager() -> WorkerManager:
    mgr = _active_manager.get()
    if mgr is None:
        raise RuntimeError(
            "No active WorkerManager bound to this context. "
            "delegation tools can only be invoked from a chat request."
        )
    return mgr


@tool(
    name="delegate_task",
    description=(
        "Spawn a Worker Agent with a custom role/instructions and assign it "
        "the given task. Returns the Worker's final result as text."
    ),
)
async def delegate_task(
    task: Annotated[str, "The task the Worker should perform."],
    role: Annotated[str, "Role/persona for the Worker (e.g. 'Python refactor expert')."],
    instructions: Annotated[str, "Detailed instructions the Worker must follow."],
) -> str:
    manager = get_active_worker_manager()
    return await manager.delegate(task=task, role=role, instructions=instructions)


@tool(
    name="check_workers",
    description=(
        "List all Worker Agents created during the current request along with "
        "their id, role, status, task, and result (if any). Returns a JSON string."
    ),
)
async def check_workers() -> str:
    manager = get_active_worker_manager()
    return json.dumps({"workers": manager.list_workers()}, ensure_ascii=False)


@tool(
    name="cancel_worker",
    description="Cancel a running Worker Agent by its id. Returns its final snapshot.",
)
async def cancel_worker(
    worker_id: Annotated[str, "Worker id returned by delegate_task / check_workers."],
) -> str:
    manager = get_active_worker_manager()
    try:
        snap = manager.cancel(worker_id)
    except KeyError:
        return json.dumps({"error": f"unknown worker_id: {worker_id}"})
    return json.dumps(snap, ensure_ascii=False)


SUPERVISOR_DELEGATION_TOOLS: list[Any] = [
    delegate_task,
    check_workers,
    cancel_worker,
]
