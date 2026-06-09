"""IDE hooks -> MoDeX auto-logger (Cursor + Antigravity).

This is the capture half of MoDeX (Face 1). Each IDE event (session start, user
prompt, agent response, tool call, file edit, error, session end) is delivered
to this script as JSON on stdin. We turn it into an immutable row in
BigQuery ``agent_memory.codebase_logs`` and mirror it to the Fivetran Google
Sheet. When a conversation ends we deterministically compress the whole session
into a JSON + Markdown handoff (``context_compressed``) so any other agent
(Antigravity, a teammate, Face 2) can load the full context.

IMPORTANT (Windows): Cursor must invoke this file with python.exe DIRECTLY.
Routing through a ``.cmd``/``.bat`` wrapper drops stdin on Windows, which means
hooks fire with an empty payload and nothing real gets logged. See ``hooks.json``.
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


def _bootstrap_credentials() -> None:
    """Ensure GCP creds + project are set before importing the memory store.

    Hooks launched directly by python.exe don't inherit the env vars a shell
    wrapper used to set, so we re-establish them here from well-known paths.
    """
    os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "gen-lang-client-0795401430")
    if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        for candidate in (
            _WORKSPACE / "gen-lang-client-0795401430-7e740cbd01ac.json",
            _ROOT / "gen-lang-client-0795401430-7e740cbd01ac.json",
        ):
            if candidate.is_file():
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(candidate)
                break


_bootstrap_credentials()

from dotenv import load_dotenv  # noqa: E402

load_dotenv(_ROOT / ".env")
load_dotenv(_WORKSPACE / ".env")

from modex_mcp.memory_store import (  # noqa: E402
    append_codebase_log,
    save_compressed_context,
)

_EVENT = sys.argv[1] if len(sys.argv) > 1 else ""
_CONFIG_PATHS = (
    _WORKSPACE / ".agents" / "modex.json",
    _WORKSPACE / ".cursor" / "modex.json",
    _ROOT / ".cursor" / "modex.json",
)
_AGENTS_DIR = _WORKSPACE / ".agents"
_HYDRATION_FILE = _AGENTS_DIR / "modex-hydration.md"
_TRANSCRIPT_FILE = _AGENTS_DIR / "modex-transcript.md"
_SESSION_MARKER = _AGENTS_DIR / ".modex-active-session"
_DEBUG_LOG = _AGENTS_DIR / "modex-hook-debug.log"


# --------------------------------------------------------------------------- #
# config + identity
# --------------------------------------------------------------------------- #
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
        "developer_id": os.getenv("MODEX_DEVELOPER_ID", file_cfg.get("developer_id", "")),
        "auto_hydrate": file_cfg.get("auto_hydrate", True),
    }


def _developer_id() -> str:
    cfg = _cfg()
    if cfg["developer_id"]:
        return cfg["developer_id"]
    for cwd in _repo_search_paths({}):
        try:
            r = subprocess.run(
                ["git", "-C", cwd, "config", "user.email"],
                capture_output=True,
                text=True,
                timeout=3,
                check=False,
            )
            if r.stdout.strip():
                return r.stdout.strip()
        except (OSError, subprocess.TimeoutExpired):
            continue
    return os.getenv("USERNAME") or os.getenv("USER") or "developer"


# --------------------------------------------------------------------------- #
# repo + session resolution
# --------------------------------------------------------------------------- #
def _git_repo(cwd: str) -> str | None:
    try:
        r = subprocess.run(
            ["git", "-C", cwd, "remote", "get-url", "origin"],
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


def _repo_search_paths(payload: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    cwd = payload.get("cwd") or _ag_cwd(payload)
    if isinstance(cwd, str) and cwd.strip():
        paths.append(cwd.strip())
    for root in payload.get("workspace_roots") or []:
        if isinstance(root, str) and root.strip():
            paths.append(root.strip())
    # Known locations: the workspace root is not a git repo here; the actual
    # origin lives in the agentic-data-platform subfolder.
    paths.extend(
        [
            str(_ROOT),
            str(_WORKSPACE / "agentic-data-platform"),
            str(_WORKSPACE),
        ]
    )
    seen: set[str] = set()
    out: list[str] = []
    for p in paths:
        if p and p not in seen:
            seen.add(p)
            out.append(p)
    return out


def _project_repo(payload: dict[str, Any]) -> str:
    cfg = _cfg()
    for path in _repo_search_paths(payload):
        repo = _git_repo(path)
        if repo:
            return repo
        nested = Path(path) / "agentic-data-platform"
        if nested.is_dir():
            repo = _git_repo(str(nested))
            if repo:
                return repo
    return cfg["project_repo"]


def _session_id(payload: dict[str, Any]) -> str:
    """Cursor sends ``conversation_id`` (stable per chat); ``session_id`` only
    on sessionStart. Antigravity may use ``conversation_id``/``thread_id``."""
    for key in ("conversation_id", "session_id", "thread_id", "parent_conversation_id"):
        val = payload.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    env_sid = os.getenv("MODEX_SESSION_ID", "").strip()
    if env_sid:
        return env_sid
    try:
        if _SESSION_MARKER.is_file():
            marker = _SESSION_MARKER.read_text(encoding="utf-8").strip()
            if marker:
                return marker
    except OSError:
        pass
    return "unknown-session"


def _set_active_session(sid: str) -> None:
    try:
        _AGENTS_DIR.mkdir(parents=True, exist_ok=True)
        _SESSION_MARKER.write_text(sid, encoding="utf-8")
    except OSError:
        pass
    os.environ["MODEX_SESSION_ID"] = sid


# --------------------------------------------------------------------------- #
# payload field extractors (tolerant to Cursor + Antigravity shapes)
# --------------------------------------------------------------------------- #
def _prompt_text(payload: dict[str, Any]) -> str:
    for key in ("prompt", "user_prompt", "message", "input", "user_message", "text"):
        val = payload.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def _response_text(payload: dict[str, Any]) -> str:
    for key in ("text", "response", "assistant_message", "content"):
        val = payload.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def _tool_name(payload: dict[str, Any]) -> str:
    for key in ("tool_name", "name", "tool", "toolName"):
        val = payload.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def _tool_input(payload: dict[str, Any]) -> dict[str, Any]:
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


def _file_path(payload: dict[str, Any], args: dict[str, Any] | None = None) -> str:
    args = args or {}
    for key in ("file_path", "filePath", "TargetFile", "FilePath", "path", "AbsolutePath"):
        val = payload.get(key) or args.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def _ag_cwd(payload: dict[str, Any]) -> str | None:
    args = _tool_input(payload)
    for key in ("cwd", "Cwd", "working_directory", "workspace"):
        val = payload.get(key) or args.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return None


# --------------------------------------------------------------------------- #
# logging + hydration helpers
# --------------------------------------------------------------------------- #
def _debug(raw: str, payload: dict[str, Any]) -> None:
    if os.getenv("MODEX_HOOK_DEBUG", "1") not in ("1", "true", "yes"):
        return
    try:
        _AGENTS_DIR.mkdir(parents=True, exist_ok=True)
        entry: dict[str, Any] = {
            "event": _EVENT,
            "raw_len": len(raw or ""),
            "parsed": bool(payload),
            "keys": sorted(payload.keys()),
            "conversation_id": payload.get("conversation_id"),
            "tool_name": payload.get("tool_name"),
            "file_path": payload.get("file_path"),
        }
        if not payload and raw and raw.strip():
            entry["parse_failed"] = True
            entry["raw_preview"] = (raw or "")[:120]
        with _DEBUG_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, default=str) + "\n")
    except OSError:
        pass


def _safe_log(**kwargs: Any) -> None:
    try:
        res = append_codebase_log(**kwargs)
        if isinstance(res, dict) and res.get("status") != "success":
            print(f"modex hook bq error: {res.get('message')}", file=sys.stderr)
    except Exception as exc:  # noqa: BLE001
        print(f"modex hook log failed: {exc}", file=sys.stderr)


def _hydration_context(project_repo: str) -> str:
    # Prefer the latest deterministic compressed pack; fall back to Face 2 graph.
    try:
        from modex_mcp.context_compress import render_hydration_from_context
        from modex_mcp.memory_store import load_latest_compressed_context

        packed = load_latest_compressed_context(project_repo)
        blob = packed.get("context_json") if packed.get("status") == "success" else None
        if isinstance(blob, dict) and blob:
            return render_hydration_from_context(blob)
    except Exception:  # noqa: BLE001
        pass
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
            "# MoDeX shared memory (auto-loaded)\n\n" + ctx + "\n", encoding="utf-8"
        )
    except OSError as exc:
        print(f"modex hydration write failed: {exc}", file=sys.stderr)


def _write_transcript_files(transcript_md: str) -> None:
    if not transcript_md or not transcript_md.strip():
        return
    try:
        _AGENTS_DIR.mkdir(parents=True, exist_ok=True)
        _TRANSCRIPT_FILE.write_text(transcript_md, encoding="utf-8")
        _HYDRATION_FILE.write_text(transcript_md, encoding="utf-8")
    except OSError as exc:
        print(f"modex transcript write failed: {exc}", file=sys.stderr)


def _compress_session(payload: dict[str, Any], repo: str, sid: str) -> None:
    """Deterministically compress the session into a JSON + Markdown handoff
    and persist it (BigQuery + Sheet) so other agents can load full context."""
    try:
        compressed = save_compressed_context(
            developer_id=_developer_id(),
            agent_tool=_cfg()["agent_tool"],
            project_repo=repo,
            session_id=sid if sid != "unknown-session" else None,
        )
        md = compressed.get("transcript_md") or compressed.get("hydration_prompt")
        if md:
            _write_transcript_files(md)
    except Exception as exc:  # noqa: BLE001
        print(f"modex compress failed: {exc}", file=sys.stderr)


def _ensure_session(payload: dict[str, Any], *, ide: str) -> str:
    """Open a session (log session_start + hydrate) the first time we see a new
    conversation id. Handles resumed chats where sessionStart never fires."""
    sid = _session_id(payload)
    if sid == "unknown-session":
        sid = str(uuid.uuid4())
    try:
        prev = (
            _SESSION_MARKER.read_text(encoding="utf-8").strip()
            if _SESSION_MARKER.is_file()
            else ""
        )
    except OSError:
        prev = ""
    if prev != sid:
        cfg = _cfg()
        repo = _project_repo(payload)
        mode = payload.get("composer_mode", "agent")
        _safe_log(
            developer_id=_developer_id(),
            agent_tool=cfg["agent_tool"],
            project_repo=repo,
            event_type="session_start",
            summary=f"{ide} session started ({mode})",
            session_id=sid,
            payload={"composer_mode": mode, "auto": True, "ide": ide},
        )
        if cfg.get("auto_hydrate", True):
            _write_hydration_file(repo)
    _set_active_session(sid)
    return sid


# --------------------------------------------------------------------------- #
# Cursor handlers
# --------------------------------------------------------------------------- #
def _handle_session_start(payload: dict[str, Any]) -> dict[str, Any]:
    cfg = _cfg()
    repo = _project_repo(payload)
    sid = payload.get("session_id") or _session_id(payload)
    if sid == "unknown-session":
        sid = str(uuid.uuid4())
    mode = payload.get("composer_mode", "agent")
    _set_active_session(sid)
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
        }
    }
    if cfg.get("auto_hydrate", True):
        ctx = _hydration_context(repo)
        if ctx:
            out["additional_context"] = (
                "## MoDeX shared memory (auto-loaded at session start)\n\n"
                + ctx
                + "\n\n---\nBuild on this context; log new decisions when they matter."
            )
    return out


def _handle_before_prompt(payload: dict[str, Any]) -> dict[str, Any]:
    sid = _ensure_session(payload, ide="Cursor")
    prompt = _prompt_text(payload)
    if prompt:
        cfg = _cfg()
        _safe_log(
            developer_id=_developer_id(),
            agent_tool=cfg["agent_tool"],
            project_repo=_project_repo(payload),
            event_type="user_prompt",
            summary=prompt[:4000],
            session_id=sid,
            payload={
                "auto": True,
                "full_text": prompt[:16000],
                "generation_id": payload.get("generation_id"),
            },
        )
    return {"continue": True}


def _handle_after_agent_response(payload: dict[str, Any]) -> dict[str, Any]:
    text = _response_text(payload)
    if not text:
        return {}
    cfg = _cfg()
    _safe_log(
        developer_id=_developer_id(),
        agent_tool=cfg["agent_tool"],
        project_repo=_project_repo(payload),
        event_type="agent_response",
        summary=text[:4000],
        session_id=_session_id(payload),
        payload={
            "auto": True,
            "full_text": text[:16000],
            "generation_id": payload.get("generation_id"),
        },
    )
    return {}


def _handle_after_file_edit(payload: dict[str, Any]) -> dict[str, Any]:
    path = _file_path(payload)
    edits = payload.get("edits") or []
    if not path:
        return {}
    cfg = _cfg()
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
    name = _tool_name(payload)
    if not name:
        return {}
    if "modex-memory" in name.lower():
        return {}
    cfg = _cfg()
    args = _tool_input(payload)
    summary = name
    if name == "Shell" and isinstance(args, dict):
        summary = f"Shell: {str(args.get('command', ''))[:500]}"
    elif isinstance(args, dict) and args:
        summary = f"{name}: {json.dumps(args, default=str)[:500]}"
    _safe_log(
        developer_id=_developer_id(),
        agent_tool=cfg["agent_tool"],
        project_repo=_project_repo(payload),
        event_type="tool_call",
        summary=summary[:4000],
        session_id=_session_id(payload),
        payload={
            "tool_name": name,
            "tool_input": args,
            "tool_output": (payload.get("tool_output") or "")[:2000],
            "duration_ms": payload.get("duration"),
            "auto": True,
        },
    )
    return {}


def _handle_after_shell(payload: dict[str, Any]) -> dict[str, Any]:
    command = (payload.get("command") or "").strip()
    if not command:
        return {}
    cfg = _cfg()
    _safe_log(
        developer_id=_developer_id(),
        agent_tool=cfg["agent_tool"],
        project_repo=_project_repo(payload),
        event_type="tool_call",
        summary=f"Shell: {command[:500]}",
        session_id=_session_id(payload),
        payload={
            "tool_name": "Shell",
            "tool_input": {"command": command},
            "tool_output": (payload.get("output") or "")[:2000],
            "duration_ms": payload.get("duration"),
            "auto": True,
            "via": "afterShellExecution",
        },
    )
    return {}


def _handle_after_mcp(payload: dict[str, Any]) -> dict[str, Any]:
    name = _tool_name(payload) or "MCP"
    if "modex-memory" in name.lower():
        return {}
    cfg = _cfg()
    args = _tool_input(payload)
    _safe_log(
        developer_id=_developer_id(),
        agent_tool=cfg["agent_tool"],
        project_repo=_project_repo(payload),
        event_type="tool_call",
        summary=f"MCP {name}: {json.dumps(args, default=str)[:500]}",
        session_id=_session_id(payload),
        payload={
            "tool_name": f"MCP:{name}",
            "tool_input": args,
            "auto": True,
            "via": "afterMCPExecution",
        },
    )
    return {}


def _handle_post_tool_failure(payload: dict[str, Any]) -> dict[str, Any]:
    name = _tool_name(payload) or "tool"
    err = (payload.get("error_message") or payload.get("error") or "unknown error")[:2000]
    cfg = _cfg()
    _safe_log(
        developer_id=_developer_id(),
        agent_tool=cfg["agent_tool"],
        project_repo=_project_repo(payload),
        event_type="error",
        summary=f"{name} failed: {err}",
        session_id=_session_id(payload),
        payload={"tool_name": name, "failure_type": payload.get("failure_type"), "auto": True},
    )
    return {}


def _handle_stop(payload: dict[str, Any]) -> dict[str, Any]:
    """Agent turn finished -> refresh the compressed handoff so the latest
    transcript is always available to the next agent."""
    repo = _project_repo(payload)
    sid = _session_id(payload)
    _compress_session(payload, repo, sid)
    return {}


def _handle_session_end(payload: dict[str, Any]) -> dict[str, Any]:
    cfg = _cfg()
    repo = _project_repo(payload)
    sid = _session_id(payload)
    reason = payload.get("reason", "ended")
    _safe_log(
        developer_id=_developer_id(),
        agent_tool=cfg["agent_tool"],
        project_repo=repo,
        event_type="session_end",
        summary=f"Session ended ({reason})",
        session_id=sid,
        payload={"reason": reason, "duration_ms": payload.get("duration_ms"), "auto": True},
    )
    _compress_session(payload, repo, sid)
    try:
        if _SESSION_MARKER.is_file():
            _SESSION_MARKER.unlink()
    except OSError:
        pass
    return {}


# --------------------------------------------------------------------------- #
# Antigravity handlers (https://antigravity.google/docs/hooks)
# --------------------------------------------------------------------------- #
def _handle_antigravity_pre_invocation(payload: dict[str, Any]) -> dict[str, Any]:
    sid = _ensure_session(payload, ide="Antigravity")
    prompt = _prompt_text(payload)
    if prompt:
        cfg = _cfg()
        _safe_log(
            developer_id=_developer_id(),
            agent_tool=cfg["agent_tool"],
            project_repo=_project_repo(payload),
            event_type="user_prompt",
            summary=prompt[:4000],
            session_id=sid,
            payload={"auto": True, "full_text": prompt[:16000], "ide": "antigravity"},
        )
    return {}


def _handle_antigravity_post_tool(payload: dict[str, Any]) -> dict[str, Any]:
    name = _tool_name(payload)
    if not name or "modex-memory" in name.lower():
        return {}
    cfg = _cfg()
    args = _tool_input(payload)
    repo = _project_repo({**payload, "cwd": _ag_cwd(payload)})
    sid = _session_id(payload)
    if name in {"edit_file", "Edit", "Write", "write_file"}:
        path = _file_path(payload, args)
        if not path:
            return {}
        _safe_log(
            developer_id=_developer_id(),
            agent_tool=cfg["agent_tool"],
            project_repo=repo,
            event_type="file_edit",
            summary=f"Edited {Path(path).name or path}",
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
        payload={"tool_name": name, "tool_input": args, "auto": True, "ide": "antigravity"},
    )
    return {}


def _handle_antigravity_stop(payload: dict[str, Any]) -> dict[str, Any]:
    return _handle_session_end(payload)


_HANDLERS = {
    # Cursor
    "sessionStart": _handle_session_start,
    "sessionEnd": _handle_session_end,
    "beforeSubmitPrompt": _handle_before_prompt,
    "afterAgentResponse": _handle_after_agent_response,
    "afterFileEdit": _handle_after_file_edit,
    "postToolUse": _handle_post_tool,
    "postToolUseFailure": _handle_post_tool_failure,
    "afterShellExecution": _handle_after_shell,
    "afterMCPExecution": _handle_after_mcp,
    "stop": _handle_stop,
    # Antigravity
    "PreInvocation": _handle_antigravity_pre_invocation,
    "PostInvocation": _handle_after_agent_response,
    "PostToolUse": _handle_antigravity_post_tool,
    "Stop": _handle_antigravity_stop,
    "SessionStart": _handle_session_start,
}


def _decode_stdin(raw_bytes: bytes) -> str:
    """Cursor on Windows may pipe UTF-16LE; manual pipes use UTF-8."""
    if not raw_bytes:
        return ""
    # Strip BOM/null-padding artifacts from UTF-16 reads mis-decoded as latin-1
    if raw_bytes[:2] in (b"\xff\xfe", b"\xfe\xff"):
        for enc in ("utf-16", "utf-16-le", "utf-16-be"):
            try:
                return raw_bytes.decode(enc)
            except UnicodeDecodeError:
                continue
    for enc in ("utf-8-sig", "utf-8", "utf-16-le", "utf-16", "latin-1"):
        try:
            text = raw_bytes.decode(enc)
            # Heuristic: UTF-16 misread as latin-1 has lots of \x00 between chars
            if "\x00" in text and enc.startswith("utf-8"):
                continue
            return text
        except UnicodeDecodeError:
            continue
    return raw_bytes.decode("utf-8", errors="replace")


def _parse_hook_json(raw: str) -> dict[str, Any]:
    text = (raw or "").strip()
    if not text:
        return {}
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass
    # Some Cursor builds wrap extra bytes; grab the outermost JSON object.
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        try:
            parsed = json.loads(text[start : end + 1])
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass
    return {}


def _read_payload() -> tuple[str, dict[str, Any]]:
    """Read hook JSON from stdin. Falls back to argv[2] for tests."""
    raw_bytes = b""
    try:
        if hasattr(sys.stdin, "buffer"):
            raw_bytes = sys.stdin.buffer.read()
        else:
            raw_bytes = sys.stdin.read().encode("utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        raw_bytes = b""
    raw = _decode_stdin(raw_bytes)
    if (not raw or not raw.strip()) and len(sys.argv) > 2:
        raw = sys.argv[2]
    payload = _parse_hook_json(raw)
    return raw, payload


def main() -> None:
    raw, payload = _read_payload()
    _debug(raw, payload)
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
