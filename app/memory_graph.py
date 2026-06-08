"""MoDeX decision memory — cross-reference session reasoning with GitHub (via Fivetran).

This is the heart of MoDeX: it fuses two sources of engineering "why" —
  1. coding-agent **session decisions** (Face 1 MCP -> agent_memory.codebase_logs)
  2. **GitHub PRs + reviews** synced by Fivetran (github.pull_request / pull_request_review)

and returns a curated, provenance-stamped **context pack** that a new coding
agent can be hydrated with. Every item is dated and cited (session timestamp
and/or Fivetran `_fivetran_synced`), so the agent gets *trustworthy* context,
not a fuzzy blob.

Retrieval is hybrid: precise SQL for structured/cited facts (primary) plus
optional RAG for conceptual grounding (secondary).
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any

from google.cloud import bigquery

from app import config

_STOPWORDS = frozenset({
    "the", "and", "for", "with", "this", "that", "from", "into", "over", "than",
    "use", "using", "used", "need", "needs", "our", "are", "was", "were", "has",
    "have", "but", "not", "via", "out", "new", "add", "added", "switch", "chose",
    "choose", "instead", "rejected", "approach", "decision", "decided", "test",
    "store", "auth", "primary", "make", "made", "team", "code", "data",
    # ambiguous domain words that otherwise over-link unrelated decisions
    "session", "server", "client", "service", "support", "update", "change",
})


def _bq() -> bigquery.Client:
    return bigquery.Client(project=config.GOOGLE_CLOUD_PROJECT)


def _iso(value: Any) -> Any:
    return value.isoformat() if hasattr(value, "isoformat") else value


def _normalize_repo(project_repo: str) -> str:
    """codebase_logs 'github.com/demo/api-service' -> github full_name 'demo/api-service'."""
    repo = (project_repo or "").strip()
    for prefix in ("https://github.com/", "http://github.com/", "github.com/"):
        if repo.startswith(prefix):
            return repo[len(prefix):]
    return repo


def _keywords(text: str) -> set[str]:
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9_+.-]{2,}", (text or "").lower())
    return {t for t in tokens if t not in _STOPWORDS and len(t) > 3}


def _fetch_session_decisions(repo: str, limit: int) -> list[dict[str, Any]]:
    sql = f"""
        SELECT summary, developer_id, agent_tool, created_at, commit_sha, file_path, payload_json
        FROM `{config.MODEX_CODEBASE_LOGS_FULL_TABLE}`
        WHERE project_repo = @repo AND event_type = 'decision'
        ORDER BY created_at DESC
        LIMIT @limit
    """
    job_config = bigquery.QueryJobConfig(query_parameters=[
        bigquery.ScalarQueryParameter("repo", "STRING", repo),
        bigquery.ScalarQueryParameter("limit", "INT64", limit),
    ])
    rows = _bq().query(sql, job_config=job_config).result()
    out: list[dict[str, Any]] = []
    for r in rows:
        rec = dict(r.items())
        rec["created_at"] = _iso(rec.get("created_at"))
        out.append(rec)
    return out


def _fetch_session_signals(repo: str) -> dict[str, Any]:
    sql = f"""
        SELECT event_type, summary, file_path, developer_id, agent_tool, created_at
        FROM `{config.MODEX_CODEBASE_LOGS_FULL_TABLE}`
        WHERE project_repo = @repo
        ORDER BY created_at DESC
        LIMIT 200
    """
    job_config = bigquery.QueryJobConfig(query_parameters=[
        bigquery.ScalarQueryParameter("repo", "STRING", repo),
    ])
    rows = [dict(r.items()) for r in _bq().query(sql, job_config=job_config).result()]
    errors = [
        {"summary": r["summary"], "at": _iso(r["created_at"]), "who": r.get("developer_id")}
        for r in rows if r.get("event_type") == "error"
    ][:5]
    files = []
    seen = set()
    for r in rows:
        fp = r.get("file_path")
        if r.get("event_type") == "file_edit" and fp and fp not in seen:
            seen.add(fp)
            files.append(fp)
    last_event = _iso(rows[0]["created_at"]) if rows else None
    return {
        "errors": errors,
        "files_recent": files[:10],
        "last_event": last_event,
        "event_total": len(rows),
    }


def _github_available() -> bool:
    sql = f"""
        SELECT table_name
        FROM `{config.GITHUB_PREFIX}.INFORMATION_SCHEMA.TABLES`
        WHERE table_name = 'pull_request'
        LIMIT 1
    """
    try:
        return len(list(_bq().query(sql).result())) > 0
    except Exception:  # noqa: BLE001
        return False


def _fetch_github_prs(full_name: str) -> list[dict[str, Any]]:
    sql = f"""
        SELECT
          pr.number AS number, pr.title AS title, pr.body AS body, pr.state AS state,
          pr.merged AS merged, pr.merged_at AS merged_at, pr.created_at AS created_at,
          pr.html_url AS html_url, pr.merge_commit_sha AS merge_commit_sha,
          au.login AS author, pr._fivetran_synced AS synced
        FROM `{config.GITHUB_PREFIX}.pull_request` pr
        JOIN `{config.GITHUB_PREFIX}.repository` r
          ON pr.repository_id = r.id AND r.full_name = @full_name
        LEFT JOIN `{config.GITHUB_PREFIX}.user` au ON pr.user_id = au.id
        WHERE COALESCE(pr._fivetran_deleted, FALSE) = FALSE
        ORDER BY pr.created_at DESC
        LIMIT 100
    """
    job_config = bigquery.QueryJobConfig(query_parameters=[
        bigquery.ScalarQueryParameter("full_name", "STRING", full_name),
    ])
    prs = [dict(r.items()) for r in _bq().query(sql, job_config=job_config).result()]

    review_sql = f"""
        SELECT rev.pull_request_id AS pr_id, pr.number AS number, rev.state AS state,
               rev.body AS body, ru.login AS reviewer, rev.submitted_at AS submitted_at
        FROM `{config.GITHUB_PREFIX}.pull_request_review` rev
        JOIN `{config.GITHUB_PREFIX}.pull_request` pr ON rev.pull_request_id = pr.id
        LEFT JOIN `{config.GITHUB_PREFIX}.user` ru ON rev.user_id = ru.id
    """
    reviews_by_num: dict[int, list[dict[str, Any]]] = {}
    for r in _bq().query(review_sql).result():
        rec = dict(r.items())
        reviews_by_num.setdefault(rec["number"], []).append({
            "reviewer": rec.get("reviewer"),
            "state": rec.get("state"),
            "body": rec.get("body"),
            "at": _iso(rec.get("submitted_at")),
        })

    for pr in prs:
        pr["created_at"] = _iso(pr.get("created_at"))
        pr["merged_at"] = _iso(pr.get("merged_at"))
        pr["synced"] = _iso(pr.get("synced"))
        pr["reviews"] = reviews_by_num.get(pr["number"], [])
    return prs


def _pr_status(pr: dict[str, Any]) -> str:
    if pr.get("merged"):
        return "adopted"
    if pr.get("state") == "open":
        return "proposed"
    for rev in pr.get("reviews", []):
        if rev.get("state") == "CHANGES_REQUESTED":
            return "rejected"
    return "closed"


def _fetch_sheet_mirror_stats() -> dict[str, Any]:
    """Fivetran mirror of Face 1 logs: Sheet -> modex_logs.modex_logs."""
    sql = f"""
        SELECT MAX(_fivetran_synced) AS last_synced, COUNT(1) AS row_count
        FROM `{config.MODEX_FIVETRAN_FULL_TABLE}`
    """
    try:
        rows = list(_bq().query(sql).result())
        if rows:
            return {
                "last_synced": _iso(rows[0].get("last_synced")),
                "row_count": int(rows[0].get("row_count") or 0),
            }
    except Exception:  # noqa: BLE001
        pass
    return {"last_synced": None, "row_count": 0}


def build_context_pack(
    project_repo: str | None = None,
    limit: int = 40,
    include_rag: bool = False,
) -> dict[str, Any]:
    """Assemble a curated, provenance-stamped context pack for a coding agent.

    Fuses session decisions (codebase_logs) with GitHub PRs/reviews (Fivetran),
    cross-references them, and returns adopted/rejected/open decisions plus
    gotchas and a tight hydration_prompt — each item dated and cited.

    Args:
        project_repo: Repo identifier (e.g. github.com/demo/api-service).
        limit: Max session decisions to scan.
        include_rag: Also attach a conceptual note from Vertex AI RAG.
    """
    repo = project_repo or config.MODEX_DEMO_REPO
    full_name = _normalize_repo(repo)

    try:
        session_decisions = _fetch_session_decisions(repo, limit)
        signals = _fetch_session_signals(repo)
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "message": f"session memory query failed: {exc}"}

    github_synced = None
    prs: list[dict[str, Any]] = []
    if _github_available():
        try:
            prs = _fetch_github_prs(full_name)
            synced_times = [p["synced"] for p in prs if p.get("synced")]
            github_synced = max(synced_times) if synced_times else None
        except Exception:  # noqa: BLE001
            prs = []

    sheet_mirror = _fetch_sheet_mirror_stats()

    # Cross-reference: link each session decision to GitHub PRs by topic overlap.
    decisions: list[dict[str, Any]] = []
    linked_pr_numbers: set[int] = set()

    for d in session_decisions:
        d_kw = _keywords(d.get("summary", ""))
        sources = [{
            "type": "session",
            "who": d.get("developer_id"),
            "tool": d.get("agent_tool"),
            "at": d.get("created_at"),
            "ref": "agent_memory.codebase_logs",
        }]
        matched = []
        for pr in prs:
            pr_kw = _keywords(f"{pr.get('title','')} {pr.get('body','')}")
            if d_kw & pr_kw:
                matched.append(pr)
                linked_pr_numbers.add(pr["number"])
        for pr in matched:
            top_review = next((r for r in pr.get("reviews", []) if r.get("body")), None)
            sources.append({
                "type": "github_pr",
                "number": pr["number"],
                "title": pr["title"],
                "who": pr.get("author"),
                "status": _pr_status(pr),
                "url": pr.get("html_url"),
                "review": (f"{top_review['reviewer']} ({top_review['state']}): {top_review['body']}"
                           if top_review else None),
                "at": pr.get("merged_at") or pr.get("created_at"),
                "synced": pr.get("synced"),
            })
        summary = d.get("summary", "")
        status = "adopted"
        if re.search(r"\b(reject|instead of|not |avoid|drop)\b", summary, re.I):
            status = "rejected"
        decisions.append({
            "decision": summary,
            "status": status,
            "confidence": "corroborated" if matched else "session-only",
            "sources": sources,
        })

    # GitHub PRs with no matching session decision = decisions the agents never saw.
    rejected: list[dict[str, Any]] = []
    open_questions: list[dict[str, Any]] = []
    for pr in prs:
        status = _pr_status(pr)
        top_review = next((r for r in pr.get("reviews", []) if r.get("body")), None)
        entry = {
            "decision": pr["title"],
            "why": (pr.get("body") or "")[:240],
            "pr": pr["number"],
            "author": pr.get("author"),
            "url": pr.get("html_url"),
            "review": (f"{top_review['reviewer']} ({top_review['state']}): {top_review['body']}"
                       if top_review else None),
            "source": "github_pr",
            "synced": pr.get("synced"),
            "confidence": "corroborated" if pr["number"] in linked_pr_numbers else "github-only",
        }
        if status == "rejected":
            rejected.append(entry)
        elif status == "proposed":
            open_questions.append(entry)
        elif pr["number"] not in linked_pr_numbers and status == "adopted":
            decisions.append({
                "decision": pr["title"],
                "status": "adopted",
                "confidence": "github-only",
                "sources": [{
                    "type": "github_pr", "number": pr["number"], "title": pr["title"],
                    "who": pr.get("author"), "status": status, "url": pr.get("html_url"),
                    "review": entry["review"], "at": pr.get("merged_at"), "synced": pr.get("synced"),
                }],
            })

    for d in decisions:
        types = {s["type"] for s in d.get("sources", [])}
        d["corroboration"] = len(types)
        d["source_types"] = sorted(types)
        if "session" in types and "github_pr" in types:
            d["confidence"] = "corroborated"

    rag_note = None
    if include_rag:
        try:
            from app.tools import search_knowledge_base
            res = search_knowledge_base(f"engineering context for {full_name}")
            if res.get("status") == "success" and res.get("passages"):
                rag_note = res["passages"][0]["text"][:300]
        except Exception:  # noqa: BLE001
            rag_note = None

    connected_sources = ["session"]
    if sheet_mirror.get("row_count"):
        connected_sources.append("sheet_mirror")
    if prs:
        connected_sources.append("github")

    corroborated = sum(1 for d in decisions if d.get("confidence") == "corroborated")
    hydration = _render_hydration(
        full_name,
        decisions,
        rejected,
        open_questions,
        signals,
        github_synced,
        sheet_mirror.get("last_synced"),
    )

    return {
        "status": "success",
        "project_repo": repo,
        "github_repo": full_name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "freshness": {
            "session_last_event": signals.get("last_event"),
            "sheet_last_synced": sheet_mirror.get("last_synced"),
            "sheet_row_count": sheet_mirror.get("row_count", 0),
            "github_last_synced": github_synced,
            "github_source": "live" if github_synced and config.GITHUB_DATASET == "github" else (
                "demo" if prs else "not_connected"),
            "fivetran_connection": config.FIVETRAN_MODEX_LOGS_CONNECTION_ID,
            "connected_sources": connected_sources,
        },
        "counts": {
            "decisions": len(decisions),
            "corroborated": corroborated,
            "rejected": len(rejected),
            "open_questions": len(open_questions),
            "gotchas": len(signals.get("errors", [])),
            "sheet_rows": sheet_mirror.get("row_count", 0),
            "sources_connected": len(connected_sources),
        },
        "sources": [
            {"id": "session", "label": "Coding-agent sessions", "kind": "MCP capture",
             "count": len(session_decisions), "synced": signals.get("last_event"),
             "status": "live"},
            {"id": "sheet_mirror", "label": "Sheet mirror (Fivetran bus)", "kind": "Fivetran",
             "count": sheet_mirror.get("row_count", 0), "synced": sheet_mirror.get("last_synced"),
             "status": "live" if sheet_mirror.get("row_count") else "not_connected"},
            {"id": "github", "label": "GitHub PRs + reviews", "kind": "Fivetran",
             "count": len(prs), "synced": github_synced,
             "status": ("live" if (github_synced and config.GITHUB_DATASET == "github")
                        else ("demo" if prs else "not_connected"))},
        ],
        "decisions": decisions,
        "rejected": rejected,
        "open_questions": open_questions,
        "gotchas": signals.get("errors", []),
        "files_recent": signals.get("files_recent", []),
        "rag_note": rag_note,
        "hydration_prompt": hydration,
    }


def _render_hydration(
    full_name: str,
    decisions: list[dict[str, Any]],
    rejected: list[dict[str, Any]],
    open_questions: list[dict[str, Any]],
    signals: dict[str, Any],
    github_synced: str | None,
    sheet_synced: str | None = None,
) -> str:
    lines = [f"# MoDeX shared context for {full_name}"]
    fresh = []
    if signals.get("last_event"):
        fresh.append(f"session memory current to {signals['last_event']}")
    if sheet_synced:
        fresh.append(f"Sheet mirror synced via Fivetran at {sheet_synced}")
    if github_synced:
        fresh.append(f"GitHub synced via Fivetran at {github_synced}")
    if fresh:
        lines.append("Freshness: " + "; ".join(fresh))

    if decisions:
        lines.append("\n## Decisions the team already made (don't relitigate):")
        for d in decisions[:8]:
            cite = []
            for s in d["sources"]:
                t = s["type"]
                if t == "github_pr":
                    cite.append(f"GitHub PR #{s['number']} by {s.get('who')}" +
                                (f" - {s['review']}" if s.get("review") else ""))
                else:
                    cite.append(f"{s.get('tool')} session by {s.get('who')} ({s.get('at')})")
            tag = "[corroborated]" if d.get("confidence") == "corroborated" else ""
            lines.append(f"- {d['decision']} {tag}\n    cited: " + " | ".join(c for c in cite if c))

    if rejected:
        lines.append("\n## Approaches the team REJECTED (do not redo):")
        for r in rejected[:5]:
            lines.append(f"- {r['decision']} - {r.get('review') or r.get('why')}"
                         f"  (PR #{r.get('pr')})")

    if open_questions:
        lines.append("\n## Open questions / in-flight:")
        for o in open_questions[:5]:
            lines.append(f"- {o['decision']} (PR #{o.get('pr')}, {o.get('author')})")

    if signals.get("errors"):
        lines.append("\n## Known gotchas (recent errors):")
        for e in signals["errors"][:3]:
            lines.append(f"- {e['summary']} ({e.get('at')})")

    if signals.get("files_recent"):
        lines.append("\n## Recently touched files: " + ", ".join(signals["files_recent"][:8]))

    lines.append("\nEvery item above is sourced from the team's shared memory "
                 "(coding-agent sessions + GitHub synced through Fivetran). "
                 "Build on it instead of starting cold.")
    return "\n".join(lines)


def get_decision_graph(project_repo: str | None = None) -> dict[str, Any]:
    """Dashboard-friendly view of the cross-referenced decision memory."""
    pack = build_context_pack(project_repo=project_repo, include_rag=False)
    if pack.get("status") != "success":
        return pack
    return {
        "status": "success",
        "project_repo": pack["project_repo"],
        "github_repo": pack["github_repo"],
        "freshness": pack["freshness"],
        "counts": pack["counts"],
        "sources": pack.get("sources", []),
        "decisions": pack["decisions"],
        "rejected": pack["rejected"],
        "open_questions": pack["open_questions"],
    }
