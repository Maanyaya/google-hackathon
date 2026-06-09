"""MoDeX served-over-the-web API — Face 1 as a real multi-user tool.

The blocker for sharing MoDeX was that the local MCP wrote to BigQuery using a
service-account key file that only lived on one machine. This router fixes that:
Cloud Run already runs with a service account, so it holds the credentials. Each
teammate only needs a per-user API key + this base URL — no GCP key, no cloning.

A thin stdio MCP client (`modex_mcp/remote_client.py`) calls these endpoints, so
the exact same memory tools work in Cursor on Windows and Antigravity on a Mac,
all writing into the one shared BigQuery memory bus.

Auth: send the per-user key as `Authorization: Bearer <key>` (or `X-MoDeX-Key`).
The resolved developer_id is stamped on every event for clean attribution.
"""

from __future__ import annotations

import hmac
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel

from app import config
from app.memory_graph import build_context_pack
from modex_mcp.memory_store import (
    append_codebase_log,
    get_memory_catalog,
    load_context_from_logs,
    load_session_history,
    log_decision,
    save_compressed_context,
    save_memory,
)

router = APIRouter(prefix="/api/v1", tags=["modex-mcp"])


def _resolve_developer(authorization: str | None, x_modex_key: str | None) -> str:
    """Validate the per-user key and return the developer_id it maps to."""
    keys = config.MODEX_API_KEYS
    if not keys:
        raise HTTPException(
            status_code=503,
            detail=(
                "MoDeX API has no API keys configured. Set MODEX_API_KEYS on the "
                "server (format 'user:key,user2:key2')."
            ),
        )

    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
    elif x_modex_key:
        token = x_modex_key.strip()

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Missing API key. Send 'Authorization: Bearer <your-key>'.",
        )

    # Constant-time compare against every configured key to avoid timing leaks.
    for secret, developer_id in keys.items():
        if hmac.compare_digest(token, secret):
            return developer_id
    raise HTTPException(status_code=403, detail="Invalid MoDeX API key.")


def require_developer(
    authorization: str | None = Header(default=None),
    x_modex_key: str | None = Header(default=None, alias="X-MoDeX-Key"),
) -> str:
    return _resolve_developer(authorization, x_modex_key)


class AppendBody(BaseModel):
    agent_tool: str
    project_repo: str
    event_type: str
    summary: str
    session_id: str | None = None
    file_path: str | None = None
    commit_sha: str | None = None
    payload: dict[str, Any] | None = None
    parent_event_id: str | None = None


class DecisionBody(BaseModel):
    agent_tool: str
    project_repo: str
    decision: str
    context: str = ""
    session_id: str | None = None
    file_path: str | None = None


class SessionEndBody(BaseModel):
    agent_tool: str
    project_repo: str
    summary: str
    decisions: list[str] | None = None
    files_touched: list[str] | None = None
    rejected_approaches: list[str] | None = None
    session_id: str | None = None


class CompressBody(BaseModel):
    agent_tool: str
    project_repo: str
    session_id: str | None = None
    event_limit: int = 300


@router.get("/health")
def health() -> dict[str, Any]:
    """Unauthenticated readiness probe + whether the server is share-ready."""
    return {
        "status": "ok",
        "service": "modex-memory",
        "keys_configured": bool(config.MODEX_API_KEYS),
        "developers": sorted(set(config.MODEX_API_KEYS.values())),
    }


@router.get("/whoami")
def whoami(developer: str = Depends(require_developer)) -> dict[str, Any]:
    """Confirm a key works and show which developer it logs as."""
    return {"status": "ok", "developer_id": developer}


@router.post("/memory/append")
def api_append(
    body: AppendBody, developer: str = Depends(require_developer)
) -> dict[str, Any]:
    return append_codebase_log(
        developer_id=developer,
        agent_tool=body.agent_tool,
        project_repo=body.project_repo,
        event_type=body.event_type,
        summary=body.summary,
        session_id=body.session_id,
        file_path=body.file_path,
        commit_sha=body.commit_sha,
        payload=body.payload,
        parent_event_id=body.parent_event_id,
    )


@router.post("/memory/decision")
def api_decision(
    body: DecisionBody, developer: str = Depends(require_developer)
) -> dict[str, Any]:
    return log_decision(
        developer_id=developer,
        agent_tool=body.agent_tool,
        project_repo=body.project_repo,
        decision=body.decision,
        context=body.context,
        session_id=body.session_id,
        file_path=body.file_path,
    )


@router.post("/memory/session_end")
def api_session_end(
    body: SessionEndBody, developer: str = Depends(require_developer)
) -> dict[str, Any]:
    return save_memory(
        developer_id=developer,
        agent_tool=body.agent_tool,
        project_repo=body.project_repo,
        summary=body.summary,
        decisions=body.decisions,
        files_touched=body.files_touched,
        rejected_approaches=body.rejected_approaches,
        session_id=body.session_id,
    )


@router.post("/memory/compress")
def api_compress(
    body: CompressBody, developer: str = Depends(require_developer)
) -> dict[str, Any]:
    """Deterministic JSON compression of raw logs (not LLM summarization)."""
    return save_compressed_context(
        developer_id=developer,
        agent_tool=body.agent_tool,
        project_repo=body.project_repo,
        session_id=body.session_id,
        event_limit=body.event_limit,
    )


@router.get("/memory/context")
def api_context(
    project_repo: str = Query(...),
    limit: int = Query(40, ge=1, le=200),
    include_rag: bool = Query(False),
    developer: str = Depends(require_developer),
) -> dict[str, Any]:
    """Curated, provenance-stamped context pack to hydrate a fresh session."""
    try:
        return build_context_pack(
            project_repo=project_repo, limit=limit, include_rag=include_rag
        )
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "error",
            "message": f"context pack failed, falling back to raw logs: {exc}",
            "fallback": load_context_from_logs(
                project_repo=project_repo, limit=limit
            ),
        }


@router.get("/memory/timeline")
def api_timeline(
    project_repo: str = Query(...),
    limit: int = Query(50, ge=1, le=200),
    session_id: str | None = Query(None),
    developer: str = Depends(require_developer),
) -> dict[str, Any]:
    return load_context_from_logs(
        project_repo=project_repo, limit=limit, session_id=session_id
    )


@router.get("/memory/history")
def api_history(
    project_repo: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    developer: str = Depends(require_developer),
) -> dict[str, Any]:
    return load_session_history(
        developer_id=developer, project_repo=project_repo, limit=limit
    )


@router.get("/memory/catalog")
def api_catalog(developer: str = Depends(require_developer)) -> dict[str, Any]:
    return get_memory_catalog()
