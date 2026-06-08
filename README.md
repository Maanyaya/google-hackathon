# MoDeX — Memory of Codex

> **Shared reasoning memory for AI coding teams.** Git remembers *what* changed. MoDeX remembers *why*.

**Live dashboard:** https://agentic-data-platform-979112189932.asia-south1.run.app/dashboard/  
**Judge setup (MCP + architecture):** [JUDGES.md](JUDGES.md) · dashboard **Setup** section

---

## Two faces, one memory bus

```
┌─────────────────────────────────────────────────────────────────┐
│  FACE 1 · Developer Edge (MCP)                                  │
│  Cursor · Antigravity · Windsurf                                │
│  load_context() · append_codebase_log()                         │
└────────────────────────────┬────────────────────────────────────┘
                             │  hosted API (URL + API key)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  MEMORY BUS · Fivetran + BigQuery                               │
│  agent_memory.codebase_logs · GitHub PRs · Sheet mirror         │
│  Platform Connector metadata · _fivetran_synced provenance      │
└────────────────────────────┬────────────────────────────────────┘
                             │
         ┌───────────────────┴───────────────────┐
         ▼                                       ▼
┌─────────────────────┐              ┌──────────────────────────┐
│  FACE 2 · Central   │              │  Dashboard (this UI)     │
│  Memory Guide       │              │  Context pack · pipelines│
│  Memory answers     │              │  decisions · Setup docs  │
│  Fivetran ops       │              └──────────────────────────┘
│  Governed actions   │
└─────────────────────┘
```

| Face | Proved | Job |
|------|--------|-----|
| **Face 1 (MCP)** | Coding agents capture reasoning | Write/read session memory from any IDE |
| **Bus** | Fivetran syncs sources | Centralized, cited, queryable memory |
| **Face 2** | Bus is answerable | Answer what/why/rejected + operate Fivetran |

---

## For judges — test Face 1 MCP in 5 minutes

**No GCP credentials needed.** Use the hosted API + judge key.

| | |
|---|---|
| **URL** | `https://agentic-data-platform-979112189932.asia-south1.run.app` |
| **Judge API key** | `msk-7079ba3cdcf863affee3bbdea41b0485` |
| **Verify** | `curl -H "Authorization: Bearer msk-7079ba3cdcf863affee3bbdea41b0485" …/api/v1/whoami` |

1. `pip install mcp`
2. Download [`modex_mcp/remote_client.py`](modex_mcp/remote_client.py)
3. Copy [`docs/mcp-cursor-judge.json`](docs/mcp-cursor-judge.json) → `~/.cursor/mcp.json` (fix path)
4. Restart Cursor → ask agent: `load_context for github.com/demo/api-service`

Full guide: **[JUDGES.md](JUDGES.md)**

---

## For judges — test Face 2 (no install)

Open the [dashboard](https://agentic-data-platform-979112189932.asia-south1.run.app/dashboard/) → **Ask Face 2**:

1. **Hydrate me** — cited memory answer (session + GitHub PRs)
2. **Why this stack?** — PostgreSQL vs MongoDB provenance
3. **Pipeline health** — live Fivetran MCP

---

## Face 2 — three answerable jobs

1. **Memory answers** — `get_team_context`, decisions, rejected approaches, PR citations
2. **Fivetran operations** — list/sync connectors, lineage, freshness (`stowed_register`, GitHub)
3. **Governed actions** — export to GCS/Sheets after explicit approval

Built with **Google ADK + Gemini 2.5 Flash** on Cloud Run.

---

## Fivetran integration

| Connector | Role |
|-----------|------|
| **MoDeX logs** (`stowed_register`) | Sheet → `modex_logs` BigQuery table |
| **GitHub** | PRs + reviews → cross-reference with session decisions |
| **Platform Connector** | Lineage, freshness, pipeline metadata |
| **Fivetran MCP** | Face 2 operates connections live (judge-visible) |

---

## Live deployment

| Item | Value |
|------|--------|
| **Cloud Run** | https://agentic-data-platform-979112189932.asia-south1.run.app |
| **Dashboard** | …/dashboard/ |
| **Dev UI (ADK)** | …/dev-ui |
| **GitHub** | https://github.com/Maanyaya/google-hackathon |
| **GCP Project** | `gen-lang-client-0795401430` |

---

## Project layout

```
app/
  agent.py           # Central Memory Guide (Face 2 root)
  specialists.py     # Memory Answers · Fivetran Ops · Governed Actions
  mcp_api.py         # Hosted Face 1 API (/api/v1)
  dashboard_api.py   # Dashboard + /setup for judges
  memory_graph.py    # Context pack builder
modex_mcp/
  remote_client.py   # Thin MCP client (URL + key only)
  server.py          # Local MCP (optional, needs GCP)
docs/
  mcp-cursor-judge.json
  mcp-antigravity-judge.json
JUDGES.md            # Judge credentials + architecture
frontend/            # Command Center dashboard
```

---

## Quick start (developers)

```powershell
cd agentic-data-platform
uv sync

# Verify Face 2 tools (no LLM)
uv run python scripts/face2_tools_smoke.py

# Verify demo missions on live Cloud Run
uv run python scripts/demo_missions.py

# Run Face 2 agent locally (needs Vertex AI)
uv run python scripts/run_mission.py "Hydrate me on github.com/demo/api-service"
```

---

## Hackathon

**Google Cloud Rapid Agent Hackathon** — Fivetran Track  
**Deadline:** June 11, 2026

---

*Face 1 proved capture. Face 2 proved the bus is answerable. Fivetran keeps it fresh.*
