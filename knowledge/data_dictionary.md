# MoDeX (Memory of Codex) — Knowledge Base

This document grounds the MoDeX agent team. It covers the platform architecture,
shared memory concepts, engineering data schemas, Fivetran pipeline concepts, and
how to answer team questions — so agents can handle both analytical queries and
conceptual "what/why/how" questions about the team's engineering decisions.

## What is MoDeX?

MoDeX (Memory of Codex) is a shared reasoning memory layer for engineering teams
using AI coding agents. When 15 developers on a team each use their own AI coding
agent (Cursor, Antigravity, Windsurf, etc.), every agent starts from scratch —
no shared context, no shared decisions, no memory of what the team decided before.

MoDeX solves this by:
1. **Syncing** engineering data from multiple sources (GitHub, Jira, Slack, Sheets)
   into a centralized warehouse (BigQuery) via Fivetran — the data pipeline backbone.
2. **Indexing** this data for semantic search via Vertex AI RAG Engine.
3. **Querying** it through a team of specialized AI agents that can answer:
   "Why did we choose X?", "Who worked on Y?", "What was rejected and why?"
4. **Acting** on insights — pushing reports, alerts, and summaries back to the team.

## Why Shared Memory Matters

Today's AI coding agents are **amnesiac and isolated**:
- **Git** records what changed, not WHY the decision was made.
- **Jira** records task assignments, not the reasoning behind implementation choices.
- **Slack** has conversations, but they're unstructured and not queryable by agents.
- **Confluence/Notion** docs go stale within days.
- **Cursor/Antigravity sessions** die when the conversation ends — not shared across team.

MoDeX captures the reasoning behind engineering decisions — code-grounded and
verifiable against the actual codebase. It's not general-purpose memory; it's
structurally designed for engineering context.

## How Fivetran Powers MoDeX

Fivetran is the **data pipeline backbone** — it handles the hard problem of getting
engineering data from scattered sources into one queryable warehouse:

- **GitHub connector** → syncs commits, pull requests, reviews, issues into BigQuery
- **Google Sheets connector** → syncs decision logs, team notes, project data
- **Jira connector** → syncs tickets, decisions, sprint data (production vision)
- **Slack connector** → syncs conversations, threads, decisions (production vision)
- **Notion connector** → syncs docs, ADRs, wikis (production vision)

Without Fivetran, you'd need to build and maintain 5 separate API integrations.
With Fivetran's 750+ managed connectors, you connect sources in minutes.

### Fivetran Platform Connector

The Platform Connector is a special Fivetran connection that automatically lands
**pipeline metadata** into BigQuery:
- `log` — sync events, successes, failures, timestamps
- `connection` — inventory of connected data sources
- `table_lineage` — source-to-destination table mapping
- `incremental_mar` — rows synced per table per day
- `destination_table_change_event` — schema evolution events

This metadata is what enables **decision provenance** — tracing every piece of
shared memory back to its original source, sync time, and data quality status.

### Dataset: agent_memory.codebase_logs

Append-only event store written by Face 1 MoDeX MCP servers running inside
developer IDEs (Cursor, Antigravity). Each row is one event from a coding session.

| Column | Meaning | Shared Memory Role |
|--------|---------|-------------------|
| `session_id` | Unique coding session identifier | Groups events by session |
| `project_repo` | Repository URL (e.g. `github.com/team/api`) | Scopes memory to a project |
| `developer_id` | Developer or agent name | Who made the decision |
| `agent_tool` | AI tool used (Cursor, Antigravity, etc.) | Which agent was active |
| `event_type` | One of: session_start, user_prompt, tool_call, file_edit, decision, error, session_end | What happened |
| `file_path` | File affected (if applicable) | Code-grounded context |
| `summary` | Human-readable description of the event | The actual memory content |
| `payload_json` | Structured metadata (JSON) | Additional context |
| `created_at` | Timestamp of the event | When it happened |

### Dataset: modex_logs.modex_logs

MoDeX events mirrored to Google Sheets and synced into BigQuery via Fivetran
connector `stowed_register`. Contains `_fivetran_synced` provenance timestamps.

### Dataset: analytics.*

Structured tables produced by dbt transformations from codebase logs:
- `analytics.events_by_type` — event counts by type (decision, file_edit, error, etc.)
- `analytics.events_by_developer` — event distribution across developers/agents

### Dataset: fivetran_metadata_*

Pipeline metadata from the Platform Connector — used by the Lineage Agent to
answer provenance and freshness questions.

## Key Concepts

### Decision Provenance
The ability to trace any piece of team knowledge back to its source:
- Which data source it came from (GitHub PR, Google Sheet, Jira ticket)
- When it was synced into shared memory (`_fivetran_synced`)
- Whether the source data is still fresh or stale
- The full lineage chain: source → Fivetran → BigQuery → agent answer

### Memory Freshness
How current the team's shared memory is. Determined by:
- `_fivetran_synced` timestamps on data rows
- Last successful sync time per connection
- Sync frequency configuration (how often Fivetran pulls new data)

### Schema Drift
When the structure of source data changes (new columns, renamed fields).
Fivetran detects this automatically and records it as change events in the
Platform Connector metadata. MoDeX agents can report on schema drift to
alert the team about structural changes in their shared memory.

### Guardian Governance
All write operations in MoDeX require explicit human approval:
- Syncing new data sources (pulls real code and team communications)
- Running transformations (reshapes shared memory)
- Exporting reports (shares team context externally)
This ensures sensitive engineering decisions aren't leaked without consent.

## MoDeX Agent Team

| Agent | Role | What It Does |
|-------|------|-------------|
| **Orchestrator** | Mission Control | Plans multi-step missions, delegates to specialists |
| **Ingestion Agent** | Data Source Connector | Syncs engineering data via Fivetran MCP |
| **Knowledge Agent** | Shared Memory Engine | Queries BigQuery + RAG for team decisions |
| **Lineage Agent** | Decision Provenance | Traces data freshness, lineage, change history |
| **Transformation Agent** | Knowledge Structurer | Runs dbt to structure raw data into decision records |
| **Action Agent** | Team Broadcaster | Pushes reports to GCS, Sheets, webhooks |
| **Guardian Agent** | Access Governor | Human-in-the-loop write approval |

## How to Answer Questions

- For "what decisions / who worked on / count / list" → query BigQuery shared memory.
- For "is the memory fresh / when was last sync / what changed" → that's the Lineage Agent.
- For "what does this term/concept mean / how does MoDeX work" → use this knowledge base.
- For "push a report / alert the team / export" → that's the Action Agent (needs Guardian approval).
