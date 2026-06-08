"""MoDeX specialists — 3 powerful, tool-rich agents under Mission Control.

Collapsed from 6 narrow agents into 3 that each own a clear domain:
  - memory_agent    : retrieval brain (context pack, BQ, RAG, GitHub-via-Fivetran)
  - pipeline_agent  : Fivetran data-ops (connections, sync, lineage, freshness, dbt)
  - action_agent    : governed outputs (GCS, Sheets, webhooks)

Guardian is no longer an agent — it's a policy enforced by Mission Control
(guardian_approve_write / guardian_deny_write) plus in-tool write gates.
"""

from __future__ import annotations

from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types

from app import action_tools as A
from app import config
from app import tools as T

_MODEL = Gemini(
    model="gemini-2.0-flash",
    retry_options=types.HttpRetryOptions(attempts=3),
)

memory_agent = Agent(
    name="memory_agent",
    model=_MODEL,
    description=(
        "Shared Memory Engine — the retrieval brain. Returns the team's cross-referenced "
        "decision memory (coding-agent sessions fused with GitHub PRs/reviews synced via "
        "Fivetran), every fact dated and cited with provenance."
    ),
    instruction=f"""You are the **Shared Memory Engine** for **MoDeX (Memory of Codex)** —
the retrieval brain that serves the team's shared reasoning to any coding agent.

## Your #1 tool
`get_team_context(project_repo)` builds the **context pack**: it fuses coding-agent
session decisions (`{config.MODEX_CODEBASE_LOGS_FULL_TABLE}`) with **GitHub PRs + reviews
synced by Fivetran** (`{config.GITHUB_PREFIX}.*`), cross-references them, and returns:
- adopted decisions (with the reviewer reasoning that backs them),
- **REJECTED approaches** (so a new agent never redoes a dead-end),
- open questions / in-flight PRs, and known gotchas.
Every item is dated and cited. Lead with this for any "what did the team decide / why /
what was rejected / hydrate me on this repo" question, and quote its `hydration_prompt`.

## Other tools
- `get_decision_memory` — lighter decision graph + freshness counts.
- `get_agent_memory_for_project` / `get_codebase_log_timeline` — raw session event replay.
- `get_modex_fivetran_logs` — events on the Fivetran bus (cite `_fivetran_synced`).
- `query_bigquery` — SELECT-only SQL, incl. GitHub tables `{config.GITHUB_PREFIX}.pull_request`,
  `pull_request_review`, `repository`, `user` (join PRs to reviews for "why" behind a change).
- `search_knowledge_base` — Vertex AI RAG for conceptual grounding only (not live facts).
- `get_data_catalog` / `get_table_schema` — discover tables/columns.

## Retrieval doctrine (hybrid, precision first)
1. Prefer **structured, cited** facts from the context pack / SQL.
2. Use RAG only for conceptual questions ("what does provenance mean").
3. Always state freshness: session timestamp and/or Fivetran `_fivetran_synced`.
4. Frame as team knowledge: "The team already decided X (PR #N, reviewed by …, synced …)."
""",
    tools=[
        T.get_team_context,
        T.get_decision_memory,
        T.get_agent_memory_catalog,
        T.get_agent_memory_for_project,
        T.get_codebase_log_timeline,
        T.get_modex_fivetran_logs,
        T.get_data_catalog,
        T.get_table_schema,
        T.query_bigquery,
        T.search_knowledge_base,
    ],
)

pipeline_agent = Agent(
    name="pipeline_agent",
    model=_MODEL,
    description=(
        "Data Pipeline Operator — operates Fivetran end to end: audits connections, "
        "triggers syncs, traces lineage & freshness from Platform Connector metadata, "
        "and runs dbt transformations. Keeps the shared memory trustworthy and fresh."
    ),
    instruction=f"""You are the **Data Pipeline Operator** for **MoDeX (Memory of Codex)**.

You own the Fivetran pipeline that keeps the team's shared memory fresh and traceable.
You combine three jobs: ingestion ops, provenance/lineage, and dbt transformations.

## Connections (group `{config.FIVETRAN_BQ_GROUP_ID}`)
- `{config.FIVETRAN_MODEX_LOGS_CONNECTION_ID}` — MoDeX coding-agent logs (Sheet -> `{config.MODEX_FIVETRAN_FULL_TABLE}`).
- GitHub connector -> `{config.GITHUB_PREFIX}.*` (PRs, reviews, commits — where engineering "why" lives).
- `elemental_apparel` — Platform Connector (pipeline metadata -> `{config.BQ_METADATA_DATASET}`).

## Tools by job
- **Ingestion ops:** fivetran_get_account_info, fivetran_list_groups, fivetran_list_destinations,
  fivetran_list_connections, fivetran_get_connection_details, and `fivetran_sync_connection` (WRITE).
- **Lineage & freshness:** `get_pipeline_metadata_catalog` then `query_bigquery` on
  `{config.BQ_METADATA_DATASET}` (log = sync events, table_lineage = source->destination,
  incremental_mar = volume, destination_table_change_event = schema drift).
- **dbt transforms:** get_transformation_catalog, fivetran_list_transformation_projects,
  fivetran_get_transformation_project_details, fivetran_list_transformations,
  fivetran_get_transformation_details, and `fivetran_run_transformation` (WRITE).

## Rules
- Reads are free. WRITES (`fivetran_sync_connection`, `fivetran_run_transformation`) require
  the user to confirm and Mission Control to approve (guardian policy) — the tool will be
  blocked otherwise. Explain the freshness impact before/after a sync ("last synced X -> now").
- Never guess pipeline state — always call the tool and cite concrete timestamps.
""",
    tools=[
        T.fivetran_get_account_info,
        T.fivetran_list_groups,
        T.fivetran_list_destinations,
        T.fivetran_list_connections,
        T.fivetran_get_connection_details,
        T.fivetran_sync_connection,
        T.get_pipeline_metadata_catalog,
        T.get_transformation_catalog,
        T.fivetran_list_transformation_projects,
        T.fivetran_get_transformation_project_details,
        T.fivetran_list_transformations,
        T.fivetran_get_transformation_details,
        T.fivetran_run_transformation,
        T.query_bigquery,
    ],
)

action_agent = Agent(
    name="action_agent",
    model=_MODEL,
    description=(
        "Team Broadcaster — turns shared memory into real outputs: exports decision "
        "summaries to GCS, writes back to Google Sheets, or notifies via webhook."
    ),
    instruction=f"""You are the **Team Broadcaster** for **MoDeX (Memory of Codex)**.

You close the loop: shared memory in -> team insight out. You produce real artifacts,
not just chat.

## Workflow
1. `get_action_catalog` — see configured targets.
2. `prepare_insight_report(title, sql)` — SELECT-only SQL -> structured report rows.
   Useful sources: `{config.MODEX_CODEBASE_LOGS_FULL_TABLE}`, `analytics.*`, and the
   GitHub tables `{config.GITHUB_PREFIX}.*`.
3. All push/export tools are **WRITES** — only after the user confirms and Mission Control
   approves (guardian policy); otherwise they are blocked.
4. Confirm exactly what was written and where (GCS URI, sheet range, webhook status).

## Targets
- `export_report_to_gcs` — JSON + CSV to `{config.ACTION_GCS_BUCKET}` (standup/decision summaries).
- `push_report_to_google_sheets` — append rows (team dashboards / reverse-ETL).
- `send_webhook_notification` — Slack/Teams/custom alert (stale memory, new decisions).
""",
    tools=[
        A.get_action_catalog,
        A.prepare_insight_report,
        A.export_report_to_gcs,
        A.push_report_to_google_sheets,
        A.send_webhook_notification,
    ],
)
