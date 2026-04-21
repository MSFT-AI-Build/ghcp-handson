"""Supervisor agent factory."""
from __future__ import annotations

from functools import lru_cache
from typing import Protocol

from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient

from .config import get_settings


SUPERVISOR_INSTRUCTIONS = (
    "You are the Supervisor Agent. Understand the user's request, "
    "answer concisely, and coordinate work when needed."
)


class SupportsRun(Protocol):
    async def run(self, message: str) -> object: ...


@lru_cache
def get_supervisor_agent() -> Agent:
    """Build the singleton supervisor Agent backed by Azure OpenAI."""
    settings = get_settings()
    client = OpenAIChatClient(
        api_key=settings.azure_openai_key,
        base_url=settings.azure_openai_endpoint,
        model=settings.azure_openai_deployment,
    )
    return Agent(
        name="supervisor",
        client=client,
        instructions=SUPERVISOR_INSTRUCTIONS,
    )


def reset_supervisor_agent() -> None:
    """Clear the cached agent (used in tests)."""
    get_supervisor_agent.cache_clear()
