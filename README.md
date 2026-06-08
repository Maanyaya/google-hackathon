# MoDeX — Memory of Codex

> **Shared reasoning memory for engineering teams using AI coding agents.**

15 developers. 15 AI coding agents. Zero shared context. **MoDeX changes that.**

---

## The Problem

Every developer on your team uses an AI coding agent — Cursor, Antigravity, Windsurf. Each agent starts from scratch every session. When Developer A decides *"we're using PostgreSQL, not MongoDB"* — Developer B's agent has no idea. It spends an hour exploring MongoDB.

**No tool today records WHY engineering decisions were made.**

| Tool | What It Records | What It Misses |
|------|----------------|----------------|
| Git | What changed | WHY the decision was made |
| Jira | What was assigned | The reasoning behind implementation choices |
| Slack | What was said | Not structured, not queryable by agents |
| Confluence | Documents | Stale within days, never connected to code |
| AI Agent Sessions | Per-session context | Dies when the conversation ends |

MoDeX captures the reasoning behind engineering decisions — code-grounded, verifiable, and shared across every agent on the team.

---

## How It Works

```
┌──────────────────────────────────────────┐
│     Individual AI Coding Agents          │
│  Cursor · Antigravity · Windsurf · ...   │
└────────┬─────────────┬───────────────────┘
         │  MCP Protocol (read/write)  │
         ▼             ▼               ▼
┌──────────────────────────────────────────┐
│         MoDeX Agent Team (7 agents)      │
│                                          │
│  🧠 Mission Control (Orchestrator)       │
│  📡 Data Source Connector (Fivetran MCP) │
│  🔍 Shared Memory Engine (BigQuery+RAG)  │
│  🔗 Decision Provenance (Lineage)        │
│  ⚙️ Knowledge Structurer (dbt)           │
│  📢 Team Broadcaster (Actions)           │
│  🛡️ Access Governor (Guardian)           │
└────────┬─────────────┬───────────────────┘
         │             │
         ▼             ▼
┌──────────────┐ ┌─────────────────┐
│ Fivetran MCP │ │ BigQuery + RAG  │
│ (pipeline    │ │ (shared memory  │
│  operations) │ │  warehouse)     │
└──────┬───────┘ └─────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ Fivetran Connectors (750+)      │
│ GitHub · Sheets · Jira · Slack  │
│ Notion · and 750+ more          │
└──────────────────────────────────┘
```

### Fivetran: The Data Backbone

Without Fivetran, you'd build and maintain 5+ separate API integrations. With Fivetran's 750+ managed connectors, you connect engineering data sources in minutes:

- **GitHub** → commits, PRs, reviews, issues
- **Google Sheets** → decision logs, team notes, project tracking
- **Jira** → tickets, decisions, sprint data
- **Slack** → conversations, threads, context
- **+ 750 more** → any data source your team uses

Fivetran MCP lets the agent team **operate** these pipelines — check health, trigger syncs, monitor freshness — not just read from them.

---

## Architecture

| Agent | Role | Tools |
|-------|------|-------|
| **Mission Control** | Plans missions, delegates, summarizes | Sub-agent delegation |
| **Data Source Connector** | Syncs engineering data via Fivetran | Fivetran MCP (11 tools) |
| **Shared Memory Engine** | Queries decisions + knowledge | BigQuery SQL + Vertex AI RAG |
| **Decision Provenance** | Traces data freshness & lineage | Platform Connector metadata |
| **Knowledge Structurer** | Structures raw data via dbt | Fivetran Transformations |
| **Team Broadcaster** | Pushes reports & alerts | GCS + Sheets + Webhooks |
| **Access Governor** | Human-in-the-loop governance | Approve/deny writes |

---

## Example Mission

> *"What architecture decisions has the team made this week? Is our data fresh? Export a summary for the standup."*

**Flow:**
1. **Mission Control** → plans 4 steps
2. **Data Source Connector** → Fivetran MCP → confirms data sources are synced and fresh
3. **Shared Memory Engine** → BigQuery → queries team decision records
4. **Decision Provenance** → traces each decision back to its source and sync time
5. User approves export → **Access Governor** → approves → **Team Broadcaster** → pushes report to GCS

---

## Live Deployment ✅

| Item | Value |
|------|-------|
| **Agent Runtime** | Vertex AI Agent Engine (asia-south1) |
| **Cloud Run** | https://agentic-data-platform-979112189932.asia-south1.run.app |
| **Web UI** | https://agentic-data-platform-979112189932.asia-south1.run.app/dev-ui |
| **Dashboard** | https://agentic-data-platform-979112189932.asia-south1.run.app/dashboard/ |
| **GCP Project** | `gen-lang-client-0795401430` |
| **Region** | `asia-south1` |

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Agent Framework | Google ADK (Agent Development Kit) |
| LLM | Gemini (via Vertex AI) |
| Pipeline Operations | Fivetran MCP Server (11 tools) |
| Data Warehouse | BigQuery |
| Semantic Search | Vertex AI RAG Engine (serverless) |
| Transformations | Fivetran Transformations for dbt Core |
| Deployment | Agent Runtime + Cloud Run |
| Governance | Guardian Agent (human-in-the-loop) |
| Protocol | A2A (Agent-to-Agent) |

---

## Project Layout

```
app/
  agent.py          # Mission Control (Orchestrator) + App
  specialists.py    # 6 specialist agents
  tools.py          # BigQuery + Fivetran + RAG + transformation tools
  fivetran_mcp.py   # Fivetran MCP client
  action_tools.py   # Team Broadcaster tools (GCS, Sheets, webhooks)
  dashboard_api.py  # Dashboard API + agent topology
  config.py         # Runtime configuration
  agent.json        # A2A agent card
knowledge/
  data_dictionary.md  # MoDeX knowledge base (indexed into RAG)
frontend/
  src/              # MoDeX Command Center dashboard
scripts/
  run_mission.py    # End-to-end smoke test
  provision_rag.py  # Create Vertex AI RAG corpus
tests/
  eval/             # Agent evaluation dataset
```

---

## Quick Start

```powershell
cd agentic-data-platform
agents-cli install

# Run a mission locally
uv run python scripts/run_mission.py

# Deploy to Agent Runtime
agents-cli deploy --project gen-lang-client-0795401430 --region asia-south1
```

---

## Hackathon

**Google Cloud Rapid Agent Hackathon** — Fivetran Track
- **Deadline:** June 11, 2026
- **Track:** Fivetran
- **Team:** Solo (Gagan Tak)

---

*MoDeX: because AI coding agents should share context, not start from scratch.*
