"""Deterministic log compression for MoDeX Face 1 — structure, not summarization.

Builds a full session transcript (user + assistant + tools + edits) as JSON and
Markdown so the next agent gets complete context via MCP / Fivetran / sheet mirror.
No LLM summarization — facts preserved, duplicate noise collapsed.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any

SCHEMA_VERSION = "modex.context.v2"
MAX_DECISIONS = 30
MAX_FILES = 40
MAX_TOOLS = 25
MAX_PROMPTS = 20
MAX_RESPONSES = 20
MAX_ERRORS = 10
MAX_SAMPLES = 3
MAX_TRANSCRIPT_CHARS = 48000


def _norm(text: str) -> str:
    return " ".join((text or "").lower().split())


def _parse_payload(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str) and raw.strip():
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


_REPO_DIR_HINTS = ("agentic-data-platform", "modex_mcp", "app", "frontend", "tests", "scripts")


def _rel_path(path: str) -> str:
    """Normalize an absolute IDE path to a stable repo-relative path so the same
    file isn't double-counted as both 'D:\\...\\x.py' and 'modex_mcp/x.py'."""
    if not path:
        return path
    norm = path.replace("\\", "/").strip()
    low = norm.lower()
    for hint in _REPO_DIR_HINTS:
        token = f"/{hint}/"
        idx = low.find(token)
        if idx >= 0:
            tail = norm[idx + 1 :]
            # strip the leading agentic-data-platform/ wrapper so paths match
            if tail.lower().startswith("agentic-data-platform/"):
                tail = tail[len("agentic-data-platform/") :]
            return tail
    return norm.rsplit("/", 1)[-1] if "/" in norm else norm


def _full_text(ev: dict[str, Any]) -> str:
    payload = _parse_payload(ev.get("payload_json") or ev.get("payload"))
    for key in ("full_text", "text", "decision", "context"):
        val = payload.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return (ev.get("summary") or "").strip()


def _tool_name(ev: dict[str, Any]) -> str:
    payload = _parse_payload(ev.get("payload_json") or ev.get("payload"))
    if payload.get("tool_name"):
        return str(payload["tool_name"])
    summary = (ev.get("summary") or "").strip()
    if ":" in summary:
        return summary.split(":", 1)[0].strip()
    return summary[:80] or "tool"


# Garbage produced by the earlier (broken) hook wiring: empty stdin meant file
# edits with no path and tool calls with no name. We drop these so historical
# noise never pollutes a handoff.
_NOISE_FILE_PATHS = {"", "edited  (0 change(s))"}


def _is_noise(ev: dict[str, Any]) -> bool:
    et = ev.get("event_type") or ""
    summary = (ev.get("summary") or "").strip()
    if et == "file_edit":
        path = (ev.get("file_path") or "").strip()
        if path.lower() in _NOISE_FILE_PATHS:
            return True
        if "(0 change(s))" in summary and not path:
            return True
    if et == "tool_call":
        if _tool_name(ev) in ("", "tool") and not summary.strip():
            return True
    if et == "error" and summary.lower() in ("tool failed: unknown error",):
        return True
    return False


def _build_transcript(chronological: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Ordered chat transcript for handoff — every captured turn with full text."""
    transcript: list[dict[str, Any]] = []
    seq = 0

    for ev in chronological:
        if _is_noise(ev):
            continue
        et = ev.get("event_type") or ""
        at = ev.get("created_at")
        sid = ev.get("session_id")
        who = ev.get("developer_id")
        tool = ev.get("agent_tool")
        payload = _parse_payload(ev.get("payload_json") or ev.get("payload"))
        text = _full_text(ev)

        if et == "session_start":
            seq += 1
            transcript.append({
                "seq": seq,
                "role": "system",
                "kind": "session_start",
                "text": text or "Session started",
                "at": at,
                "session_id": sid,
                "by": who,
                "tool": tool,
            })
            continue

        if et == "user_prompt" and text:
            seq += 1
            transcript.append({
                "seq": seq,
                "role": "user",
                "kind": "user_prompt",
                "text": text[:8000],
                "at": at,
                "session_id": sid,
                "by": who,
                "tool": tool,
            })
            continue

        if et == "agent_response" and text:
            seq += 1
            transcript.append({
                "seq": seq,
                "role": "assistant",
                "kind": "agent_response",
                "text": text[:16000],
                "at": at,
                "session_id": sid,
                "by": who,
                "tool": tool,
            })
            continue

        if et == "tool_call":
            seq += 1
            tinput = payload.get("tool_input") or payload.get("arguments") or payload.get("args")
            transcript.append({
                "seq": seq,
                "role": "tool",
                "kind": "tool_call",
                "tool": _tool_name(ev),
                "text": text[:4000],
                "input": tinput if isinstance(tinput, (dict, list, str)) else str(tinput or ""),
                "at": at,
                "session_id": sid,
                "by": who,
            })
            continue

        if et == "file_edit":
            seq += 1
            fp = _rel_path(ev.get("file_path") or text)
            transcript.append({
                "seq": seq,
                "role": "system",
                "kind": "file_edit",
                "text": f"Edited `{fp}`",
                "file_path": fp,
                "at": at,
                "session_id": sid,
                "by": who,
            })
            continue

        if et == "decision" and text:
            seq += 1
            transcript.append({
                "seq": seq,
                "role": "decision",
                "kind": "decision",
                "text": text[:4000],
                "context": payload.get("context") or "",
                "file_path": ev.get("file_path") or "",
                "at": at,
                "session_id": sid,
                "by": who,
            })
            continue

        if et == "error" and text:
            seq += 1
            transcript.append({
                "seq": seq,
                "role": "system",
                "kind": "error",
                "text": text[:2000],
                "tool": payload.get("tool_name") or "",
                "at": at,
                "session_id": sid,
            })
            continue

        if et == "session_end":
            seq += 1
            transcript.append({
                "seq": seq,
                "role": "system",
                "kind": "session_end",
                "text": text or "Session ended",
                "at": at,
                "session_id": sid,
            })

    return transcript


def _last(items: list[dict[str, Any]], key: str = "text") -> str:
    for item in reversed(items or []):
        val = (item.get(key) or "").strip()
        if val:
            return val
    return ""


def render_system_context(blob: dict[str, Any]) -> str:
    """Concise, actionable briefing the NEXT agent reads before doing anything.

    This is the 'same system context' handoff: who worked on what, the decisions
    that stand, approaches already rejected, files in flight, unresolved errors,
    and the last thing the user asked + the last thing the previous agent said.
    """
    repo = blob.get("project_repo", "unknown")
    sessions = blob.get("sessions") or []
    decisions = blob.get("decisions") or []
    rejected = blob.get("rejected") or []
    files = blob.get("files") or []
    errors = blob.get("errors") or []
    prompts = blob.get("prompts") or []
    responses = blob.get("responses") or []

    tools = {s.get("agent_tool") for s in sessions if s.get("agent_tool")}
    devs = {s.get("developer_id") for s in sessions if s.get("developer_id")}
    last_at = blob.get("compressed_at", "unknown")

    lines: list[str] = [
        "# MoDeX handoff — system context for the next agent",
        "",
        f"You are resuming work on `{repo}`. Prior coding-agent session(s) already "
        "happened; the shared memory below is the source of truth. Build on it — do "
        "not start from scratch or re-ask what was already decided.",
        "",
        "## Where things stand",
        f"- Sessions captured: **{len(sessions)}** "
        f"({', '.join(sorted(t for t in tools if t)) or 'unknown tool'})",
        f"- Contributors: {', '.join(sorted(d for d in devs if d)) or 'unknown'}",
        f"- Memory current as of: {last_at}",
        f"- Total events compressed: {blob.get('source_event_count', 0)}",
        "",
    ]

    if decisions:
        lines.append("## Decisions already made (honor these)")
        for d in decisions[-8:]:
            ctx = f" — {d['context']}" if d.get("context") else ""
            lines.append(f"- {d.get('text', '')}{ctx}")
        lines.append("")

    if rejected:
        lines.append("## Rejected approaches (do NOT redo)")
        for r in rejected[:8]:
            lines.append(f"- {r.get('text', '')}")
        lines.append("")

    if files:
        lines.append("## Files in flight")
        for f in sorted(files, key=lambda x: x.get("edits", 0), reverse=True)[:12]:
            lines.append(f"- `{f.get('path', '')}` ({f.get('edits', 0)} edit(s))")
        lines.append("")

    if errors:
        lines.append("## Unresolved errors / failures seen")
        for e in errors[-6:]:
            lines.append(f"- {e.get('text', '')}")
        lines.append("")

    last_prompt = _last(prompts)
    if last_prompt:
        lines.append("## What the user last asked")
        lines.append(f"> {last_prompt[:1200]}")
        lines.append("")

    last_resp = _last(responses)
    if last_resp:
        lines.append("## What the previous agent last reported")
        lines.append(f"> {last_resp[:1200]}")
        lines.append("")

    lines.append("## Your job now")
    lines.append(
        "- Continue the work above. Respect the decisions and rejected approaches.\n"
        "- If you make a new significant decision, log it via MoDeX.\n"
        "- The full turn-by-turn transcript follows for detail."
    )
    lines.append("")
    return "\n".join(lines)


def render_transcript_md(context_json: dict[str, Any]) -> str:
    """Full session handoff as Markdown — paste into the next agent's context."""
    repo = context_json.get("project_repo", "unknown")
    sid = context_json.get("session_id") or "multi-session"
    lines = [
        f"# MoDeX session transcript",
        f"",
        f"**Repo:** `{repo}`  ",
        f"**Session:** `{sid}`  ",
        f"**Schema:** {context_json.get('schema', SCHEMA_VERSION)}  ",
        f"**Compressed at:** {context_json.get('compressed_at', 'unknown')}  ",
        f"**Events captured:** {context_json.get('source_event_count', 0)}  ",
        f"",
        f"_Full chat + tool trace for the next agent. Not a summary._",
        f"",
        "---",
        f"",
    ]

    for turn in context_json.get("transcript") or []:
        role = turn.get("role", "system")
        kind = turn.get("kind", "")
        at = turn.get("at") or ""
        header = f"### [{turn.get('seq', '?')}] {role}"
        if kind:
            header += f" · {kind}"
        if at:
            header += f" · {at}"
        lines.append(header)
        lines.append("")

        if role == "tool":
            lines.append(f"**Tool:** `{turn.get('tool', '')}`")
            if turn.get("text"):
                lines.append(f"**Summary:** {turn['text']}")
            inp = turn.get("input")
            if inp:
                if isinstance(inp, (dict, list)):
                    lines.append("```json")
                    lines.append(json.dumps(inp, indent=2, default=str)[:6000])
                    lines.append("```")
                else:
                    lines.append(f"```\n{str(inp)[:4000]}\n```")
        else:
            body = (turn.get("text") or "").strip()
            if body:
                lines.append(body)
            if turn.get("context"):
                lines.append(f"\n_Context: {turn['context']}_")
            if turn.get("file_path"):
                lines.append(f"\n_File: `{turn['file_path']}`_")

        lines.append("")
        lines.append("---")
        lines.append("")

    rejected = context_json.get("rejected") or []
    if rejected:
        lines.append("## Rejected approaches (do not redo)")
        for r in rejected:
            lines.append(f"- {r.get('text')}")
        lines.append("")

    md = "\n".join(lines)
    if len(md) > MAX_TRANSCRIPT_CHARS:
        md = md[:MAX_TRANSCRIPT_CHARS] + "\n\n_(transcript truncated at 48k chars)_"
    return md


def compress_events(
    events: list[dict[str, Any]],
    *,
    project_repo: str,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Compress chronological events into JSON + transcript for agent handoff."""
    chronological = [e for e in sorted(events, key=lambda e: str(e.get("created_at") or "")) if not _is_noise(e)]

    decisions: list[dict[str, Any]] = []
    seen_decisions: set[str] = set()
    rejected: list[dict[str, Any]] = []
    seen_rejected: set[str] = set()
    files: dict[str, dict[str, Any]] = {}
    tools: dict[str, dict[str, Any]] = {}
    prompts: list[dict[str, Any]] = []
    responses: list[dict[str, Any]] = []
    seen_prompts: set[str] = set()
    errors: list[dict[str, Any]] = []
    seen_errors: set[str] = set()
    sessions: dict[str, dict[str, Any]] = {}

    for ev in chronological:
        et = ev.get("event_type") or ""
        summary = (ev.get("summary") or "").strip()
        full = _full_text(ev)
        sid = str(ev.get("session_id") or "unknown")
        at = ev.get("created_at")
        payload = _parse_payload(ev.get("payload_json") or ev.get("payload"))

        if sid not in sessions:
            sessions[sid] = {
                "session_id": sid,
                "developer_id": ev.get("developer_id"),
                "agent_tool": ev.get("agent_tool"),
                "started_at": None,
                "ended_at": None,
                "event_count": 0,
            }
        sessions[sid]["event_count"] += 1
        if et == "session_start":
            sessions[sid]["started_at"] = at
        if et == "session_end":
            sessions[sid]["ended_at"] = at

        for ra in payload.get("rejected_approaches") or []:
            text = str(ra).strip()
            key = _norm(text)
            if text and key not in seen_rejected:
                seen_rejected.add(key)
                rejected.append({"text": text, "source": "session_end", "at": at, "session_id": sid})

        if et == "decision" and summary:
            key = _norm(summary)
            if key not in seen_decisions:
                seen_decisions.add(key)
                decisions.append({
                    "text": summary,
                    "context": payload.get("context") or "",
                    "file": ev.get("file_path") or "",
                    "at": at,
                    "by": ev.get("developer_id"),
                    "tool": ev.get("agent_tool"),
                    "session_id": sid,
                })
            if re.search(r"\breject(ed|ion|s)?\b", summary, re.I):
                rkey = _norm(summary)
                if rkey not in seen_rejected:
                    seen_rejected.add(rkey)
                    rejected.append({"text": summary, "source": "decision_event", "at": at, "session_id": sid})

        if et == "agent_response" and full:
            responses.append({
                "text": full[:16000],
                "at": at,
                "by": ev.get("developer_id"),
                "session_id": sid,
            })

        if et == "file_edit":
            path = _rel_path((ev.get("file_path") or summary or "unknown").strip())
            if path not in files:
                files[path] = {"path": path, "edits": 0, "first_at": at, "last_at": at, "by": ev.get("developer_id")}
            files[path]["edits"] += 1
            files[path]["last_at"] = at

        if et == "tool_call":
            name = _tool_name(ev)
            if name not in tools:
                tools[name] = {"tool": name, "count": 0, "last_at": at, "last_summary": summary[:240], "samples": []}
            rec = tools[name]
            rec["count"] += 1
            rec["last_at"] = at
            rec["last_summary"] = summary[:240]
            if len(rec["samples"]) < MAX_SAMPLES and summary not in rec["samples"]:
                rec["samples"].append(summary[:180])

        if et == "user_prompt" and full:
            key = _norm(full[:240])
            if key not in seen_prompts:
                seen_prompts.add(key)
                prompts.append({"text": full[:8000], "at": at, "by": ev.get("developer_id"), "session_id": sid})

        if et == "error" and summary:
            key = _norm(summary)
            if key not in seen_errors:
                seen_errors.add(key)
                errors.append({"text": summary[:500], "tool": payload.get("tool_name") or "", "at": at, "session_id": sid})

    transcript = _build_transcript(chronological)

    blob = {
        "schema": SCHEMA_VERSION,
        "kind": "compressed_context",
        "project_repo": project_repo,
        "session_id": session_id,
        "compressed_at": datetime.now(timezone.utc).isoformat(),
        "source_event_count": len(chronological),
        "sessions": list(sessions.values()),
        "transcript": transcript,
        "decisions": decisions[-MAX_DECISIONS:],
        "rejected": rejected[:MAX_DECISIONS],
        "files": list(files.values())[-MAX_FILES:],
        "tools": sorted(tools.values(), key=lambda t: t["count"], reverse=True)[:MAX_TOOLS],
        "prompts": prompts[-MAX_PROMPTS:],
        "responses": responses[-MAX_RESPONSES:],
        "errors": errors[-MAX_ERRORS:],
    }
    blob["system_context"] = render_system_context(blob)
    blob["transcript_md"] = blob["system_context"] + "\n\n---\n\n" + render_transcript_md(blob)
    blob["session_summary"] = render_session_summary_paragraph(blob)
    return blob


def render_session_summary_paragraph(blob: dict[str, Any]) -> str:
    """One plain-English paragraph summarising the session — readable by humans and agents.

    This is the column the judge sees when opening the Google Sheet. It answers:
    who worked on what, what was decided, what was rejected, what files changed,
    and what the user was asking for at the end.
    """
    repo = blob.get("project_repo") or "unknown repo"
    sessions = blob.get("sessions") or []
    decisions = blob.get("decisions") or []
    rejected = blob.get("rejected") or []
    files = blob.get("files") or []
    prompts = blob.get("prompts") or []
    responses = blob.get("responses") or []
    errors = blob.get("errors") or []
    event_count = blob.get("source_event_count", 0)

    devs = sorted({s.get("developer_id") for s in sessions if s.get("developer_id")})
    tools = sorted({s.get("agent_tool") for s in sessions if s.get("agent_tool")})
    dev_str = " and ".join(devs) if devs else "an unknown developer"
    tool_str = " + ".join(tools) if tools else "an unknown IDE"

    parts: list[str] = []

    # Who did what
    parts.append(
        f"In this session, {dev_str} worked on {repo} using {tool_str} "
        f"({event_count} events captured)."
    )

    # Decisions
    if decisions:
        d_texts = [d.get("text", "").strip() for d in decisions[-5:] if d.get("text")]
        parts.append(
            f"{len(decisions)} engineering decision(s) made: "
            + "; ".join(d_texts[:5])
            + "."
        )

    # Rejected approaches
    if rejected:
        r_texts = [r.get("text", "").strip() for r in rejected[:4] if r.get("text")]
        parts.append(
            f"{len(rejected)} approach(es) tried and rejected: "
            + "; ".join(r_texts[:4])
            + "."
        )

    # Files touched
    if files:
        top_files = sorted(files, key=lambda f: f.get("edits", 0), reverse=True)[:6]
        f_list = ", ".join(
            f"{f.get('path', '?')} ({f.get('edits', 0)} edit(s))" for f in top_files
        )
        parts.append(f"{len(files)} file(s) modified: {f_list}.")

    # Errors
    if errors:
        parts.append(f"{len(errors)} error(s) recorded during the session.")

    # What the user last asked
    last_prompt = _last(prompts)
    if last_prompt:
        short = last_prompt[:300].replace("\n", " ")
        parts.append(f'Last user request: "{short}".')

    # What the agent last said
    last_resp = _last(responses)
    if last_resp:
        short = last_resp[:200].replace("\n", " ")
        parts.append(f'Last agent action: "{short}".')

    return " ".join(parts)


def compression_summary_line(blob: dict[str, Any]) -> str:
    turns = len(blob.get("transcript") or [])
    return (
        f"{blob.get('schema', SCHEMA_VERSION)} · "
        f"{turns} turns · "
        f"{len(blob.get('decisions', []))} decisions · "
        f"{len(blob.get('files', []))} files · "
        f"{blob.get('source_event_count', 0)} events"
    )


def render_hydration_from_context(context_json: dict[str, Any]) -> str:
    """The artifact injected into the next agent: briefing + full transcript."""
    if context_json.get("transcript_md"):
        return context_json["transcript_md"]
    briefing = context_json.get("system_context") or render_system_context(context_json)
    return briefing + "\n\n---\n\n" + render_transcript_md(context_json)


def merge_context_blobs(blobs: list[dict[str, Any]], project_repo: str) -> dict[str, Any]:
    if not blobs:
        return {}
    if len(blobs) == 1:
        return blobs[0]

    all_events: list[dict[str, Any]] = []
    for blob in blobs:
        for turn in blob.get("transcript") or []:
            kind = turn.get("kind") or "user_prompt"
            et_map = {
                "user_prompt": "user_prompt",
                "agent_response": "agent_response",
                "tool_call": "tool_call",
                "file_edit": "file_edit",
                "decision": "decision",
                "error": "error",
                "session_start": "session_start",
                "session_end": "session_end",
            }
            all_events.append({
                "event_type": et_map.get(kind, "user_prompt"),
                "summary": turn.get("text") or "",
                "file_path": turn.get("file_path") or "",
                "created_at": turn.get("at"),
                "developer_id": turn.get("by"),
                "agent_tool": turn.get("tool"),
                "session_id": turn.get("session_id") or blob.get("session_id"),
                "payload_json": turn,
            })
    merged = compress_events(all_events, project_repo=project_repo)
    merged["merged_from_sessions"] = [b.get("session_id") for b in blobs if b.get("session_id")]
    merged["source_event_count"] = sum(b.get("source_event_count", 0) for b in blobs)
    return merged
