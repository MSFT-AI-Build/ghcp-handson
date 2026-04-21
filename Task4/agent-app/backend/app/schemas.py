"""Pydantic schemas for the API layer."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Incoming chat message from the UI."""

    message: str = Field(..., min_length=1, description="User message text")


class ChatResponse(BaseModel):
    """Agent reply returned to the UI."""

    role: Literal["assistant"] = "assistant"
    message: str


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
