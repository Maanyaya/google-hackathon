"""Face 2 read path for MoDeX codebase logs (deployed inside app/ bundle)."""

from __future__ import annotations

import json
from typing import Any

from google.cloud import bigquery

from app import config

VALID_EVENT_TYPES = frozenset({
    "session_start",
    "user_prompt",
    "tool_call",
    "file_edit",
    "decision",
    "error",
    "session_end",
})


def _normalize_events(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        rec = dict(row)
        if isinstance(rec.get("payload_json"), str) and rec["payload_json"]:
            try:
                rec["payload_json"] = json.loads(rec["payload_json"])
            except json.JSONDecodeError:
                pass
        if hasattr(rec.get("created_at"), "isoformat"):
            rec["created_at"] = rec["created_at"].isoformat()
        out.append(rec)
    return out


def get_memory_catalog() -> dict[str, Any]:
    sql = f"""
        SELECT
          project_repo,
          COUNT(*) AS event_count,
          COUNT(DISTINCT developer_id) AS developers,
          COUNT(DISTINCT session_id) AS sessions,
          MAX(created_at) AS last_updated
        FROM `{config.MODEX_CODEBASE_LOGS_FULL_TABLE}`
        GROUP BY project_repo
        ORDER BY last_updated DESC
    """
    client = bigquery.Client(project=config.GOOGLE_CLOUD_PROJECT)
    try:
        projects = []
        for row in client.query(sql).result():
            rec = dict(row.items())
            if hasattr(rec.get("last_updated"), "isoformat"):
                rec["last_updated"] = rec["last_updated"].isoformat()
            projects.append(rec)
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "message": str(exc)}

    return {
        "status": "success",
        "primary_table": config.MODEX_CODEBASE_LOGS_FULL_TABLE,
        "project_count": len(projects),
        "projects": projects,
    }


def load_context_from_logs(
    project_repo: str,
    limit: int = 50,
    event_types: list[str] | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    limit = max(1, min(limit, 200))
    where = "project_repo = @project_repo"
    params: list[bigquery.ScalarQueryParameter] = [
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
        FROM `{config.MODEX_CODEBASE_LOGS_FULL_TABLE}`
        WHERE {where}
        ORDER BY created_at DESC
        LIMIT {limit}
    """
    client = bigquery.Client(project=config.GOOGLE_CLOUD_PROJECT)
    try:
        result = client.query(
            sql, job_config=bigquery.QueryJobConfig(query_parameters=params)
        ).result()
        events = _normalize_events([dict(r.items()) for r in result])
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "message": str(exc)}

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

    return {
        "status": "success",
        "project_repo": project_repo,
        "event_count": len(chronological),
        "events": chronological,
        "decision_count": len(decisions),
        "file_edit_count": len(edits),
        "hydration_prompt": "\n".join(hydration_parts),
    }
