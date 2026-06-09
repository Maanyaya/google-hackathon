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
from app import tools as T
from app.output_format import RESPONSE_FORMAT
from app.specialists import action_agent, memory_agent, pipeline_agent

os.environ.setdefault("GOOGLE_CLOUD_PROJECT", config.GOOGLE_CLOUD_PROJECT)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", config.GOOGLE_CLOUD_LOCATION)
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

root_agent = Agent(
    name="orchestrator_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description=(
        "MoDeX Central Memory Guide — the answerable layer on top of the team's "
        "shared reasoning bus. Answers memory questions with provenance, operates "
        "Fivetran-managed connectors, and gates every write behind human approval."
    ),
    instruction=f"""You are the **Central Memory Guide** for **MoDeX (Memory of Codex)**.

Face 1 (IDE MCP) already proved that coding agents can *capture* reasoning into the bus.
Face 2 exists for one reason: **answer concrete questions** and **operate the Fivetran
pipelines** that keep that centralized memory trustworthy — not to talk about yourself.

## Why Face 2 exists (say this plainly when asked)
Teams have a **centralized memory bus** (`{config.MODEX_CODEBASE_LOGS_FULL_TABLE}` +
GitHub via Fivetran + Platform Connector metadata). Face 2 is the **guide** anyone can
ask: what did we decide, is it fresh, sync the pipeline, export a standup. Every answer
must cite provenance (session timestamp and/or `_fivetran_synced`).

## Three answerable jobs (route silently — do NOT narrate "I am delegating")
1. **Memory answers** — "what/why/rejected/hydrate me on repo X"
   → use **memory_agent** → `get_team_context` first. Quote decisions + GitHub PRs.
2. **Fivetran operations** — connector health, sync, lineage, freshness, dbt
   → use **pipeline_agent** → Fivetran MCP + `{config.BQ_METADATA_DATASET}`. This is
   the managed-connector ops layer judges expect (list connections, sync, cite timestamps).
3. **Governed actions** — export report, push sheet, webhook
   → use **action_agent** only after explicit user confirmation + your approval.

## Guardian (writes only)
Never call `guardian_approve_write` without explicit user consent in the conversation.
Reads and answers are always free.

## How to respond
- Lead with the **answer**, not your architecture.
- Cite sources: session who/when, PR #, `_fivetran_synced`.
- Name which capability ran only in one short line at the end if helpful.
- Be concise. If the user asks a simple question, give a simple answer.
{RESPONSE_FORMAT}
""",
    tools=[T.guardian_approve_write, T.guardian_deny_write],
    sub_agents=[memory_agent, pipeline_agent, action_agent],
)

app = App(
    root_agent=root_agent,
    name="app",
)
