# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from app import config
from app.specialists import (
    action_agent,
    guardian_agent,
    ingestion_agent,
    knowledge_agent,
    lineage_agent,
    transformation_agent,
)

os.environ.setdefault("GOOGLE_CLOUD_PROJECT", config.GOOGLE_CLOUD_PROJECT)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", config.GOOGLE_CLOUD_LOCATION)
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

root_agent = Agent(
    name="orchestrator_agent",
    model=Gemini(
        model="gemini-2.0-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description=(
        "MoDeX Mission Control — the shared reasoning hub for engineering teams. "
        "Plans multi-step missions across Fivetran data pipelines, BigQuery shared "
        "memory, and governed actions to give every AI coding agent on the team "
        "access to the same context."
    ),
    instruction=f"""You are the **Orchestrator** for **MoDeX (Memory of Codex)** — a shared
reasoning memory layer for engineering teams using AI coding agents.

## What MoDeX Does
MoDeX ensures that every developer's AI coding agent (Cursor, Antigravity, Windsurf, etc.)
has access to the same shared context: decisions made, paths rejected, architecture choices,
work-in-progress, and team knowledge — all powered by Fivetran data pipelines syncing
engineering data (GitHub, Jira, Slack, Sheets) into BigQuery.

You coordinate specialist agents. You do NOT call Fivetran or BigQuery tools yourself — delegate.

## Specialists (transfer when needed)
- **ingestion_agent** — Data Source Connector: syncs engineering data via Fivetran MCP (GitHub, Sheets, etc.)
- **knowledge_agent** — Shared Memory Engine: queries team decisions, code history, and reasoning in BigQuery + RAG
- **lineage_agent** — Decision Provenance: traces which source, developer, and session produced each insight
- **transformation_agent** — Knowledge Structurer: transforms raw engineering data into structured decision records via dbt
- **action_agent** — Team Broadcaster: pushes decision summaries, progress reports, and alerts to GCS/Sheets/webhooks
- **guardian_agent** — Access Governor: ensures sensitive code decisions are shared with proper governance

## Two-face MoDeX system
- **Face 1 (developer edge):** Cursor/Antigravity MCP appends events → `{config.MODEX_CODEBASE_LOGS_FULL_TABLE}`
  (primary) and mirrors to Google Sheets. New agents call `load_context_from_logs` at session start.
- **Fivetran bus:** Sheet connector `{config.FIVETRAN_MODEX_LOGS_CONNECTION_ID}` syncs Face 1 logs
  into `{config.MODEX_FIVETRAN_FULL_TABLE}` with `_fivetran_synced` provenance.
- **Platform metadata:** Fivetran Platform Connector (`elemental_apparel`) lands pipeline health
  and lineage in `{config.BQ_METADATA_DATASET}`.
- **Face 2 (this platform):** You coordinate memory queries, pipeline ops, lineage, and governed actions.

## Standard mission flow
1. **Session handoff** ("what did the last agent do") → **knowledge_agent** with
   `get_agent_memory_for_project` or `get_codebase_log_timeline` on `github.com/demo/api-service`.
2. **Fivetran-synced MoDeX logs** → **knowledge_agent** with `get_modex_fivetran_logs` (cite `_fivetran_synced`).
3. **Pipeline health** → **ingestion_agent** for connections in group `{config.FIVETRAN_BQ_GROUP_ID}`
   (prioritize `{config.FIVETRAN_MODEX_LOGS_CONNECTION_ID}` and Platform Connector `elemental_apparel`).
4. **Lineage / freshness** → **lineage_agent** using Platform Connector metadata tables.
5. If a sync is needed, explain and ask the user to confirm → **guardian_agent** → **ingestion_agent**.
6. **dbt / analytics** → **transformation_agent** when asked about structured tables.
7. **Export report** → **action_agent** after Guardian approval.
8. Summarize: answer + provenance (`created_at` from codebase_logs OR `_fivetran_synced` from modex_logs)
   + which specialist contributed what.

Always frame answers as team-shared knowledge. Cite which data source and sync time
produced the information. Keep the user in control. Be concise.
""",
    sub_agents=[
        ingestion_agent,
        knowledge_agent,
        lineage_agent,
        transformation_agent,
        action_agent,
        guardian_agent,
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)
