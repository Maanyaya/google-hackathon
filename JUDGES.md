# MoDeX — Judge & evaluator guide

**What MoDeX is:** An MCP superpower that gives AI coding agents a shared, persistent memory — so when a second agent picks up a codebase, it starts exactly where the first one left off, not from a blank slate.

**The two faces you are evaluating:**

| | Face 1 — Developer-Edge MCP | Face 2 — Central Memory Guide |
|---|---|---|
| **What it is** | Hooks + MCP server that auto-captures every IDE event | ADK agent (Gemini 2.5) deployed on Cloud Run |
| **What it does** | Writes every prompt, response, decision, file edit to BigQuery + Google Sheet | Answers memory questions, operates Fivetran, governs writes |
| **Where to test** | Install MCP (5 min, steps below) | Dashboard → Ask Face 2 (no install) |

---

## Built with (DevPost checklist)

| Layer | Technology | Role |
|-------|-----------|------|
| **Core AI** | Gemini 2.5 Flash (Vertex AI) | All agent reasoning — multi-step missions, citations |
| **Agent framework** | Google ADK (Agent Dev Kit) | Multi-agent orchestration: Mission Control + 3 specialists |
| **Deployment** | Google Cloud Run (asia-south1) | Both faces served from one serverless revision |
| **Ground-truth store** | Google BigQuery (`agent_memory.codebase_logs`) | Append-only log; Face 2 queries this first |
| **Warehouse** | Google BigQuery (`modex_logs.modex_logs`) | Fivetran destination — warehouse copy for reporting |
| **Secrets** | Google Secret Manager | Fivetran API key + secret — never in env vars |
| **Partner superpower** | **Fivetran MCP** (`fivetran-mcp`) | Pipeline operations live inside the agent conversation |
| **Data movement** | Fivetran — 3 connectors | Google Sheets → BQ, GitHub → BQ, Platform Connector → BQ |

---

## Fivetran integrations (the partner story)

| Connector | ID | Source | Destination | Why it matters |
|-----------|-----|--------|-------------|----------------|
| MoDeX Logs | `stowed_register` | Google Sheets · MoDex_Logs tab | `modex_logs.modex_logs` (BigQuery) | Every IDE session → queryable warehouse table |
| GitHub PRs | `solve_unhurt` | GitHub · PRs + reviews | `github.*` tables (BigQuery) | Grounds decisions in code review history |
| Platform Connector ★ | `elemental_apparel` | Fivetran Platform | Pipeline metadata + lineage | **Lineage + trust** — Face 2 reports freshness, schema drift |

★ The Platform Connector is the **differentiator** — Face 2 calls `get_connector_lineage` and answers questions about *data trust*, not just data content.

**Fivetran MCP tools visible in agent trace:**
- `list_connections` — all connector statuses
- `get_connection_details` — schema, sync history, errors
- `sync_connection` — trigger resync (Guardian-gated, user approves)
- `get_connector_lineage` — OpenLineage metadata from Platform Connector

---

## Test Face 2 right now (no install needed)

Open the dashboard: **https://agentic-data-platform-979112189932.asia-south1.run.app/dashboard/**

Click **Ask Face 2** and try these prompts — in this order for the best story:

### Mission 1 — Hydrate me
```
Hydrate me on github.com/Maanyaya/google-hackathon
```
**What you'll see:** Face 2 reads the latest `context_compressed` row from BigQuery, returns a full briefing: decisions made, approaches rejected, files in flight, the last user request, and the last agent action. This is exactly what Agent B receives before starting work.

### Mission 2 — Why was this chosen?
```
Why was python.exe chosen over a .cmd wrapper for the Cursor hooks?
```
**What you'll see:** Face 2 cites a specific `decision` event from a prior coding session, cross-referenced with any relevant GitHub PR reviews synced by Fivetran (`solve_unhurt` connector → `github.pull_request_review` table).

### Mission 3 — Pipeline trust (live Fivetran MCP)
```
What is the current sync status of the MoDeX logs pipeline? Check the Platform Connector metadata for freshness and lineage.
```
**What you'll see:** Face 2 calls the Fivetran MCP live — `list_connections` + `get_connector_lineage` — returns connector status for `stowed_register`, last sync time, and lineage metadata from the Platform Connector (`elemental_apparel`). This is the differentiator: not just "is it synced?" but "what changed, what's the lineage, is the data trustworthy?"

### Mission 4 — Trigger resync with Guardian approval
```
Check the stowed_register connector health. If the MoDeX logs are stale, request approval to trigger a resync.
```
**What you'll see:** Face 2 calls `get_connection_details` on `stowed_register`, reports staleness, then calls `sync_connection` — but only after the Guardian agent asks for your approval. This shows the governed write pattern (user stays in control).

---

## Test Face 1 MCP (5 minutes)

### Credentials — two keys for the handoff demo

MoDeX shared memory is proven when **two different developer IDs** log to the **same repo slug**:

| Key | `developer_id` | Use as |
|-----|----------------|--------|
| `msk-7079ba3cdcf863affee3bbdea41b0485` | `judge` | Agent A — writes decisions + compresses |
| `msk-1681c9a2c379d01e755fd0eb99de35ec` | `judge2` | Agent B — hydrates and continues |

| Field | Value |
|-------|--------|
| **Service URL** | `https://agentic-data-platform-979112189932.asia-south1.run.app` |
| **Judge API key (Agent A)** | `msk-7079ba3cdcf863affee3bbdea41b0485` |
| **Judge 2 API key (Agent B)** | `msk-1681c9a2c379d01e755fd0eb99de35ec` |
| **Demo repo** | `github.com/demo/api-service` |
| **Copy/paste MCP config** | [docs/JUDGE_MCP_CREDENTIALS.md](docs/JUDGE_MCP_CREDENTIALS.md) |

Verify key works:
```bash
curl -H "Authorization: Bearer msk-7079ba3cdcf863affee3bbdea41b0485" \
  https://agentic-data-platform-979112189932.asia-south1.run.app/api/v1/whoami
# → {"status":"ok","developer_id":"judge"}
```

### Install (one-time)

```bash
pip install mcp
curl -o remote_client.py \
  https://raw.githubusercontent.com/Maanyaya/google-hackathon/main/modex_mcp/remote_client.py
```

**Cursor** — paste into `~/.cursor/mcp.json` (Windows: `%USERPROFILE%\.cursor\mcp.json`):

```json
{
  "mcpServers": {
    "modex-memory": {
      "command": "python",
      "args": ["/ABSOLUTE/PATH/TO/remote_client.py"],
      "env": {
        "MODEX_API_URL": "https://agentic-data-platform-979112189932.asia-south1.run.app",
        "MODEX_API_KEY": "msk-7079ba3cdcf863affee3bbdea41b0485",
        "MODEX_DEVELOPER_ID": "judge"
      }
    }
  }
}
```

Restart Cursor → Settings → MCP → `modex-memory` should show: `load_context`, `append_codebase_log`, `log_decision`, `compress_context`.

### Test prompts (ask your coding agent)

```
Call load_context for github.com/demo/api-service and tell me the decisions and rejected approaches.
```
```
Log a decision: "Judge verified MoDeX agent-to-agent handoff" for github.com/demo/api-service
```

Refresh the dashboard **Context pack** — your event appears within seconds.

---

## The handoff story (what to look for on the dashboard)

```
AGENT A works on the codebase (Cursor, Windows)
  → every prompt + response + file edit captured automatically
  → session ends → context_compressed row written to BigQuery + Google Sheet
  → Sheet column "session_summary":
      "In this session, gagantak00@gmail.com worked on github.com/Maanyaya/
       google-hackathon using cursor (47 events). 3 decisions made: invoke
       hooks via python.exe; decode UTF-16LE stdin; use conversation_id as
       session key. 4 files modified: hook_runner.py (6 edits)... Last user
       request: 'add setup instructions to readme'."

         ↓  Fivetran syncs the sheet  ↓

AGENT B starts (Antigravity, Mac, different developer)
  → calls load_context() via MCP
  → receives the exact same briefing from BigQuery
  → continues exactly where Agent A left off
  → zero cold start
```

The `session_summary` column in the sheet is a plain-English paragraph — open the sheet and you can read it without knowing the system at all. The `transcript_md` column is the full briefing Agent B injects as system context.

**Google Sheet (open to inspect):** https://docs.google.com/spreadsheets/d/1NKxRyKBBgBzETtaaPO_gPC8vdM1i4vtt5yxrq6iCRck

---

## What Fivetran does here

| Connector | ID | What it syncs | Why it matters |
|-----------|-----|--------------|----------------|
| MoDeX logs (Google Sheets) | `stowed_register` | `MoDex_Logs` tab → `modex_logs.modex_logs` in BigQuery | Turns every IDE session's memory into a queryable warehouse table |
| GitHub | `solve_unhurt` | PRs + reviews → `github.*` tables | Grounds decisions in code review history, not just agent claims |
| Platform Connector | `elemental_apparel` | Pipeline metadata + lineage | Face 2 reports freshness and health live |

Face 2 calls the Fivetran MCP server directly — it can trigger syncs, report health, and read lineage within a conversation.

---

## Architecture in one diagram

```
Developer types in Cursor
        │
        ▼  hook_runner.py (UTF-16LE decoded, all event types)
        │
        ├──► BigQuery: agent_memory.codebase_logs  (ground truth, append-only)
        │
        └──► Google Sheet: MoDex_Logs tab
                 │  columns: summary · session_summary · context_json · transcript_md
                 │
                 ▼  Fivetran (stowed_register)
                 │
                 └──► BigQuery: modex_logs.modex_logs  (warehouse, for other agents)

Face 2 (ADK + Gemini 2.5, Cloud Run)
  ├── memory_agent    → get_team_context() fuses codebase_logs + GitHub PRs
  ├── pipeline_agent  → Fivetran MCP: sync, health, lineage
  └── action_agent    → governed writes (export, approve)
```

---

## Links

| Resource | URL |
|----------|-----|
| Dashboard | https://agentic-data-platform-979112189932.asia-south1.run.app/dashboard/ |
| GitHub | https://github.com/Maanyaya/google-hackathon |
| API health | …/api/v1/health |
| Architecture README | [README.md](README.md) |
| Configuration (both faces) | [CONFIGURATION.md](CONFIGURATION.md) |

---

*Face 1 proves capture. Face 2 proves the bus is answerable. Fivetran keeps it fresh.*
