"""MoDeX Face 1 memory store — append-only codebase logs + session handoff."""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import urllib.error
import urllib.request

import google.auth
import google.auth.transport.requests
from dotenv import load_dotenv
from google.cloud import bigquery

_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(_ROOT / ".env")
load_dotenv(_ROOT.parent / ".env")

GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "gen-lang-client-0795401430")
MEMORY_DATASET = os.getenv("MODEX_MEMORY_DATASET", "agent_memory")
MEMORY_TABLE = os.getenv("MODEX_MEMORY_TABLE", "session_logs")
CODEBASE_LOGS_TABLE = os.getenv("MODEX_CODEBASE_LOGS_TABLE", "codebase_logs")
MEMORY_FULL_TABLE = f"{GOOGLE_CLOUD_PROJECT}.{MEMORY_DATASET}.{MEMORY_TABLE}"
CODEBASE_LOGS_FULL_TABLE = (
    f"{GOOGLE_CLOUD_PROJECT}.{MEMORY_DATASET}.{CODEBASE_LOGS_TABLE}"
)

def _parse_sheet_id(raw: str) -> str:
    """Accept bare ID or full Google Sheets URL."""
    raw = (raw or "").strip()
    if "/d/" in raw:
        return raw.split("/d/")[1].split("/")[0]
    return raw


MEMORY_SHEET_ID = _parse_sheet_id(
    os.getenv("MODEX_MEMORY_SHEET_ID", os.getenv("ACTION_REPORT_SHEET_ID", ""))
)
MEMORY_SHEET_RANGE = os.getenv("MODEX_MEMORY_SHEET_RANGE", "MoDeX Memory!A1")
LOG_SHEET_RANGE = os.getenv("MODEX_LOG_SHEET_RANGE", "MoDex_Logs!A1")

# On Cloud Run the runtime (compute) SA has no Sheets access, so we impersonate
# the dedicated sheet-writer SA the spreadsheet is shared with. Locally this is
# unset and we fall back to the ambient credentials (the sheet-writer key).
SHEET_IMPERSONATE_SA = os.getenv("MODEX_SHEET_IMPERSONATE_SA", "")
SHEET_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def _sheet_access_token() -> str:
    """Mint an OAuth token with Sheets scope, impersonating if configured."""
    request = google.auth.transport.requests.Request()
    if SHEET_IMPERSONATE_SA:
        from google.auth import impersonated_credentials

        source, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        creds = impersonated_credentials.Credentials(
            source_credentials=source,
            target_principal=SHEET_IMPERSONATE_SA,
            target_scopes=SHEET_SCOPES,
        )
    else:
        creds, _ = google.auth.default(scopes=SHEET_SCOPES)
    creds.refresh(request)
    return creds.token

VALID_EVENT_TYPES = frozenset({
    "session_start",
    "user_prompt",
    "agent_response",
    "tool_call",
    "file_edit",
    "decision",
    "error",
    "session_end",
    "context_compressed",
})

CODEBASE_LOG_COLUMNS = [
    "event_id",
    "session_id",
    "developer_id",
    "agent_tool",
    "project_repo",
    "event_type",
    "file_path",
    "commit_sha",
    "summary",
    "payload_json",
    "parent_event_id",
    "created_at",
    "context_json",
    "transcript_md",
    "session_summary",
]

MEMORY_COLUMNS = [
    "session_id",
    "developer_id",
    "agent_tool",
    "project_repo",
    "memory_type",
    "summary",
    "decisions_json",
    "files_touched",
    "rejected_approaches",
    "context_json",
    "transcript_md",
    "created_at",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _bq_client() -> bigquery.Client:
    return bigquery.Client(project=GOOGLE_CLOUD_PROJECT)


def _ensure_dataset(client: bigquery.Client) -> None:
    dataset_ref = bigquery.Dataset(f"{GOOGLE_CLOUD_PROJECT}.{MEMORY_DATASET}")
    dataset_ref.location = "US"
    try:
        client.get_dataset(dataset_ref.dataset_id)
    except Exception:
        client.create_dataset(dataset_ref, exists_ok=True)


def ensure_codebase_logs_table() -> dict[str, Any]:
    """Create append-only agent_memory.codebase_logs (primary memory store)."""
    client = _bq_client()
    _ensure_dataset(client)
    schema = [
        bigquery.SchemaField("event_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("session_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("developer_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("agent_tool", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("project_repo", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("event_type", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("file_path", "STRING"),
        bigquery.SchemaField("commit_sha", "STRING"),
        bigquery.SchemaField("summary", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("payload_json", "STRING"),
        bigquery.SchemaField("parent_event_id", "STRING"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("context_json", "STRING"),
        bigquery.SchemaField("transcript_md", "STRING"),
        bigquery.SchemaField("session_summary", "STRING"),
    ]
    table = bigquery.Table(CODEBASE_LOGS_FULL_TABLE, schema=schema)
    client.create_table(table, exists_ok=True)
    _migrate_codebase_logs_schema(client)
    return {"status": "success", "table": CODEBASE_LOGS_FULL_TABLE}


def _migrate_codebase_logs_schema(client: bigquery.Client) -> None:
    """Add columns introduced after initial deploy (idempotent)."""
    try:
        table = client.get_table(CODEBASE_LOGS_FULL_TABLE)
    except Exception:
        return
    existing = {f.name for f in table.schema}
    additions = []
    if "session_summary" not in existing:
        additions.append(bigquery.SchemaField("session_summary", "STRING"))
    if not additions:
        return
    new_schema = list(table.schema) + additions
    table.schema = new_schema
    client.update_table(table, ["schema"])


def ensure_memory_table() -> dict[str, Any]:
    """Create legacy session_logs summary table (derived / backward compatible)."""
    client = _bq_client()
    _ensure_dataset(client)
    schema = [
        bigquery.SchemaField("session_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("developer_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("agent_tool", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("project_repo", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("memory_type", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("summary", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("decisions_json", "STRING"),
        bigquery.SchemaField("files_touched", "STRING"),
        bigquery.SchemaField("rejected_approaches", "STRING"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
    ]
    table = bigquery.Table(MEMORY_FULL_TABLE, schema=schema)
    client.create_table(table, exists_ok=True)
    return {"status": "success", "table": MEMORY_FULL_TABLE}


def ensure_all_tables() -> dict[str, Any]:
    logs = ensure_codebase_logs_table()
    legacy = ensure_memory_table()
    return {
        "status": "success",
        "primary": logs["table"],
        "legacy_summary": legacy["table"],
    }


def _append_sheet_row(row: dict[str, Any], columns: list[str], range_name: str) -> dict[str, Any] | None:
    if not MEMORY_SHEET_ID:
        return None

    values = [[str(row.get(col, "")) for col in columns]]
    token = _sheet_access_token()
    url = (
        f"https://sheets.googleapis.com/v4/spreadsheets/{MEMORY_SHEET_ID}/values/"
        f"{range_name}:append?valueInputOption=USER_ENTERED"
    )
    body = json.dumps({"values": values}).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
        return {"sheet_updated_range": result.get("updates", {}).get("updatedRange")}
    except urllib.error.HTTPError as exc:
        return {"sheet_error": exc.read().decode()[:300]}


def _normalize_events(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        rec = dict(row)
        raw = rec.get("payload_json")
        if isinstance(raw, str) and raw:
            try:
                rec["payload_json"] = json.loads(raw)
            except json.JSONDecodeError:
                pass
        if hasattr(rec.get("created_at"), "isoformat"):
            rec["created_at"] = rec["created_at"].isoformat()
        out.append(rec)
    return out


def append_codebase_log(
    *,
    developer_id: str,
    agent_tool: str,
    project_repo: str,
    event_type: str,
    summary: str,
    session_id: str | None = None,
    file_path: str | None = None,
    commit_sha: str | None = None,
    payload: dict[str, Any] | None = None,
    parent_event_id: str | None = None,
    context_json: str | dict[str, Any] | None = None,
    transcript_md: str | None = None,
    session_summary: str | None = None,
) -> dict[str, Any]:
    """Append one immutable event to codebase_logs (primary MoDeX memory)."""
    if event_type not in VALID_EVENT_TYPES:
        return {
            "status": "error",
            "message": f"Invalid event_type. Use one of: {sorted(VALID_EVENT_TYPES)}",
        }

    sid = session_id or str(uuid.uuid4())
    created = _now_iso()
    pl = dict(payload or {})
    if context_json is not None:
        pl["context_json"] = (
            context_json if isinstance(context_json, dict)
            else json.loads(context_json) if isinstance(context_json, str) and context_json.strip().startswith("{")
            else context_json
        )
    if transcript_md:
        pl["transcript_md"] = transcript_md

    ctx_col = ""
    if context_json is not None:
        ctx_col = (
            context_json if isinstance(context_json, str)
            else json.dumps(context_json, default=str)
        )
    md_col = transcript_md or ""

    row = {
        "event_id": str(uuid.uuid4()),
        "session_id": sid,
        "developer_id": developer_id,
        "agent_tool": agent_tool,
        "project_repo": project_repo,
        "event_type": event_type,
        "file_path": file_path or "",
        "commit_sha": commit_sha or "",
        "summary": summary[:4000],
        "payload_json": json.dumps(pl, default=str),
        "parent_event_id": parent_event_id or "",
        "created_at": created,
        "context_json": ctx_col[:50000] if ctx_col else "",
        "transcript_md": md_col[:50000] if md_col else "",
        "session_summary": (session_summary or "")[:4000],
    }

    client = _bq_client()
    errors = client.insert_rows_json(CODEBASE_LOGS_FULL_TABLE, [row])
    if errors:
        # Backward compat: older BQ tables may lack session_summary (added in v2).
        slim = {
            k: v
            for k, v in row.items()
            if k not in ("context_json", "transcript_md", "session_summary")
        }
        errors = client.insert_rows_json(CODEBASE_LOGS_FULL_TABLE, [slim])
    if errors:
        return {"status": "error", "message": str(errors)}

    # Sheet mirror: use slim row if sheet header lacks session_summary column.
    sheet_row = row
    sheet_result = _append_sheet_row(sheet_row, CODEBASE_LOG_COLUMNS, LOG_SHEET_RANGE)
    if sheet_result and sheet_result.get("sheet_error") and row.get("session_summary"):
        sheet_row = {k: v for k, v in row.items() if k != "session_summary"}
        sheet_result = _append_sheet_row(
            sheet_row, [c for c in CODEBASE_LOG_COLUMNS if c != "session_summary"], LOG_SHEET_RANGE
        )
    return {
        "status": "success",
        "event_id": row["event_id"],
        "session_id": sid,
        "event_type": event_type,
        "table": CODEBASE_LOGS_FULL_TABLE,
        "created_at": created,
        "fivetran_mirror": sheet_result,
    }


def _fetch_log_events(
    project_repo: str,
    *,
    limit: int = 200,
    session_id: str | None = None,
    event_types: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Load raw codebase log rows from BigQuery."""
    limit = max(1, min(limit, 500))
    where = "project_repo = @project_repo"
    params: list[bigquery.ScalarQueryParameter | bigquery.ArrayQueryParameter] = [
        bigquery.ScalarQueryParameter("project_repo", "STRING", project_repo),
    ]
    if session_id:
        where += " AND session_id = @session_id"
        params.append(bigquery.ScalarQueryParameter("session_id", "STRING", session_id))
    if event_types:
        cleaned = [e for e in event_types if e in VALID_EVENT_TYPES]
        if cleaned:
            where += " AND event_type IN UNNEST(@event_types)"
            params.append(bigquery.ArrayQueryParameter("event_types", "STRING", cleaned))

    sql = f"""
        SELECT *
        FROM `{CODEBASE_LOGS_FULL_TABLE}`
        WHERE {where}
        ORDER BY created_at DESC
        LIMIT {limit}
    """
    client = _bq_client()
    result = client.query(
        sql, job_config=bigquery.QueryJobConfig(query_parameters=params)
    ).result()
    return _normalize_events([dict(r.items()) for r in result])


def save_compressed_context(
    *,
    developer_id: str,
    agent_tool: str,
    project_repo: str,
    session_id: str | None = None,
    event_limit: int = 300,
) -> dict[str, Any]:
    """Compress raw session/repo logs into JSON and persist as context_compressed event.

    The full JSON lives in payload_json (synced by Fivetran from MoDex_Logs sheet).
    This is structural compression — dedupe/group — not LLM summarization.
    """
    from modex_mcp.context_compress import (
        compress_events,
        compression_summary_line,
        render_hydration_from_context,
    )

    try:
        events = _fetch_log_events(
            project_repo,
            limit=event_limit,
            session_id=session_id,
        )
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "message": str(exc)}

    if not events:
        return {
            "status": "success",
            "project_repo": project_repo,
            "session_id": session_id,
            "context_json": {},
            "message": "No events to compress.",
        }

    chronological = list(reversed(events))
    context_json = compress_events(
        chronological,
        project_repo=project_repo,
        session_id=session_id,
    )
    from modex_mcp.context_compress import render_hydration_from_context

    # Use the briefing-inclusive handoff (system context + full transcript) that
    # compress_events already built, so the Sheet/BQ transcript_md column gives
    # the next agent the actionable briefing, not just a raw transcript.
    transcript_md = context_json.get("transcript_md") or render_hydration_from_context(
        context_json
    )
    summary = compression_summary_line(context_json)
    session_summary = context_json.get("session_summary") or ""

    log_result = append_codebase_log(
        developer_id=developer_id,
        agent_tool=agent_tool,
        project_repo=project_repo,
        event_type="context_compressed",
        summary=summary[:4000],
        session_id=session_id or chronological[-1].get("session_id"),
        payload={
            "context_json": context_json,
            "transcript_md": transcript_md,
            "compression": "deterministic",
            "not_summarized": True,
        },
        context_json=context_json,
        transcript_md=transcript_md,
        session_summary=session_summary,
    )
    if log_result.get("status") != "success":
        return log_result

    return {
        "status": "success",
        "event_id": log_result.get("event_id"),
        "session_id": log_result.get("session_id"),
        "context_json": context_json,
        "transcript_md": transcript_md,
        "hydration_prompt": transcript_md or render_hydration_from_context(context_json),
        "summary": summary,
        "fivetran_mirror": log_result.get("fivetran_mirror"),
        "message": (
            "Compressed context saved. Fivetran will sync payload_json to BigQuery "
            "for other agents to load_context."
        ),
    }


def load_latest_compressed_context(
    project_repo: str,
    *,
    limit: int = 3,
) -> dict[str, Any]:
    """Fetch the most recent context_compressed JSON packs for a repo."""
    from modex_mcp.context_compress import merge_context_blobs

    try:
        rows = _fetch_log_events(
            project_repo,
            limit=max(1, min(limit, 10)),
            event_types=["context_compressed"],
        )
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "message": str(exc)}

    blobs: list[dict[str, Any]] = []
    for row in reversed(rows):
        payload = row.get("payload_json") or {}
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError:
                payload = {}
        blob = payload.get("context_json")
        if isinstance(blob, dict):
            blobs.append(blob)

    if not blobs:
        return {"status": "success", "project_repo": project_repo, "context_json": None, "packs": []}

    merged = merge_context_blobs(blobs, project_repo) if len(blobs) > 1 else blobs[-1]
    return {
        "status": "success",
        "project_repo": project_repo,
        "context_json": merged,
        "transcript_md": (merged or {}).get("transcript_md") if isinstance(merged, dict) else None,
        "packs": blobs,
        "pack_count": len(blobs),
    }


def load_context_from_logs(
    project_repo: str,
    limit: int = 50,
    event_types: list[str] | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Replay recent codebase logs to hydrate a new agent session."""
    limit = max(1, min(limit, 200))
    try:
        events = _fetch_log_events(
            project_repo,
            limit=limit,
            session_id=session_id,
            event_types=event_types,
        )
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "error",
            "message": str(exc),
            "hint": "Run: uv run python scripts/setup_agent_memory.py",
        }

    if not events:
        return {
            "status": "success",
            "project_repo": project_repo,
            "event_count": 0,
            "events": [],
            "hydration_prompt": (
                f"No codebase logs for {project_repo}. This agent starts fresh."
            ),
        }

    chronological = list(reversed(events))
    lines = []
    for ev in chronological[-30:]:
        fp = f" [{ev.get('file_path')}]" if ev.get("file_path") else ""
        lines.append(
            f"- [{ev.get('created_at')}] {ev.get('event_type')}{fp} "
            f"({ev.get('developer_id')} / {ev.get('agent_tool')}): {ev.get('summary')}"
        )

    decisions = [e for e in chronological if e.get("event_type") == "decision"]
    edits = [e for e in chronological if e.get("event_type") == "file_edit"]
    errors = [e for e in chronological if e.get("event_type") == "error"]

    hydration_parts = [
        f"Codebase log context for {project_repo} ({len(chronological)} events, newest last):",
        *lines,
    ]
    if decisions:
        hydration_parts.append(
            "Key decisions: " + "; ".join(d.get("summary", "") for d in decisions[-5:])
        )
    if edits:
        hydration_parts.append(
            "Recent files: "
            + ", ".join(
                {str(e.get("file_path")) for e in edits[-10:] if e.get("file_path")}
            )
        )
    if errors:
        hydration_parts.append(
            "Recent errors: " + "; ".join(e.get("summary", "") for e in errors[-3:])
        )

    compressed = load_latest_compressed_context(project_repo)
    context_json = compressed.get("context_json") if compressed.get("status") == "success" else None
    transcript_md = compressed.get("transcript_md") if compressed.get("status") == "success" else None
    hydration = "\n".join(hydration_parts)
    if transcript_md:
        hydration = transcript_md
    elif context_json:
        from modex_mcp.context_compress import render_hydration_from_context

        hydration = render_hydration_from_context(context_json)

    return {
        "status": "success",
        "project_repo": project_repo,
        "event_count": len(chronological),
        "events": chronological,
        "decision_count": len(decisions),
        "file_edit_count": len(edits),
        "context_json": context_json,
        "transcript_md": transcript_md,
        "hydration_prompt": hydration,
    }


def save_memory(
    *,
    developer_id: str,
    agent_tool: str,
    project_repo: str,
    summary: str,
    memory_type: str = "session_summary",
    decisions: list[str] | None = None,
    files_touched: list[str] | None = None,
    rejected_approaches: list[str] | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """End-of-session save — writes session_end log events (primary) + legacy summary row."""
    sid = session_id or str(uuid.uuid4())
    payload = {
        "decisions": decisions or [],
        "files_touched": files_touched or [],
        "rejected_approaches": rejected_approaches or [],
        "memory_type": memory_type,
    }

    log_result = append_codebase_log(
        developer_id=developer_id,
        agent_tool=agent_tool,
        project_repo=project_repo,
        event_type="session_end",
        summary=summary,
        session_id=sid,
        payload=payload,
    )
    if log_result.get("status") != "success":
        return log_result

    for decision in decisions or []:
        append_codebase_log(
            developer_id=developer_id,
            agent_tool=agent_tool,
            project_repo=project_repo,
            event_type="decision",
            summary=decision,
            session_id=sid,
            payload={"source": "session_end_batch"},
            parent_event_id=log_result.get("event_id"),
        )

    created = _now_iso()
    compressed_result = save_compressed_context(
        developer_id=developer_id,
        agent_tool=agent_tool,
        project_repo=project_repo,
        session_id=sid,
    )
    context_json = compressed_result.get("context_json") or {}
    transcript_md = compressed_result.get("transcript_md") or ""

    legacy_row = {
        "session_id": sid,
        "developer_id": developer_id,
        "agent_tool": agent_tool,
        "project_repo": project_repo,
        "memory_type": memory_type,
        "summary": summary,
        "decisions_json": json.dumps(decisions or []),
        "files_touched": json.dumps(files_touched or []),
        "rejected_approaches": json.dumps(rejected_approaches or []),
        "context_json": json.dumps(context_json, default=str),
        "transcript_md": transcript_md[:50000],
        "created_at": created,
    }
    client = _bq_client()
    client.insert_rows_json(MEMORY_FULL_TABLE, [legacy_row])
    _append_sheet_row(legacy_row, MEMORY_COLUMNS, MEMORY_SHEET_RANGE)

    return {
        "status": "success",
        "session_id": sid,
        "event_id": log_result.get("event_id"),
        "compressed_event_id": compressed_result.get("event_id"),
        "context_json": context_json,
        "transcript_md": transcript_md,
        "hydration_prompt": compressed_result.get("hydration_prompt"),
        "table": CODEBASE_LOGS_FULL_TABLE,
        "created_at": created,
        "message": (
            "Session logged + compressed JSON + transcript saved. Next agent: call load_context."
        ),
    }


def log_decision(
    *,
    developer_id: str,
    agent_tool: str,
    project_repo: str,
    decision: str,
    context: str = "",
    session_id: str | None = None,
    file_path: str | None = None,
) -> dict[str, Any]:
    """Log a single engineering decision as an append-only event."""
    summary = decision if not context else f"{decision} — {context}"
    return append_codebase_log(
        developer_id=developer_id,
        agent_tool=agent_tool,
        project_repo=project_repo,
        event_type="decision",
        summary=summary,
        session_id=session_id,
        file_path=file_path,
        payload={"decision": decision, "context": context},
    )


def load_team_context(project_repo: str, limit: int = 50) -> dict[str, Any]:
    """Hydrate new agent — prefers codebase_logs event replay."""
    return load_context_from_logs(project_repo=project_repo, limit=limit)


def load_session_history(
    developer_id: str,
    project_repo: str | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    """Load recent log events for one developer."""
    limit = max(1, min(limit, 200))
    where = "developer_id = @developer_id"
    params: list[bigquery.ScalarQueryParameter] = [
        bigquery.ScalarQueryParameter("developer_id", "STRING", developer_id),
    ]
    if project_repo:
        where += " AND project_repo = @project_repo"
        params.append(
            bigquery.ScalarQueryParameter("project_repo", "STRING", project_repo)
        )
    sql = f"""
        SELECT *
        FROM `{CODEBASE_LOGS_FULL_TABLE}`
        WHERE {where}
        ORDER BY created_at DESC
        LIMIT {limit}
    """
    client = _bq_client()
    try:
        result = client.query(
            sql, job_config=bigquery.QueryJobConfig(query_parameters=params)
        ).result()
        events = _normalize_events([dict(r.items()) for r in result])
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "message": str(exc)}

    return {
        "status": "success",
        "developer_id": developer_id,
        "project_repo": project_repo,
        "event_count": len(events),
        "events": list(reversed(events)),
    }


def get_memory_catalog() -> dict[str, Any]:
    """Summarize projects with codebase log activity."""
    sql = f"""
        SELECT
          project_repo,
          COUNT(*) AS event_count,
          COUNT(DISTINCT developer_id) AS developers,
          COUNT(DISTINCT session_id) AS sessions,
          MAX(created_at) AS last_updated
        FROM `{CODEBASE_LOGS_FULL_TABLE}`
        GROUP BY project_repo
        ORDER BY last_updated DESC
    """
    client = _bq_client()
    try:
        rows = client.query(sql).result()
        projects = []
        for row in rows:
            rec = dict(row.items())
            if hasattr(rec.get("last_updated"), "isoformat"):
                rec["last_updated"] = rec["last_updated"].isoformat()
            projects.append(rec)
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "message": str(exc)}

    return {
        "status": "success",
        "primary_table": CODEBASE_LOGS_FULL_TABLE,
        "project_count": len(projects),
        "projects": projects,
    }
