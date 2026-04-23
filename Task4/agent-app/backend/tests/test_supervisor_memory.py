"""Tests for Supervisor memory injection + [MEMORY_SAVE] persistence."""
from __future__ import annotations

from pathlib import Path

import pytest

from app import agents


@pytest.fixture
def memory_root(tmp_path: Path, monkeypatch):
    """Redirect WORK_DIRS_ROOT (used by load/save helpers) to tmp_path."""
    monkeypatch.setattr(agents, "WORK_DIRS_ROOT", tmp_path)
    return tmp_path


def test_load_memory_returns_empty_when_missing(memory_root: Path) -> None:
    assert agents.load_supervisor_memory() == ""


def test_load_memory_skips_template_only(memory_root: Path) -> None:
    sup = memory_root / "supervisor"
    sup.mkdir()
    (sup / "MEMORY.md").write_text(
        "# Memory\n\n<!-- placeholder -->\n", encoding="utf-8"
    )
    assert agents.load_supervisor_memory() == ""


def test_load_memory_returns_substantive_content(memory_root: Path) -> None:
    sup = memory_root / "supervisor"
    sup.mkdir()
    (sup / "MEMORY.md").write_text(
        "# Memory\n- 사용자 이름: Alice\n", encoding="utf-8"
    )
    out = agents.load_supervisor_memory()
    assert "Alice" in out


def test_inject_memory_into_message_prepends_block() -> None:
    msg = agents.inject_memory_into_message("hello", "- key: value")
    assert "MEMORY.md" in msg
    assert "- key: value" in msg
    assert msg.endswith("hello")


def test_inject_memory_into_message_passthrough_when_empty() -> None:
    assert agents.inject_memory_into_message("hi", "") == "hi"
    assert agents.inject_memory_into_message("hi", "   \n") == "hi"


def test_extract_memory_saves_strips_markers() -> None:
    text = (
        "Sure, here is your answer.\n"
        "[MEMORY_SAVE]\n- 사용자 선호: 다크모드\n[/MEMORY_SAVE]\n"
        "Hope this helps."
    )
    visible, saves = agents.extract_memory_saves(text)
    assert "[MEMORY_SAVE]" not in visible
    assert "Sure, here is your answer." in visible
    assert "Hope this helps." in visible
    assert saves == ["- 사용자 선호: 다크모드"]


def test_extract_memory_saves_handles_multiple_blocks() -> None:
    text = "[MEMORY_SAVE]a[/MEMORY_SAVE]middle[MEMORY_SAVE]b[/MEMORY_SAVE]"
    visible, saves = agents.extract_memory_saves(text)
    assert visible == "middle"
    assert saves == ["a", "b"]


def test_append_supervisor_memory_creates_file(memory_root: Path) -> None:
    agents.append_supervisor_memory(["fact one", "fact two"])
    content = (memory_root / "supervisor" / "MEMORY.md").read_text(encoding="utf-8")
    assert "fact one" in content
    assert "fact two" in content


def test_append_supervisor_memory_appends_to_existing(memory_root: Path) -> None:
    sup = memory_root / "supervisor"
    sup.mkdir()
    (sup / "MEMORY.md").write_text("# Memory\n- existing\n", encoding="utf-8")
    agents.append_supervisor_memory(["new fact"])
    content = (sup / "MEMORY.md").read_text(encoding="utf-8")
    assert "existing" in content
    assert "new fact" in content
