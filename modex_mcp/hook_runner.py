"""IDE hooks → MoDeX auto-logger (Cursor + Antigravity).

Reads hook JSON from stdin, appends to agent_memory.codebase_logs (+ Sheet mirror).
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[1]
_WORKSPACE = _ROOT.parent
sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv

load_dotenv(_ROOT / ".env")
load_dotenv(_WORKSPACE / ".env")

from modex_mcp.memory_store import append_codebase_log  # noqa: E402

_EVENT = sys.argv[1] if len(sys.argv) > 1 else ""
_CONFIG_PATHS = (
    _WORKSPACE / ".agents" / "modex.json",
    _WORKSPACE / ".cursor" / "modex.json",
    _ROOT / ".cursor" / "modex.json",
)
_AGENTS_DIR = _WORKSPACE / ".agents"
_HYDRATION_FILE = _AGENTS_DIR / "modex-hydration.md"
_SESSION_MARKER = _AGENTS_DIR / ".modex-active-session"


def _load_config() -> dict[str, Any]:
    for path in _CONFIG_PATHS:
        if path.is_file():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                pass
    return {}


def _cfg() -> dict[str, Any]:
    file_cfg = _load_config()
    return {
        "project_repo": os.getenv(
            "MODEX_PROJECT_REPO",
            file_cfg.get("project_repo", "github.com/demo/api-service"),
        ),
        "agent_tool": os.getenv("MODEX_AGENT_TOOL", file_cfg.get("agent_tool", "cursor")),
        "developer_id": os.getenv(
            "MODEX_DEVELOPER_ID",
            file_cfg.get("developer_id", ""),
        ),
        "auto_hydrate": file_cfg.get("auto_hydrate", True),
    }


def _developer_id() -> str:
    cfg = _cfg()
    if cfg["developer_id"]:
        return cfg["developer_id"]
    try:
        r = subprocess.run(
            ["git", "config", "user.email"],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
        if r.stdout.strip():
            return r.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return os.getenv("USERNAME") or os.getenv("USER") or "developer"


def _git_repo(cwd: str | None) -> str | None:
    try:
        r = subprocess.run(
            ["git", "-C", cwd or ".", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
        url = r.stdout.strip()
        if not url:
            return None
        m = re.search(r"github\.com[:/](.+?)(?:\.git)?$", url)
        if m:
            return f"github.com/{m.group(1)}"
    except (OSError, subprocess.TimeoutExpired):
        pass
    return None


def _project_repo(payload: dict[str, Any]) -> str:
    cfg = _cfg()
    cwd = payload.get("cwd") or _ag_cwd(payload)
    return _git_repo(cwd) or cfg["project_repo"]


def _session_id(payload: dict[str, Any]) -> str:
    return (
        payload.get("session_id")
        or os.getenv("MODEX_SESSION_ID")
        or "unknown-session"
    )


def _safe_log(**kwargs: Any) -> None:
    try:
        append_codebase_log(**kwargs)
    except Exception as exc:  # noqa: BLE001
        print(f"modex hook log failed: {exc}", file=sys.stderr)


def _hydration_context(project_repo: str) -> str:
    try:
        from app.memory_graph import build_context_pack

        pack = build_context_pack(project_repo=project_repo, include_rag=False)
        if pack.get("status") == "success" and pack.get("hydration_prompt"):
            return pack["hydration_prompt"]
    except Exception as exc:  # noqa: BLE001
        return f"MoDeX: context pack unavailable ({exc})."
    return ""


def _write_hydration_file(project_repo: str) -> None:
    ctx = _hydration_context(project_repo)
    if not ctx:
        return
    try:
        _AGENTS_DIR.mkdir(parents=True, exist_ok=True)
        _HYDRATION_FILE.write_text(
            "# MoDeX shared memory (auto-loaded)\n\n"
            + ctx
            + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        print(f"modex hydration file write failed: {exc}", file=sys.stderr)


def _ag_prompt(payload: dict[str, Any]) -> str:
    for key in ("prompt", "user_prompt", "message", "input", "user_message", "text"):
        val = payload.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def _ag_tool_name(payload: dict[str, Any]) -> str:
    for key in ("tool_name", "name", "tool", "toolName"):
        val = payload.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def _ag_tool_args(payload: dict[str, Any]) -> dict[str, Any]:
    raw = payload.get("tool_input") or payload.get("arguments") or payload.get("args")
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, dict) else {"raw": raw[:500]}
        except json.JSONDecodeError:
            return {"raw": raw[:500]}
    return payload.get("parameters") or {}


def _ag_file_path(args: dict[str, Any], payload: dict[str, Any]) -> str:
    for key in ("TargetFile", "FilePath", "file_path", "path", "AbsolutePath"):
        val = args.get(key) or payload.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def _ag_cwd(payload: dict[str, Any]) -> str | None:
    args = _ag_tool_args(payload)
    for key in ("cwd", "Cwd", "working_directory", "workspace"):
        val = payload.get(key) or args.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return None


def _ensure_antigravity_session(payload: dict[str, Any]) -> str:
    """First PreInvocation in a conversation → session_start + hydration file."""
    sid = (
        payload.get("session_id")
        or payload.get("conversation_id")
        or payload.get("thread_id")
        or os.getenv("MODEX_SESSION_ID")
        or str(uuid.uuid4())
    )
    try:
        prev = _SESSION_MARKER.read_text(encoding="utf-8").strip() if _SESSION_MARKER.is_file() else ""
    except OSError:
        prev = ""
    if prev != sid:
        cfg = _cfg()
        repo = _project_repo(payload)
        _safe_log(
            developer_id=_developer_id(),
            agent_tool=cfg["agent_tool"],
            project_repo=repo,
            event_type="session_start",
            summary="Antigravity session started",
            session_id=sid,
            payload={"auto": True, "ide": "antigravity"},
        )
        if cfg.get("auto_hydrate", True):
            _write_hydration_file(repo)
        try:
            _AGENTS_DIR.mkdir(parents=True, exist_ok=True)
            _SESSION_MARKER.write_text(sid, encoding="utf-8")
        except OSError:
            pass
    os.environ["MODEX_SESSION_ID"] = sid
    return sid


def _handle_antigravity_pre_invocation(payload: dict[str, Any]) -> dict[str, Any]:
    sid = _ensure_antigravity_session(payload)
    prompt = _ag_prompt(payload)
    if prompt:
        cfg = _cfg()
        _safe_log(
            developer_id=_developer_id(),
            agent_tool=cfg["agent_tool"],
            project_repo=_project_repo(payload),
            event_type="user_prompt",
            summary=prompt[:4000],
            session_id=sid,
            payload={"auto": True, "ide": "antigravity"},
        )
    return {}


def _handle_antigravity_post_tool(payload: dict[str, Any]) -> dict[str, Any]:
    cfg = _cfg()
    name = _ag_tool_name(payload)
    if not name or "modex-memory" in name.lower():
        return {}
    args = _ag_tool_args(payload)
    repo = _project_repo({**payload, "cwd": _ag_cwd(payload)})
    sid = _session_id(payload)

    if name in {"edit_file", "Edit", "Write", "write_file"}:
        path = _ag_file_path(args, payload)
        _safe_log(
            developer_id=_developer_id(),
            agent_tool=cfg["agent_tool"],
            project_repo=repo,
            event_type="file_edit",
            summary=f"Edited {Path(path).name or path or name}",
            session_id=sid,
            file_path=path,
            payload={"tool": name, "auto": True, "ide": "antigravity"},
        )
        return {}

    summary = name
    if name in {"run_command", "Shell", "run_shell_command"}:
        cmd = args.get("CommandLine") or args.get("command") or args.get("cmd") or ""
        summary = f"Shell: {str(cmd)[:500]}"
    elif args:
        summary = f"{name}: {json.dumps(args, default=str)[:500]}"
    _safe_log(
        developer_id=_developer_id(),
        agent_tool=cfg["agent_tool"],
        project_repo=repo,
        event_type="tool_call",
        summary=summary[:4000],
        session_id=sid,
        payload={"tool_name": name, "auto": True, "ide": "antigravity"},
    )
    return {}


def _handle_antigravity_stop(payload: dict[str, Any]) -> dict[str, Any]:
    result = _handle_session_end(payload)
    try:
        if _SESSION_MARKER.is_file():
            _SESSION_MARKER.unlink()
    except OSError:
        pass
    return result


def _handle_session_start(payload: dict[str, Any]) -> dict[str, Any]:
    cfg = _cfg()
    repo = _project_repo(payload)
    sid = _session_id(payload)
    mode = payload.get("composer_mode", "agent")
    _safe_log(
        developer_id=_developer_id(),
        agent_tool=cfg["agent_tool"],
        project_repo=repo,
        event_type="session_start",
        summary=f"Cursor session started ({mode})",
        session_id=sid,
        payload={"composer_mode": mode, "auto": True},
    )
    out: dict[str, Any] = {
        "env": {
            "MODEX_SESSION_ID": sid,
            "MODEX_PROJECT_REPO": repo,
            "MODEX_AGENT_TOOL": cfg["agent_tool"],
        },
    }
    if cfg.get("auto_hydrate", True):
        ctx = _hydration_context(repo)
        if ctx:
            out["additional_context"] = (
                "## MoDeX shared memory (auto-loaded at session start)\n\n"
                + ctx
                + "\n\n---\nBuild on this context; log new decisions via MoDeX when they matter."
            )
    return out


def _handle_session_end(payload: dict[str, Any]) -> dict[str, Any]:
    cfg = _cfg()
    repo = _project_repo(payload)
    sid = _session_id(payload)
    reason = payload.get("reason", "ended")
    duration = payload.get("duration_ms")
    _safe_log(
        developer_id=_developer_id(),
        agent_tool=cfg["agent_tool"],
        project_repo=repo,
        event_type="session_end",
        summary=f"Session ended ({reason})",
        session_id=sid,
        payload={"reason": reason, "duration_ms": duration, "auto": True},
    )
    return {}


def _handle_before_prompt(payload: dict[str, Any]) -> dict[str, Any]:
    cfg = _cfg()
    prompt = (payload.get("prompt") or "").strip()
    if not prompt:
        return {}
    _safe_log(
        developer_id=_developer_id(),
        agent_tool=cfg["agent_tool"],
        project_repo=_project_repo(payload),
        event_type="user_prompt",
        summary=prompt[:4000],
        session_id=_session_id(payload),
        payload={"auto": True},
    )
    return {}


def _handle_after_file_edit(payload: dict[str, Any]) -> dict[str, Any]:
    cfg = _cfg()
    path = payload.get("file_path") or ""
    edits = payload.get("edits") or []
    _safe_log(
        developer_id=_developer_id(),
        agent_tool=cfg["agent_tool"],
        project_repo=_project_repo(payload),
        event_type="file_edit",
        summary=f"Edited {Path(path).name} ({len(edits)} change(s))",
        session_id=_session_id(payload),
        file_path=path,
        payload={"edit_count": len(edits), "auto": True},
    )
    return {}


def _handle_post_tool(payload: dict[str, Any]) -> dict[str, Any]:
    cfg = _cfg()
    name = payload.get("tool_name") or ""
    if name.lower().startswith("mcp:") and "modex-memory" in name.lower():
        return {}
    tool_input = payload.get("tool_input") or {}
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except json.JSONDecodeError:
            tool_input = {"raw": tool_input[:500]}
    summary = name
    if name == "Shell" and isinstance(tool_input, dict):
        summary = f"Shell: {str(tool_input.get('command', ''))[:500]}"
    elif isinstance(tool_input, dict) and tool_input:
        summary = f"{name}: {json.dumps(tool_input, default=str)[:500]}"
    _safe_log(
        developer_id=_developer_id(),
        agent_tool=cfg["agent_tool"],
        project_repo=_project_repo(payload),
        event_type="tool_call",
        summary=summary[:4000],
        session_id=_session_id(payload),
        payload={"tool_name": name, "auto": True},
    )
    return {}


def _handle_post_tool_failure(payload: dict[str, Any]) -> dict[str, Any]:
    cfg = _cfg()
    name = payload.get("tool_name") or "tool"
    err = (payload.get("error_message") or "unknown error")[:2000]
    _safe_log(
        developer_id=_developer_id(),
        agent_tool=cfg["agent_tool"],
        project_repo=_project_repo(payload),
        event_type="error",
        summary=f"{name} failed: {err}",
        session_id=_session_id(payload),
        payload={
            "tool_name": name,
            "failure_type": payload.get("failure_type"),
            "auto": True,
        },
    )
    return {}


_HANDLERS = {
    # Cursor
    "sessionStart": _handle_session_start,
    "sessionEnd": _handle_session_end,
    "beforeSubmitPrompt": _handle_before_prompt,
    "afterFileEdit": _handle_after_file_edit,
    "postToolUse": _handle_post_tool,
    "postToolUseFailure": _handle_post_tool_failure,
    # Antigravity (https://antigravity.google/docs/hooks)
    "PreInvocation": _handle_antigravity_pre_invocation,
    "PostToolUse": _handle_antigravity_post_tool,
    "Stop": _handle_antigravity_stop,
    "SessionStart": _handle_session_start,
}


def main() -> None:
    raw = sys.stdin.read()
    payload: dict[str, Any] = {}
    if raw.strip():
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {}
    handler = _HANDLERS.get(_EVENT)
    if not handler:
        print("{}")
        return
    try:
        result = handler(payload)
        print(json.dumps(result or {}))
    except Exception as exc:  # noqa: BLE001
        print(f"modex hook error ({_EVENT}): {exc}", file=sys.stderr)
        print("{}")


if __name__ == "__main__":
    main()
