"""Tools for specialist agents — Fivetran MCP, BigQuery, Guardian."""

from __future__ import annotations

import json
import re
from typing import Any

from google.adk.tools import ToolContext
from google.cloud import bigquery

from app import config
from app.fivetran_mcp import call_fivetran_tool


_KNOWN_DATASETS = [
    (config.MODEX_MEMORY_DATASET, "Face 1 session memory from Google Antigravity coding agents"),
    (config.MODEX_FIVETRAN_BQ_DATASET, "MoDeX logs synced via Fivetran connector stowed_register"),
    (config.BQ_METADATA_DATASET, "Fivetran Platform Connector pipeline metadata"),
    ("analytics", "dbt analytics models (Fivetran Transformations for dbt Core)"),
]


def get_data_catalog() -> dict[str, Any]:
    """Return landed BigQuery tables across connector, analytics, and metadata datasets."""
    client = bigquery.Client(project=config.GOOGLE_CLOUD_PROJECT)
    tables: list[dict[str, Any]] = []
    errors: list[str] = []

    for dataset_id, description in _KNOWN_DATASETS:
        query = f"""
        SELECT table_name
        FROM `{config.GOOGLE_CLOUD_PROJECT}.{dataset_id}.INFORMATION_SCHEMA.TABLES`
        WHERE table_type = 'BASE TABLE'
        ORDER BY table_name
        LIMIT 50
        """
        try:
            rows = list(client.query(query).result())
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{dataset_id}: {exc}")
            continue
        for row in rows:
            full_name = f"{config.GOOGLE_CLOUD_PROJECT}.{dataset_id}.{row.table_name}"
            entry: dict[str, Any] = {
                "full_name": full_name,
                "dataset": dataset_id,
                "description": description,
            }
            tables.append(entry)

    return {
        "status": "success",
        "project": config.GOOGLE_CLOUD_PROJECT,
        "table_count": len(tables),
        "tables": tables,
        "primary_table": config.MODEX_CODEBASE_LOGS_FULL_TABLE,
        "fivetran_connections": {
            "bigquery_group_id": config.FIVETRAN_BQ_GROUP_ID,
        },
        "errors": errors,
    }


async def fivetran_get_account_info() -> dict[str, Any]:
    """Get Fivetran account info via MCP (groups, destinations overview)."""
    return await call_fivetran_tool("get_account_info", {})


async def fivetran_list_groups() -> dict[str, Any]:
    """List all Fivetran groups (each group maps to one destination)."""
    return await call_fivetran_tool("list_groups", {})


async def fivetran_list_destinations() -> dict[str, Any]:
    """List Fivetran destinations (e.g. BigQuery warehouse for group solve_unhurt)."""
    return await call_fivetran_tool("list_destinations", {})


async def fivetran_list_connections(group_id: str | None = None) -> dict[str, Any]:
    """List Fivetran connections via the official Fivetran MCP server.

    Args:
        group_id: Optional Fivetran group/destination id to filter (e.g. solve_unhurt).
    """
    extra: dict[str, Any] = {}
    if group_id:
        extra["group_id"] = group_id
    return await call_fivetran_tool("list_connections", extra)


async def fivetran_get_connection_details(connection_id: str) -> dict[str, Any]:
    """Get sync status and health for one Fivetran connection via MCP.

    Args:
        connection_id: Fivetran connection id (e.g. stowed_register for MoDeX logs).
    """
    return await call_fivetran_tool(
        "get_connection_details",
        {"connection_id": connection_id},
    )


async def fivetran_sync_connection(
    connection_id: str,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """Trigger a Fivetran sync via MCP. Requires Guardian approval in session state.

    Args:
        connection_id: Fivetran connection id to sync.
    """
    if not tool_context.state.get("guardian_approved"):
        return {
            "status": "blocked",
            "message": (
                "Guardian has not approved this write. Ask the user to confirm, "
                "then call guardian_approve_write before retrying."
            ),
        }
    result = await call_fivetran_tool(
        "sync_connection",
        {"connection_id": connection_id, "request_body": json.dumps({"force": True})},
        allow_writes=True,
    )
    tool_context.state["guardian_approved"] = False
    return result


async def fivetran_list_transformation_projects() -> dict[str, Any]:
    """List Fivetran dbt Core transformation projects."""
    return await call_fivetran_tool("list_transformation_projects", {})


async def fivetran_get_transformation_project_details(
    project_id: str,
) -> dict[str, Any]:
    """Get details for one Fivetran dbt transformation project.

    Args:
        project_id: Transformation project id (e.g. gracious_electable).
    """
    return await call_fivetran_tool(
        "get_transformation_project_details",
        {"project_id": project_id},
    )


async def fivetran_list_transformations() -> dict[str, Any]:
    """List Fivetran dbt Core transformations (jobs) via MCP.

    Returns transformation id, name, status, schedule, and output model names.
    """
    return await call_fivetran_tool("list_transformations", {})


async def fivetran_get_transformation_details(transformation_id: str) -> dict[str, Any]:
    """Get details/run status for one Fivetran transformation via MCP.

    Args:
        transformation_id: Fivetran transformation id (e.g. buy_tender).
    """
    return await call_fivetran_tool(
        "get_transformation_details",
        {"transformation_id": transformation_id},
    )


async def fivetran_run_transformation(
    transformation_id: str,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """Trigger a Fivetran dbt Core transformation run. Requires Guardian approval.

    This runs dbt models against BigQuery to (re)build analytics-ready tables.

    Args:
        transformation_id: Fivetran transformation id to run (e.g. buy_tender).
    """
    if not tool_context.state.get("guardian_approved"):
        return {
            "status": "blocked",
            "message": (
                "Guardian has not approved this transformation run. Ask the user to "
                "confirm, then call guardian_approve_write before retrying."
            ),
        }
    result = await call_fivetran_tool(
        "run_transformation",
        {"transformation_id": transformation_id},
        allow_writes=True,
    )
    tool_context.state["guardian_approved"] = False
    return result


def get_transformation_catalog() -> dict[str, Any]:
    """Return the configured dbt transformation project and analytics output tables.

    Use this to know which transformation to run and where its output lands.
    """
    return {
        "status": "success",
        "dbt_project": {
            "project_id": config.FIVETRAN_TRANSFORM_PROJECT_ID,
            "transformation_id": config.FIVETRAN_TRANSFORMATION_ID,
            "git_repo": "github.com/gaganTakIITD/agentic-data-platform-dbt",
            "runtime": "Fivetran Transformations for dbt Core",
        },
        "output_tables": [
            {
                "full_name": f"{config.GOOGLE_CLOUD_PROJECT}.analytics.events_by_type",
                "description": "Codebase log event counts by type (decision, file_edit, error, etc.)",
            },
            {
                "full_name": f"{config.GOOGLE_CLOUD_PROJECT}.analytics.events_by_developer",
                "description": "Event distribution across developers / agents",
            },
        ],
        "source_table": config.MODEX_CODEBASE_LOGS_FULL_TABLE,
        "tip": "After running, verify results with query_bigquery on the analytics tables.",
    }


def guardian_approve_write(
    action_description: str,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """Record user-approved permission for one Fivetran write (sync) operation.

    Args:
        action_description: What write the user approved (for audit trail).
    """
    tool_context.state["guardian_approved"] = True
    tool_context.state["guardian_last_approval"] = action_description
    return {
        "status": "approved",
        "message": f"Write approved for: {action_description}. One sync may proceed.",
    }


def guardian_deny_write(tool_context: ToolContext) -> dict[str, Any]:
    """Revoke write permission for Fivetran pipeline operations."""
    tool_context.state["guardian_approved"] = False
    tool_context.state.pop("guardian_last_approval", None)
    return {"status": "denied", "message": "Write operations blocked."}


def search_knowledge_base(query: str) -> dict[str, Any]:
    """Semantic (vector) search over the platform knowledge base via Vertex AI RAG Engine.

    Use this for conceptual questions: what a column/term means, how the platform or
    Fivetran pipeline works, glossary definitions. Returns the most relevant passages.
    For live counts/aggregations, use query_bigquery instead.
    """
    try:
        import vertexai
        from vertexai import rag
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "error": f"RAG SDK unavailable: {exc}"}

    if not config.RAG_CORPUS:
        return {"status": "error", "error": "RAG_CORPUS not configured."}

    try:
        vertexai.init(project=config.GOOGLE_CLOUD_PROJECT, location=config.RAG_LOCATION)
        resp = rag.retrieval_query(
            rag_resources=[rag.RagResource(rag_corpus=config.RAG_CORPUS)],
            text=query,
            rag_retrieval_config=rag.RagRetrievalConfig(top_k=config.RAG_TOP_K),
        )
        contexts = resp.contexts.contexts
        passages = [
            {"score": round(getattr(c, "score", 0.0), 4), "text": c.text}
            for c in contexts
        ]
        return {
            "status": "success",
            "query": query,
            "match_count": len(passages),
            "passages": passages,
            "source": "Vertex AI RAG Engine (vector search)",
        }
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "error": str(exc)}


def get_table_schema(table_full_name: str) -> dict[str, Any]:
    """Return column names and types for a BigQuery table.

    Args:
        table_full_name: Fully qualified table, e.g. project.dataset.table
    """
    parts = table_full_name.replace("`", "").split(".")
    if len(parts) != 3:
        return {
            "status": "error",
            "message": "Expected format: project.dataset.table",
        }
    project, dataset, table = parts
    client = bigquery.Client(project=config.GOOGLE_CLOUD_PROJECT)
    query = f"""
    SELECT column_name, data_type, is_nullable
    FROM `{project}.{dataset}.INFORMATION_SCHEMA.COLUMNS`
    WHERE table_name = @table
    ORDER BY ordinal_position
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("table", "STRING", table)]
    )
    try:
        rows = list(client.query(query, job_config=job_config).result())
        return {
            "status": "success",
            "table": table_full_name,
            "columns": [dict(r.items()) for r in rows],
        }
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "message": str(exc)}


def get_pipeline_metadata_catalog() -> dict[str, Any]:
    """Return the Fivetran Platform Connector metadata tables for observability/lineage.

    These tables (in the metadata dataset) describe pipeline run history, freshness,
    schema changes, and source->destination lineage. Query them with query_bigquery.
    """
    p = config.BQ_METADATA_PREFIX
    return {
        "status": "success",
        "metadata_dataset": config.BQ_METADATA_PREFIX,
        "tables": {
            "log": {
                "full_name": f"{p}.log",
                "purpose": "Connection sync events/errors timeline",
                "key_columns": ["time_stamp", "connection_id", "event", "message_event", "message_data", "sync_id"],
            },
            "connection": {
                "full_name": f"{p}.connection",
                "purpose": "Connection inventory: paused state, sync_frequency, destination",
                "key_columns": ["connection_id", "connection_name", "connector_type_id", "paused", "sync_frequency", "destination_id"],
            },
            "incremental_mar": {
                "full_name": f"{p}.incremental_mar",
                "purpose": "Rows synced per table per day (volume/freshness)",
                "key_columns": ["connection_name", "schema_name", "table_name", "measured_date", "incremental_rows", "updated_at"],
            },
            "table_lineage": {
                "full_name": f"{p}.table_lineage",
                "purpose": "Source table -> destination table lineage mapping",
                "key_columns": ["source_table_id", "destination_table_id", "created_at"],
            },
            "destination_table_change_event": {
                "full_name": f"{p}.destination_table_change_event",
                "purpose": "Schema-evolution events on destination tables (what changed)",
                "key_columns": [],
            },
            "source_table": {
                "full_name": f"{p}.source_table",
                "purpose": "Source table catalog (join lineage ids to names)",
                "key_columns": [],
            },
            "destination_table": {
                "full_name": f"{p}.destination_table",
                "purpose": "Destination table catalog (join lineage ids to names)",
                "key_columns": [],
            },
        },
        "tip": "Use query_bigquery with backtick-quoted full names. For latest event use MAX(time_stamp) in log.",
    }


def query_bigquery(sql: str) -> dict[str, Any]:
    f"""Run a read-only SQL query against the hackathon BigQuery project.

    Only SELECT statements are allowed. Use `get_data_catalog` to discover tables
    across `google_sheets`, `analytics`, and Platform Connector metadata datasets.

    Args:
        sql: BigQuery SQL (SELECT only).
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
        return {"status": "success", "row_count": len(records), "rows": records[:50]}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "message": str(exc)}


def get_team_context(project_repo: str = "", include_rag: bool = False) -> dict[str, Any]:
    """Build the MoDeX context pack — the team's shared decision memory for a repo.

    THIS IS THE PRIMARY MEMORY TOOL. It fuses coding-agent session decisions
    (agent_memory.codebase_logs) with GitHub PRs + reviews synced via Fivetran,
    cross-references them, and returns adopted decisions, REJECTED approaches,
    open questions, and gotchas — each dated and cited with provenance
    (session timestamps and Fivetran `_fivetran_synced`). Use this to answer
    "what has the team decided / why / what was rejected" and for session handoff.

    Args:
        project_repo: Repo identifier (e.g. github.com/demo/api-service). Empty = demo repo.
        include_rag: Also attach a conceptual note from Vertex AI RAG.
    """
    from app.memory_graph import build_context_pack

    return build_context_pack(
        project_repo=project_repo or None,
        include_rag=include_rag,
    )


def get_decision_memory(project_repo: str = "") -> dict[str, Any]:
    """Return the cross-referenced decision graph (session events + GitHub via Fivetran).

    Lighter than get_team_context — just the decisions/rejected/open lists plus
    freshness counts, ideal for provenance and "show me the decisions" questions.

    Args:
        project_repo: Repo identifier (empty = demo repo).
    """
    from app.memory_graph import get_decision_graph

    return get_decision_graph(project_repo=project_repo or None)


def get_agent_memory_catalog() -> dict[str, Any]:
    """List projects/repos with Face 1 session memory (coding agent handoff logs)."""
    from app.modex_memory import get_memory_catalog

    return get_memory_catalog()


def get_agent_memory_for_project(project_repo: str, limit: int = 50) -> dict[str, Any]:
    """Replay codebase logs for session handoff — decisions, file edits, errors.

    Primary Face 1 memory from Antigravity append-only event log.

    Args:
        project_repo: Repository or project identifier (e.g. github.com/org/api-service).
        limit: Max log events to return (default 50).
    """
    from app.modex_memory import load_context_from_logs

    return load_context_from_logs(project_repo=project_repo, limit=limit)


def get_codebase_log_timeline(
    project_repo: str,
    event_types: str = "",
    limit: int = 50,
) -> dict[str, Any]:
    """Fetch filtered codebase log timeline for a repo.

    Args:
        project_repo: Repository identifier.
        event_types: Comma-separated filter (e.g. 'decision,file_edit,error').
        limit: Max events (default 50).
    """
    from app.modex_memory import load_context_from_logs

    types_list = [t.strip() for t in event_types.split(",") if t.strip()] or None
    return load_context_from_logs(
        project_repo=project_repo,
        limit=limit,
        event_types=types_list,
    )


def get_modex_fivetran_logs(
    project_repo: str = "",
    limit: int = 50,
) -> dict[str, Any]:
    """Query MoDeX events synced via Fivetran (Sheet → stowed_register → modex_logs).

    Use for provenance questions that need `_fivetran_synced` timestamps.

    Args:
        project_repo: Optional repo filter (e.g. github.com/demo/api-service).
        limit: Max rows (default 50).
    """
    limit = max(1, min(limit, 200))
    table = config.MODEX_FIVETRAN_FULL_TABLE
    where = "1=1"
    if project_repo:
        where = "project_repo = @project_repo"
    sql = f"""
        SELECT event_id, session_id, developer_id, agent_tool, project_repo,
               event_type, file_path, summary, created_at, _fivetran_synced
        FROM `{table}`
        WHERE {where}
        ORDER BY created_at DESC
        LIMIT {limit}
    """
    client = bigquery.Client(project=config.GOOGLE_CLOUD_PROJECT)
    job_config = bigquery.QueryJobConfig()
    if project_repo:
        job_config.query_parameters = [
            bigquery.ScalarQueryParameter("project_repo", "STRING", project_repo)
        ]
    try:
        rows = [
            dict(r.items()) for r in client.query(sql, job_config=job_config).result()
        ]
        for row in rows:
            for key in ("created_at", "_fivetran_synced"):
                if hasattr(row.get(key), "isoformat"):
                    row[key] = row[key].isoformat()
        return {
            "status": "success",
            "table": table,
            "fivetran_connection": config.FIVETRAN_MODEX_LOGS_CONNECTION_ID,
            "row_count": len(rows),
            "rows": rows,
        }
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "message": str(exc), "table": table}
