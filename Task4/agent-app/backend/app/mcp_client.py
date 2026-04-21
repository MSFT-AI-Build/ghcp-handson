"""MCP client manager and configuration loader."""
from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import socket
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from dotenv import dotenv_values, find_dotenv, load_dotenv

logger = logging.getLogger(__name__)

# Populate os.environ from .env so ${VAR} placeholders in mcp_config.json expand
# correctly regardless of whether the shell already exported them.
load_dotenv(override=False)


def _dotenv_values() -> dict[str, str]:
    """Return key-value pairs from the .env file (empty dict if absent)."""
    path = find_dotenv(usecwd=True)
    if not path:
        return {}
    return {k: v for k, v in dotenv_values(path).items() if v is not None}  # type: ignore[misc]


class MCPConfigError(ValueError):
    """Raised when mcp_config.json is missing required fields or invalid."""


class MCPServerError(RuntimeError):
    """Raised when an MCP server interaction fails."""


DEFAULT_CONFIG_PATH = (
    Path(__file__).resolve().parents[1] / "mcp_servers" / "mcp_config.json"
)

_ENV_PATTERN = re.compile(r"\$\{([A-Z0-9_]+)\}")


def _expand_env(value: str, lookup: dict[str, str] | None = None) -> str:
    """Expand ``${VAR}`` placeholders using *lookup* or ``os.environ``."""
    source = lookup if lookup is not None else {**os.environ, **_dotenv_values()}

    def repl(match: re.Match[str]) -> str:
        return source.get(match.group(1), "")

    return _ENV_PATTERN.sub(repl, value)


def load_mcp_config(path: Path | None = None) -> dict[str, Any]:
    """Load and validate the MCP servers configuration."""
    config_path = path or DEFAULT_CONFIG_PATH
    if not config_path.exists():
        return {"mcpServers": {}}
    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise MCPConfigError(f"invalid JSON in {config_path}: {exc.msg}") from exc
    if not isinstance(raw, dict) or "mcpServers" not in raw:
        raise MCPConfigError("config must contain top-level 'mcpServers' object")
    servers = raw["mcpServers"]
    if not isinstance(servers, dict):
        raise MCPConfigError("'mcpServers' must be an object")
    for name, spec in servers.items():
        if not isinstance(spec, dict):
            raise MCPConfigError(f"server '{name}' must be an object")
        if not spec.get("command"):
            raise MCPConfigError(f"server '{name}' is missing required 'command'")
    return raw


class MCPClientManager:
    """Manages MCP server connections (stdio + http transports).

    Each server runs in its own asyncio Task so the anyio task-group based
    transports are entered and exited in the same task (avoiding the
    "Attempted to exit cancel scope in a different task" error).
    """

    def __init__(self, config: dict[str, Any]):
        self._servers: dict[str, dict[str, Any]] = dict(
            config.get("mcpServers", {})
        )
        self._status: dict[str, str] = {
            name: "disconnected" for name in self._servers
        }
        self._errors: dict[str, str] = {}
        self._tool_cache: dict[str, list[dict[str, Any]]] = {}
        self._sessions: dict[str, Any] = {}
        self._tasks: dict[str, asyncio.Task[None]] = {}
        self._stop_events: dict[str, asyncio.Event] = {}
        self._processes: dict[str, asyncio.subprocess.Process] = {}

    @property
    def server_names(self) -> list[str]:
        return list(self._servers)

    def status(self, server: str) -> str:
        return self._status.get(server, "unknown")

    def describe_servers(self) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for name, spec in self._servers.items():
            entry: dict[str, Any] = {
                "name": name,
                "transport": spec.get("transport", "stdio"),
                "command": spec.get("command"),
                "args": spec.get("args", []),
                "status": self._status.get(name, "disconnected"),
                "tools": self._tool_cache.get(name, []),
            }
            if name in self._errors:
                entry["error"] = self._errors[name]
            out.append(entry)
        return out

    def _require_known(self, server: str) -> None:
        if server not in self._servers:
            raise MCPServerError(f"unknown MCP server: {server}")

    async def connect_all(self) -> None:
        """Launch a worker task per server and wait for connect attempts."""
        ready_events: list[asyncio.Event] = []
        for name in self._servers:
            ready = asyncio.Event()
            stop = asyncio.Event()
            self._stop_events[name] = stop
            task = asyncio.create_task(
                self._server_task(name, ready), name=f"mcp-{name}"
            )
            self._tasks[name] = task
            ready_events.append(ready)
        if ready_events:
            await asyncio.gather(*(ev.wait() for ev in ready_events))

    async def _spawn_http_server(
        self,
        name: str,
        command: str,
        spec: dict[str, Any],
        env: dict[str, str],
        url: str,
    ) -> None:
        """Launch a local MCP HTTP server subprocess and wait for the port."""
        parsed = urlparse(url)
        host = parsed.hostname or "localhost"
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        if await _port_open(host, port):
            logger.info(
                "MCP server '%s' already listening on %s:%s; reusing", name, host, port
            )
            return
        args = [_expand_env(str(a), env) for a in spec.get("args", [])]
        logger.info("Spawning MCP server '%s': %s %s", name, command, " ".join(args))
        proc = await asyncio.create_subprocess_exec(
            command,
            *args,
            env=env,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE,
        )
        self._processes[name] = proc
        timeout = float(spec.get("startup_timeout", 20))
        deadline = asyncio.get_event_loop().time() + timeout
        while asyncio.get_event_loop().time() < deadline:
            if proc.returncode is not None:
                err = b""
                if proc.stderr is not None:
                    try:
                        err = await asyncio.wait_for(proc.stderr.read(), timeout=0.5)
                    except asyncio.TimeoutError:
                        pass
                raise MCPServerError(
                    f"server '{name}' exited with code {proc.returncode}: "
                    f"{err.decode(errors='replace').strip()[:400]}"
                )
            if await _port_open(host, port):
                return
            await asyncio.sleep(0.25)
        raise MCPServerError(
            f"server '{name}' did not open {host}:{port} within {timeout}s"
        )

    async def _server_task(self, name: str, ready: asyncio.Event) -> None:
        spec = self._servers[name]
        transport = spec.get("transport", "stdio")
        try:
            from mcp import ClientSession  # type: ignore

            # Build subprocess env: os.environ base, .env values on top for
            # vars not already exported, then server-specific overrides expanded.
            base_env: dict[str, str] = {**os.environ, **_dotenv_values()}
            env = {
                k: _expand_env(str(v), base_env)
                for k, v in (spec.get("env") or {}).items()
            }
            merged_env = {**base_env, **env}

            if transport == "stdio":
                from mcp import StdioServerParameters  # type: ignore
                from mcp.client.stdio import stdio_client  # type: ignore

                params = StdioServerParameters(
                    command=spec["command"],
                    args=list(spec.get("args", [])),
                    env=merged_env,
                )
                transport_ctx = stdio_client(params)
            elif transport == "http":
                try:
                    from mcp.client.streamable_http import (  # type: ignore
                        streamablehttp_client,
                    )
                except ImportError as exc:
                    raise MCPServerError(
                        "mcp SDK does not expose streamable_http client; "
                        "upgrade the 'mcp' package"
                    ) from exc
                url = _expand_env(str(spec.get("url", "")), base_env)
                if not url:
                    raise MCPServerError(
                        f"server '{name}' uses transport=http but no 'url' is set"
                    )
                command = spec.get("command")
                if command:
                    await self._spawn_http_server(name, command, spec, merged_env, url)
                transport_ctx = streamablehttp_client(url)
            else:
                raise MCPServerError(f"unsupported transport: {transport}")

            async with transport_ctx as opened:
                read, write = opened[0], opened[1]
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools_resp = await session.list_tools()
                    tools: list[dict[str, Any]] = []
                    for t in getattr(tools_resp, "tools", []) or []:
                        tools.append(
                            {
                                "name": getattr(t, "name", ""),
                                "description": getattr(t, "description", "") or "",
                                "input_schema": getattr(t, "inputSchema", None),
                            }
                        )
                    self._sessions[name] = session
                    self._tool_cache[name] = tools
                    self._status[name] = "connected"
                    self._errors.pop(name, None)
                    logger.info(
                        "MCP server '%s' connected (%d tools)", name, len(tools)
                    )
                    ready.set()
                    await self._stop_events[name].wait()
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001
            self._status[name] = "error"
            self._errors[name] = str(exc)
            logger.warning("MCP server '%s' failed: %s", name, exc)
        finally:
            self._sessions.pop(name, None)
            if self._status.get(name) == "connected":
                self._status[name] = "disconnected"
            await self._terminate_process(name)
            ready.set()

    async def list_tools(self, server: str) -> list[dict[str, Any]]:
        self._require_known(server)
        if server in self._sessions:
            return self._tool_cache.get(server, [])
        raise MCPServerError(
            f"MCP server '{server}' is not connected "
            f"({self._errors.get(server, 'offline')})"
        )

    async def call_tool(
        self, server: str, tool: str, arguments: dict[str, Any]
    ) -> Any:
        self._require_known(server)
        session = self._sessions.get(server)
        if session is None:
            raise MCPServerError(
                f"MCP server '{server}' is not connected "
                f"({self._errors.get(server, 'offline')})"
            )
        try:
            result = await session.call_tool(tool, arguments)
        except Exception as exc:  # noqa: BLE001
            raise MCPServerError(
                f"call_tool failed on '{server}.{tool}': {exc}"
            ) from exc
        return _serialize_call_result(result)

    async def aclose(self) -> None:
        for ev in self._stop_events.values():
            ev.set()
        tasks = list(self._tasks.values())
        for task in tasks:
            try:
                await asyncio.wait_for(task, timeout=5)
            except asyncio.TimeoutError:
                task.cancel()
                try:
                    await task
                except (asyncio.CancelledError, Exception):  # noqa: BLE001
                    pass
            except Exception:  # noqa: BLE001
                pass
        self._tasks.clear()
        self._stop_events.clear()
        for name in list(self._processes):
            await self._terminate_process(name)

    async def _terminate_process(self, name: str) -> None:
        proc = self._processes.pop(name, None)
        if proc is None or proc.returncode is not None:
            return
        try:
            proc.terminate()
        except ProcessLookupError:
            return
        try:
            await asyncio.wait_for(proc.wait(), timeout=5)
        except asyncio.TimeoutError:
            proc.kill()
            try:
                await proc.wait()
            except Exception:  # noqa: BLE001
                pass


def _serialize_call_result(result: Any) -> Any:
    content = getattr(result, "content", None)
    if content is None:
        return result
    parts: list[Any] = []
    for item in content:
        text = getattr(item, "text", None)
        if text is not None:
            parts.append(text)
            continue
        data = getattr(item, "data", None)
        if data is not None:
            parts.append(data)
            continue
        parts.append(str(item))
    if len(parts) == 1:
        return parts[0]
    return parts


async def _port_open(host: str, port: int, timeout: float = 0.5) -> bool:
    try:
        fut = asyncio.open_connection(host, port)
        reader, writer = await asyncio.wait_for(fut, timeout=timeout)
    except (OSError, asyncio.TimeoutError):
        return False
    writer.close()
    try:
        await writer.wait_closed()
    except Exception:  # noqa: BLE001
        pass
    return True


_manager: MCPClientManager | None = None


def get_mcp_manager() -> MCPClientManager:
    global _manager
    if _manager is None:
        try:
            config = load_mcp_config()
        except MCPConfigError:
            config = {"mcpServers": {}}
        _manager = MCPClientManager(config)
    return _manager


def set_mcp_manager(manager: MCPClientManager) -> None:
    """Inject a manager (used by tests)."""
    global _manager
    _manager = manager


def reset_mcp_manager() -> None:
    global _manager
    _manager = None

