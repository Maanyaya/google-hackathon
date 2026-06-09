"""Unit tests for MoDeX hook_runner payload handling."""

from __future__ import annotations

import json
import sys
from unittest.mock import patch

import modex_mcp.hook_runner as hr


def _run(event: str, payload: dict, *, logs: list | None = None) -> dict:
    logs = logs if logs is not None else []
    with patch.object(hr, "_EVENT", event):
        with patch.object(hr, "append_codebase_log", side_effect=lambda **kw: logs.append(kw) or {"status": "success"}):
            with patch.object(hr, "save_compressed_context", return_value={"status": "success"}):
                with patch.object(hr, "_write_hydration_file"):
                    with patch.object(hr, "_write_transcript_files"):
                        if event == "beforeSubmitPrompt":
                            return hr._handle_before_prompt(payload)
                        if event == "afterAgentResponse":
                            return hr._handle_after_agent_response(payload)
                        if event == "postToolUse":
                            return hr._handle_post_tool(payload)
                        if event == "afterFileEdit":
                            return hr._handle_after_file_edit(payload)
                        if event == "afterShellExecution":
                            return hr._handle_after_shell(payload)
    return {}


def test_session_id_uses_conversation_id():
    payload = {"conversation_id": "conv-abc-123", "session_id": "other"}
    assert hr._session_id(payload) == "conv-abc-123"


def test_project_repo_finds_nested_git(monkeypatch):
    monkeypatch.setattr(
        hr,
        "_git_repo",
        lambda cwd: "github.com/Maanyaya/google-hackathon"
        if "agentic-data-platform" in cwd
        else None,
    )
    repo = hr._project_repo({"workspace_roots": ["D:/Google cloud rapid agent hackathon"]})
    assert repo == "github.com/Maanyaya/google-hackathon"


def test_before_prompt_logs_and_continues(tmp_path, monkeypatch):
    monkeypatch.setattr(hr, "_SESSION_MARKER", tmp_path / ".modex-active-session")
    monkeypatch.setattr(hr, "_AGENTS_DIR", tmp_path)
    logs: list = []
    out = _run(
        "beforeSubmitPrompt",
        {
            "conversation_id": "conv-1",
            "prompt": "how does face 1 work?",
            "generation_id": "gen-1",
        },
        logs=logs,
    )
    assert out == {"continue": True}
    assert len(logs) >= 2  # session_start + user_prompt
    assert logs[-1]["event_type"] == "user_prompt"
    assert "face 1" in logs[-1]["summary"]
    assert logs[-1]["session_id"] == "conv-1"


def test_after_agent_response_logs_full_text():
    logs: list = []
    _run(
        "afterAgentResponse",
        {"conversation_id": "conv-1", "text": "Here is how Face 1 works."},
        logs=logs,
    )
    assert logs[0]["event_type"] == "agent_response"
    assert logs[0]["payload"]["full_text"].startswith("Here is how")


def test_after_file_edit_skips_empty():
    logs: list = []
    _run("afterFileEdit", {"file_path": "", "edits": []}, logs=logs)
    assert logs == []


def test_post_tool_skips_empty_name():
    logs: list = []
    _run("postToolUse", {"conversation_id": "c1", "tool_input": {}}, logs=logs)
    assert logs == []


def test_post_tool_logs_read():
    logs: list = []
    _run(
        "postToolUse",
        {
            "conversation_id": "c1",
            "tool_name": "Read",
            "tool_input": {"path": "modex_mcp/hook_runner.py"},
        },
        logs=logs,
    )
    assert logs[0]["event_type"] == "tool_call"
    assert logs[0]["payload"]["tool_name"] == "Read"


def test_after_shell_logs_command():
    logs: list = []
    _run(
        "afterShellExecution",
        {"conversation_id": "c1", "command": "python -m pytest", "output": "ok"},
        logs=logs,
    )
    assert logs[0]["summary"].startswith("Shell:")
    assert "pytest" in logs[0]["summary"]
