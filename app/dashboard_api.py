"""Dashboard API — MoDeX Command Center (pipeline health, memory, agent topology)."""

from __future__ import annotations

import datetime
import re
from typing import Any

from fastapi import APIRouter, HTTPException
from google.cloud import bigquery, storage
from pydantic import BaseModel

from app import config
from app.fivetran_mcp import call_fivetran_tool
from app.tools import get_codebase_log_timeline

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

CLOUD_RUN_URL = (
    "https://agentic-data-platform-979112189932.asia-south1.run.app"
)


class QueryRequest(BaseModel):
    sql: str


AGENT_TOPOLOGY = [
    {
        "id": "orchestrator_agent",
        "label": "Mission Control",
        "description": "MoDeX hub — plans missions, delegates to specialist agents",
        "icon": "brain",
        "color": "#6366f1",
        "tools": [],
        "delegates_to": [
            "ingestion_agent",
            "knowledge_agent",
            "lineage_agent",
            "transformation_agent",
            "action_agent",
            "guardian_agent",
        ],
    },
    {
        "id": "ingestion_agent",
        "label": "Data Source Connector",
        "description": "Syncs engineering data (GitHub, Sheets, Jira) via Fivetran MCP",
        "icon": "database",
        "color": "#06b6d4",
        "tools": [
            "fivetran_get_account_info",
            "fivetran_list_groups",
            "fivetran_list_destinations",
            "fivetran_list_connections",
            "fivetran_get_connection_details",
            "fivetran_sync_connection",
        ],
        "mcp": "Fivetran MCP",
    },
    {
        "id": "knowledge_agent",
        "label": "Shared Memory Engine",
        "description": "Queries team decisions & reasoning via BigQuery + RAG",
        "icon": "search",
        "color": "#10b981",
        "tools": [
            "get_data_catalog",
            "get_agent_memory_catalog",
            "get_agent_memory_for_project",
            "get_codebase_log_timeline",
            "get_modex_fivetran_logs",
            "query_bigquery",
            "search_knowledge_base",
        ],
        "mcp": "BigQuery + Vertex AI RAG + Face 1 agent_memory",
    },
    {
        "id": "lineage_agent",
        "label": "Decision Provenance",
        "description": "Traces data freshness, lineage, and change history",
        "icon": "git-branch",
        "color": "#f59e0b",
        "tools": [
            "get_pipeline_metadata_catalog",
            "query_bigquery",
            "fivetran_list_connections",
        ],
        "mcp": "Platform Connector metadata",
    },
    {
        "id": "transformation_agent",
        "label": "Knowledge Structurer",
        "description": "Transforms raw data into structured decision records via dbt",
        "icon": "layers",
        "color": "#8b5cf6",
        "tools": [
            "get_transformation_catalog",
            "fivetran_list_transformation_projects",
            "fivetran_get_transformation_project_details",
            "fivetran_list_transformations",
            "fivetran_get_transformation_details",
            "fivetran_run_transformation",
            "query_bigquery",
        ],
        "mcp": "Fivetran Transformations",
    },
    {
        "id": "action_agent",
        "label": "Team Broadcaster",
        "description": "Pushes reports & alerts to GCS, Sheets, or webhooks",
        "icon": "send",
        "color": "#ec4899",
        "tools": [
            "get_action_catalog",
            "prepare_insight_report",
            "export_report_to_gcs",
            "push_report_to_google_sheets",
            "send_webhook_notification",
        ],
        "mcp": "GCS + Sheets API + Webhooks",
    },
    {
        "id": "guardian_agent",
        "label": "Access Governor",
        "description": "Human-in-the-loop governance for all write operations",
        "icon": "shield",
        "color": "#ef4444",
        "tools": ["guardian_approve_write", "guardian_deny_write"],
    },
]


def _run_bq(sql: str) -> list[dict[str, Any]]:
    client = bigquery.Client(project=config.GOOGLE_CLOUD_PROJECT)
    rows = client.query(sql).result()
    out: list[dict[str, Any]] = []
    for row in rows:
        d = dict(row.items())
        for k, v in d.items():
            if isinstance(v, (datetime.datetime, datetime.date)):
                d[k] = v.isoformat()
        out.append(d)
    return out


@router.get("/topology")
async def get_topology() -> dict[str, Any]:
    return {"agents": AGENT_TOPOLOGY}


@router.get("/overview")
async def get_overview() -> dict[str, Any]:
    return {
        "product_name": "MoDeX — Memory of Codex",
        "tagline": "Shared reasoning memory for AI coding teams",
        "project": config.GOOGLE_CLOUD_PROJECT,
        "region": "asia-south1",
        "agent_count": 7,
        "agents": [a["label"] for a in AGENT_TOPOLOGY],
        "fivetran_group": config.FIVETRAN_BQ_GROUP_ID,
        "datasets": [
            config.MODEX_MEMORY_DATASET,
            config.MODEX_FIVETRAN_BQ_DATASET,
            config.BQ_METADATA_DATASET,
            "google_sheets",
            "analytics",
        ],
        "face1_mcp": "modex_mcp (append_codebase_log, load_context_from_logs)",
        "agent_memory_table": config.MODEX_CODEBASE_LOGS_FULL_TABLE,
        "fivetran_modex_table": config.MODEX_FIVETRAN_FULL_TABLE,
        "fivetran_modex_connection": config.FIVETRAN_MODEX_LOGS_CONNECTION_ID,
        "codebase_logs_primary": True,
        "rag_corpus": config.RAG_CORPUS,
        "rag_location": config.RAG_LOCATION,
        "dbt_project": config.FIVETRAN_TRANSFORM_PROJECT_ID,
        "cloud_run_url": CLOUD_RUN_URL,
    }


@router.get("/pipelines")
async def get_pipelines() -> dict[str, Any]:
    try:
        result = await call_fivetran_tool(
            "list_connections",
            {"group_id": config.FIVETRAN_BQ_GROUP_ID},
        )
        if result.get("status") == "error":
            return {"status": "error", "error": result.get("message"), "pipelines": []}

        raw = result.get("data", {})
        items = []
        if isinstance(raw, dict):
            for conn in raw.get("data", {}).get("items", []):
                items.append({
                    "id": conn.get("id"),
                    "name": conn.get("schema"),
                    "service": conn.get("service"),
                    "status": conn.get("status", {}).get("sync_state", "unknown"),
                    "paused": conn.get("paused", False),
                    "succeeded_at": conn.get("succeeded_at"),
                    "failed_at": conn.get("failed_at"),
                    "sync_frequency": conn.get("sync_frequency"),
                })
        return {"status": "success", "pipelines": items}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "error": str(exc), "pipelines": []}


@router.get("/pipeline/{connection_id}")
async def get_pipeline_detail(connection_id: str) -> dict[str, Any]:
    try:
        return await call_fivetran_tool(
            "get_connection_details",
            {"connection_id": connection_id},
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(500, str(exc)) from exc


@router.get("/freshness")
async def get_data_freshness() -> dict[str, Any]:
    try:
        fivetran_logs = _run_bq(
            f"SELECT MAX(_fivetran_synced) AS last_synced, COUNT(1) AS row_count "
            f"FROM `{config.MODEX_FIVETRAN_FULL_TABLE}`"
        )
        face1_logs = _run_bq(
            f"SELECT MAX(created_at) AS last_event, COUNT(1) AS event_count "
            f"FROM `{config.MODEX_CODEBASE_LOGS_FULL_TABLE}`"
        )
        metadata_freshness = _run_bq(
            f"SELECT MAX(time_stamp) AS last_event, COUNT(1) AS event_count "
            f"FROM `{config.BQ_METADATA_PREFIX}.log`"
        )
        analytics_tables = []
        for tbl in ["students_by_activity", "students_by_class_level"]:
            try:
                rows = _run_bq(
                    f"SELECT COUNT(1) AS row_count FROM "
                    f"`{config.GOOGLE_CLOUD_PROJECT}.analytics.{tbl}`"
                )
                analytics_tables.append({"table": tbl, "row_count": rows[0]["row_count"]})
            except Exception:  # noqa: BLE001
                analytics_tables.append({"table": tbl, "row_count": None, "error": "not found"})

        return {
            "status": "success",
            "main_table": {
                "name": config.MODEX_FIVETRAN_FULL_TABLE,
                "last_synced": fivetran_logs[0]["last_synced"] if fivetran_logs else None,
                "row_count": fivetran_logs[0]["row_count"] if fivetran_logs else 0,
            },
            "face1_memory": {
                "name": config.MODEX_CODEBASE_LOGS_FULL_TABLE,
                "last_event": face1_logs[0]["last_event"] if face1_logs else None,
                "event_count": face1_logs[0]["event_count"] if face1_logs else 0,
            },
            "metadata": {
                "dataset": config.BQ_METADATA_DATASET,
                "last_event": metadata_freshness[0]["last_event"] if metadata_freshness else None,
                "event_count": metadata_freshness[0]["event_count"] if metadata_freshness else 0,
            },
            "analytics_tables": analytics_tables,
        }
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "error": str(exc)}


@router.get("/memory")
async def get_memory_timeline() -> dict[str, Any]:
    result = get_codebase_log_timeline(
        project_repo="github.com/demo/api-service",
        limit=30,
    )
    if result.get("status") != "success":
        return result
    memories = []
    for ev in result.get("events", []):
        memories.append({
            "event_id": ev.get("event_id", ""),
            "session_id": ev.get("session_id", ""),
            "developer_id": ev.get("developer_id", ""),
            "agent_tool": ev.get("agent_tool", ""),
            "project_repo": ev.get("project_repo", ""),
            "event_type": ev.get("event_type", ""),
            "file_path": ev.get("file_path") or "",
            "summary": ev.get("summary", ""),
            "created_at": ev.get("created_at", ""),
        })
    return {
        "status": "success",
        "table": config.MODEX_CODEBASE_LOGS_FULL_TABLE,
        "memories": memories,
    }


@router.get("/charts/activities")
async def chart_event_types() -> dict[str, Any]:
    try:
        rows = _run_bq(
            f"SELECT event_type AS label, COUNT(1) AS value "
            f"FROM `{config.MODEX_CODEBASE_LOGS_FULL_TABLE}` "
            f"GROUP BY event_type ORDER BY value DESC"
        )
        return {
            "status": "success",
            "chart_type": "bar",
            "title": "Codebase Events by Type",
            "data": rows,
        }
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "error": str(exc)}


@router.get("/charts/class-levels")
async def chart_agent_tools() -> dict[str, Any]:
    try:
        rows = _run_bq(
            f"SELECT agent_tool AS label, COUNT(1) AS value "
            f"FROM `{config.MODEX_CODEBASE_LOGS_FULL_TABLE}` "
            f"GROUP BY agent_tool ORDER BY value DESC"
        )
        return {
            "status": "success",
            "chart_type": "pie",
            "title": "Events by AI Agent Tool",
            "data": rows,
        }
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "error": str(exc)}


@router.get("/charts/majors")
async def chart_developers() -> dict[str, Any]:
    try:
        rows = _run_bq(
            f"SELECT developer_id AS label, COUNT(1) AS value "
            f"FROM `{config.MODEX_CODEBASE_LOGS_FULL_TABLE}` "
            f"GROUP BY developer_id ORDER BY value DESC"
        )
        return {
            "status": "success",
            "chart_type": "bar",
            "title": "Events by Developer",
            "data": rows,
        }
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "error": str(exc)}


@router.get("/charts/states")
async def chart_decisions() -> dict[str, Any]:
    try:
        rows = _run_bq(
            f"SELECT SUBSTR(summary, 1, 40) AS label, COUNT(1) AS value "
            f"FROM `{config.MODEX_CODEBASE_LOGS_FULL_TABLE}` "
            f"WHERE event_type = 'decision' "
            f"GROUP BY summary ORDER BY value DESC LIMIT 8"
        )
        return {
            "status": "success",
            "chart_type": "bar",
            "title": "Engineering Decisions Logged",
            "data": rows,
        }
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "error": str(exc)}


@router.get("/timeline")
async def pipeline_timeline() -> dict[str, Any]:
    try:
        rows = _run_bq(
            f"SELECT time_stamp, connection_id, event, message_event, "
            f"SUBSTR(message_data, 1, 200) AS message_data "
            f"FROM `{config.BQ_METADATA_PREFIX}.log` "
            f"ORDER BY time_stamp DESC LIMIT 30"
        )
        return {"status": "success", "events": rows}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "error": str(exc)}


@router.get("/lineage")
async def get_lineage() -> dict[str, Any]:
    try:
        rows = _run_bq(f"""
            SELECT
                st.name AS source_table,
                dt.name AS destination_table,
                tl.created_at
            FROM `{config.BQ_METADATA_PREFIX}.table_lineage` tl
            LEFT JOIN `{config.BQ_METADATA_PREFIX}.source_table` st
                ON tl.source_table_id = st.id
            LEFT JOIN `{config.BQ_METADATA_PREFIX}.destination_table` dt
                ON tl.destination_table_id = dt.id
            ORDER BY tl.created_at DESC
            LIMIT 50
        """)
        return {"status": "success", "lineage": rows}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "error": str(exc)}


@router.get("/transformations")
async def get_transformations() -> dict[str, Any]:
    try:
        return await call_fivetran_tool("list_transformations", {})
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "error": str(exc)}


@router.get("/actions/recent")
async def get_recent_actions() -> dict[str, Any]:
    try:
        client = storage.Client(project=config.GOOGLE_CLOUD_PROJECT)
        bucket = client.bucket(config.ACTION_GCS_BUCKET)
        reports = []
        for blob in bucket.list_blobs(prefix="action-reports/", max_results=20):
            reports.append({
                "name": blob.name.split("/")[-1],
                "uri": f"gs://{config.ACTION_GCS_BUCKET}/{blob.name}",
                "created": blob.time_created.isoformat() if blob.time_created else None,
                "size_bytes": blob.size,
            })
        reports.sort(key=lambda r: r.get("created") or "", reverse=True)
        return {"status": "success", "reports": reports[:10]}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "error": str(exc), "reports": []}


@router.post("/query")
async def run_query(req: QueryRequest) -> dict[str, Any]:
    cleaned = req.sql.strip().rstrip(";")
    if not re.match(r"(?is)^\s*select\b", cleaned):
        raise HTTPException(400, "Only SELECT queries are allowed.")
    if re.search(
        r"(?is)\b(insert|update|delete|drop|create|alter|merge|truncate)\b",
        cleaned,
    ):
        raise HTTPException(400, "Mutating SQL is not allowed.")
    try:
        rows = _run_bq(cleaned)
        return {"status": "success", "row_count": len(rows), "rows": rows[:100]}
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(500, str(exc)) from exc
