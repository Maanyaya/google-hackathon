"""Action Agent tools — push insights to GCS, Google Sheets, and webhooks."""

from __future__ import annotations

import csv
import io
import json
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any

import google.auth
import google.auth.transport.requests
from google.adk.tools import ToolContext
from google.cloud import bigquery, storage

from app import config


def _guardian_block(tool_context: ToolContext) -> dict[str, Any] | None:
    if not tool_context.state.get("guardian_approved"):
        return {
            "status": "blocked",
            "message": (
                "Guardian has not approved this action. Ask the user to confirm, "
                "then call guardian_approve_write before retrying."
            ),
        }
    return None


def _consume_guardian_approval(tool_context: ToolContext) -> None:
    tool_context.state["guardian_approved"] = False


def get_action_catalog() -> dict[str, Any]:
    """Return configured action targets the Action Agent can push insights to."""
    return {
        "status": "success",
        "targets": [
            {
                "id": "gcs_report",
                "tool": "export_report_to_gcs",
                "description": "Export JSON/CSV insight report to Cloud Storage (always available)",
                "bucket": config.ACTION_GCS_BUCKET,
                "prefix": "action-reports/",
            },
            {
                "id": "google_sheets",
                "tool": "push_report_to_google_sheets",
                "description": "Append insight rows to a Google Sheet tab (reverse path)",
                "sheet_id": config.ACTION_REPORT_SHEET_ID or "(set ACTION_REPORT_SHEET_ID)",
                "range": config.ACTION_SHEET_RANGE,
            },
            {
                "id": "webhook",
                "tool": "send_webhook_notification",
                "description": "POST notification to Slack/Teams/custom webhook",
                "url_configured": bool(config.ACTION_WEBHOOK_URL),
            },
        ],
        "workflow": (
            "1) prepare_insight_report (SQL → structured rows), "
            "2) Guardian approval, 3) export/push/notify"
        ),
    }


def prepare_insight_report(title: str, sql: str) -> dict[str, Any]:
    """Run a read-only BigQuery query and package results as an insight report.

    Use this before pushing to GCS, Sheets, or a webhook. SELECT only.

    Args:
        title: Report title (e.g. 'MoDeX event summary by developer').
        sql: BigQuery SELECT statement.
    """
    cleaned = sql.strip().rstrip(";")
    if not re.match(r"(?is)^\s*select\b", cleaned):
        return {"status": "error", "message": "Only SELECT queries are allowed."}
    if re.search(r"(?is)\b(insert|update|delete|drop|create|alter|merge|truncate)\b", cleaned):
        return {"status": "error", "message": "Mutating SQL is not allowed."}

    client = bigquery.Client(project=config.GOOGLE_CLOUD_PROJECT)
    try:
        rows = client.query(cleaned).result()
        records = [dict(row.items()) for row in rows]
        for rec in records:
            for k, v in rec.items():
                if isinstance(v, datetime):
                    rec[k] = v.isoformat()
        headers = list(records[0].keys()) if records else []
        return {
            "status": "success",
            "title": title,
            "sql": cleaned,
            "row_count": len(records),
            "headers": headers,
            "rows": records[:100],
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_table": config.MODEX_CODEBASE_LOGS_FULL_TABLE,
        }
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "message": str(exc)}


def export_report_to_gcs(
    title: str,
    summary: str,
    report_json: str,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """Export an insight report to Cloud Storage as JSON + CSV.

    Requires Guardian approval. Use after prepare_insight_report.

    Args:
        title: Report title for the filename.
        summary: One-paragraph executive summary.
        report_json: JSON string from prepare_insight_report (must include headers + rows).
    """
    blocked = _guardian_block(tool_context)
    if blocked:
        return blocked

    try:
        report = json.loads(report_json)
    except json.JSONDecodeError as exc:
        return {"status": "error", "message": f"Invalid report_json: {exc}"}

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_title = re.sub(r"[^a-zA-Z0-9_-]", "_", title)[:40]
    prefix = f"action-reports/{ts}_{safe_title}"

    payload = {
        "title": title,
        "summary": summary,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "report": report,
        "platform": "Agentic Data Platform",
    }

    client = storage.Client(project=config.GOOGLE_CLOUD_PROJECT)
    bucket = client.bucket(config.ACTION_GCS_BUCKET)
    if not bucket.exists():
        bucket = client.create_bucket(
            config.ACTION_GCS_BUCKET,
            location=config.GOOGLE_CLOUD_LOCATION if config.GOOGLE_CLOUD_LOCATION != "global" else "asia-south1",
        )

    json_blob = bucket.blob(f"{prefix}.json")
    json_blob.upload_from_string(
        json.dumps(payload, indent=2, default=str),
        content_type="application/json",
    )

    headers = report.get("headers") or []
    rows = report.get("rows") or []
    csv_buf = io.StringIO()
    if headers and rows:
        writer = csv.DictWriter(csv_buf, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    csv_blob = bucket.blob(f"{prefix}.csv")
    csv_blob.upload_from_string(csv_buf.getvalue(), content_type="text/csv")

    _consume_guardian_approval(tool_context)
    return {
        "status": "success",
        "action": "export_report_to_gcs",
        "bucket": config.ACTION_GCS_BUCKET,
        "json_uri": f"gs://{config.ACTION_GCS_BUCKET}/{prefix}.json",
        "csv_uri": f"gs://{config.ACTION_GCS_BUCKET}/{prefix}.csv",
        "row_count": report.get("row_count", len(rows)),
    }


def push_report_to_google_sheets(
    report_json: str,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """Append insight report rows to a Google Sheet (reverse-ETL style write-back).

    Requires Guardian approval and ACTION_REPORT_SHEET_ID configured.
    Share the sheet with the Cloud Run service account as Editor.

    Args:
        report_json: JSON string from prepare_insight_report (headers + rows).
    """
    blocked = _guardian_block(tool_context)
    if blocked:
        return blocked

    if not config.ACTION_REPORT_SHEET_ID:
        return {
            "status": "error",
            "message": (
                "ACTION_REPORT_SHEET_ID not configured. Set env var to a Google Sheet ID "
                "and share it with the runtime service account."
            ),
        }

    try:
        report = json.loads(report_json)
    except json.JSONDecodeError as exc:
        return {"status": "error", "message": f"Invalid report_json: {exc}"}

    headers = report.get("headers") or []
    rows = report.get("rows") or []
    if not headers or not rows:
        return {"status": "error", "message": "Report has no headers or rows to push."}

    sheet_rows = [headers]
    for row in rows:
        sheet_rows.append([str(row.get(h, "")) for h in headers])

    creds, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    creds.refresh(google.auth.transport.requests.Request())

    url = (
        f"https://sheets.googleapis.com/v4/spreadsheets/"
        f"{config.ACTION_REPORT_SHEET_ID}/values/"
        f"{config.ACTION_SHEET_RANGE}:append?valueInputOption=USER_ENTERED"
    )
    body = json.dumps({"values": sheet_rows}).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {creds.token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode()[:500]
        return {"status": "error", "message": f"Sheets API error {exc.code}: {detail}"}

    _consume_guardian_approval(tool_context)
    return {
        "status": "success",
        "action": "push_report_to_google_sheets",
        "sheet_id": config.ACTION_REPORT_SHEET_ID,
        "range": config.ACTION_SHEET_RANGE,
        "rows_appended": len(rows),
        "updated_range": result.get("updates", {}).get("updatedRange"),
    }


def send_webhook_notification(
    message: str,
    report_json: str,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """POST an insight notification to a configured webhook (Slack-compatible).

    Requires Guardian approval and ACTION_WEBHOOK_URL configured.

    Args:
        message: Human-readable notification text.
        report_json: JSON string from prepare_insight_report (included in payload).
    """
    blocked = _guardian_block(tool_context)
    if blocked:
        return blocked

    if not config.ACTION_WEBHOOK_URL:
        return {
            "status": "error",
            "message": "ACTION_WEBHOOK_URL not configured.",
        }

    try:
        report = json.loads(report_json)
    except json.JSONDecodeError:
        report = {"raw": report_json}

    payload = {
        "text": message,
        "platform": "Agentic Data Platform",
        "report_title": report.get("title", "Insight Report"),
        "row_count": report.get("row_count"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary_rows": (report.get("rows") or [])[:5],
    }
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        config.ACTION_WEBHOOK_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            status = resp.status
    except urllib.error.HTTPError as exc:
        return {"status": "error", "message": f"Webhook failed: {exc.code} {exc.reason}"}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "message": str(exc)}

    _consume_guardian_approval(tool_context)
    return {
        "status": "success",
        "action": "send_webhook_notification",
        "http_status": status,
        "message_sent": message[:200],
    }
