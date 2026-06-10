# MoDeX — Memory of Codex

> **The problem:** When two AI coding agents work on the same codebase, the second one starts cold. It doesn't know what the first decided, what was tried and rejected, or what the user was actually asking for. Every handoff is a blank slate.
>
> **MoDeX solves this:** it gives coding agents a shared, persistent memory — captured automatically, stored in BigQuery, surfaced through a central memory agent, and kept fresh by Fivetran.

**Live demo:** https://agentic-data-platform-979112189932.asia-south1.run.app/dashboard/  
**GitHub:** https://github.com/Maanyaya/google-hackathon  
**New repo? Set up MCP here (step-by-step):** [docs/NEW_REPO_MCP_SETUP.md](docs/NEW_REPO_MCP_SETUP.md)  
**Judge credentials + 5-min test:** [JUDGES.md](JUDGES.md)  
**Full configuration reference (both faces):** [CONFIGURATION.md](CONFIGURATION.md)

---

## The core idea

MoDeX is an **MCP superpower for coding agents**. Any agent — Cursor, Antigravity, Windsurf — gets two new abilities:

1. **Remember everything** — every decision, every user message, every file edited, every approach rejected is captured automatically as the agent works, without the developer doing anything.
2. **Resume from any agent** — when a different agent (or the same agent on a different machine) starts, it receives a full context briefing: what was decided, what failed, what is in flight, and what the user last asked.

The memory lives in **Google BigQuery** (the ground truth) and is mirrored to a **Google Sheet** so Fivetran can sync it across the warehouse. This means the memory is not trapped in one IDE or one machine — it is a shared bus the entire team reads and writes.

---

## Two faces, one memory bus

```
┌──────────────────────────────────────────────────────────────────────┐
│  FACE 1  ·  Developer-Edge Capture (MCP + hooks)                     │
│                                                                      │
│  What it does: automatically captures every IDE event into memory    │
│                                                                      │
│  Cursor  ──► beforeSubmitPrompt hook  ──► user_prompt event          │
│          ──► afterAgentResponse hook  ──► agent_response event       │
│          ──► afterFileEdit hook       ──► file_edit event            │
│          ──► postToolUse hook         ──► tool_call event            │
│          ──► stop hook                ──► context_compressed handoff │
│                                                                      │
│  MCP tools (manual):                                                 │
│    load_context()           ← Agent B reads prior session            │
│    append_codebase_log()    ← explicit event write                   │
│    log_decision()           ← record a significant choice            │
│    compress_context()       ← force a handoff pack now               │
└────────────────────────────────┬─────────────────────────────────────┘
                                 │  writes via hosted API (URL + key)
                                 │  OR local BigQuery SA credentials
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│  MEMORY BUS  ·  BigQuery + Google Sheet + Fivetran                   │
│                                                                      │
│  Primary store:  agent_memory.codebase_logs  (BigQuery, append-only) │
│  Sheet mirror:   MoDex_Logs tab  (14 cols, Fivetran source)          │
│  Fivetran sync:  stowed_register  →  modex_logs.modex_logs  (BQ)     │
│  GitHub sync:    PRs + reviews  →  cross-reference with decisions    │
│                                                                      │
│  Key columns in every row:                                           │
│    session_id, developer_id, agent_tool, project_repo, event_type   │
│    summary (plain-English), session_summary (paragraph), context_json│
│    transcript_md (full briefing for the next agent)                  │
└─────────────────────────┬──────────────────────────────┬─────────────┘
                          │                              │
           ┌──────────────▼──────────────┐   ┌──────────▼───────────────┐
           │  FACE 2  ·  Central Memory  │   │  DASHBOARD  ·  Live UI   │
           │  Guide  (ADK + Gemini 2.5)  │   │                          │
           │                             │   │  Context pack            │
           │  Three jobs:                │   │  Decision timeline       │
           │  1. Memory answers          │   │  Pipeline health         │
           │     (decisions, rejected,   │   │  Setup & judge docs      │
           │      PRs cited, hydrate)    │   │                          │
           │  2. Fivetran operations     │   └──────────────────────────┘
           │     (sync, health, lineage) │
           │  3. Governed writes         │
           │     (export, approve)       │
           └─────────────────────────────┘
```

---

## Face 1 — How the memory capture works

### The capture pipeline (step by step)

```
Developer types a message in Cursor
         │
         ▼  beforeSubmitPrompt hook fires
         │  → hook_runner.py reads the JSON payload (UTF-16LE decoded on Windows)
         │  → appends user_prompt event to BigQuery + mirrors to Google Sheet
         │
Agent responds
         │
         ▼  afterAgentResponse hook fires
         │  → agent_response event written (full text in payload_json)
         │
Agent uses tools (Read, Shell, Write, MCP…)
         │
         ▼  postToolUse / afterShellExecution / afterMCPExecution hooks fire
         │  → tool_call events written (tool name + full input captured)
         │
Agent edits a file
         │
         ▼  afterFileEdit hook fires (skips empty/no-path edits)
         │  → file_edit event (repo-relative path, edit count)
         │
Agent turn finishes
         │
         ▼  stop hook fires
         │  → save_compressed_context() runs deterministically:
         │     reads all events for this session from BigQuery
         │     builds transcript[], decisions[], files[], errors[], rejected[]
         │     generates session_summary (plain-English paragraph)
         │     writes ONE context_compressed row to BigQuery
         │     mirrors it to Google Sheet (context_json + transcript_md columns)
         │
Developer closes chat
         │
         ▼  sessionEnd hook fires
         │  → session_end event
         │  → writes .agents/modex-transcript.md (local hydration file)
```

### What lands in the Google Sheet (MoDex_Logs tab)

Every row is one event. Most rows are the raw capture events. The important one
is the `context_compressed` row that is written when a session ends or when
`handoff snapshot` is called:

| Column | Example value for `context_compressed` |
|--------|----------------------------------------|
| `event_type` | `context_compressed` |
| `summary` | `modex.context.v2 · 12 turns · 3 decisions · 4 files · 18 events` |
| `session_summary` | `In this session, gagantak00@gmail.com worked on github.com/Maanyaya/google-hackathon using cursor. 3 engineering decisions were made: invoke hooks via python.exe, use conversation_id as session key, decode UTF-16LE stdin. 4 files were modified: hook_runner.py (6 edits), hooks.json (2 edits)...` |
| `context_json` | Full JSON: transcript[], decisions[], files[], errors[] |
| `transcript_md` | Briefing + full turn-by-turn markdown — paste this into any agent |

When **Agent B** calls `load_context` or runs `handoff hydrate`, it reads the
latest `context_compressed` row and injects the `transcript_md` as its system
context. The second agent starts exactly where the first one left off.

### Deterministic handoff CLI (works even if hooks fail)

```bash
# Agent A — snapshot current memory to BQ + Sheet
python -m modex_mcp.handoff snapshot --repo github.com/Maanyaya/google-hackathon

# Agent B (any IDE, any OS, any machine) — load the same context
python -m modex_mcp.handoff hydrate  --repo github.com/Maanyaya/google-hackathon
```

---

## Face 2 — What the Central Memory Guide does

Face 2 is a **Google ADK agent** (Gemini 2.5 Flash) deployed on Cloud Run. It
has three specific, distinct jobs — it is not a generic chatbot.

### Job 1: Answer memory questions with provenance

The agent calls `get_team_context(project_repo)` which fuses:
- **Face 1 session logs** (`agent_memory.codebase_logs`) — every decision and
  rejected approach captured from IDE sessions
- **GitHub PRs + reviews** synced by Fivetran — the reviewer reasoning that
  backs architectural choices

The answer always includes: **what was decided**, **what was explicitly rejected**
(so no agent ever redoes a dead-end), **which PR review backs this choice**, and
**how fresh the data is** (`_fivetran_synced` timestamp).

Example prompts the judge can try on the dashboard:
- *"Hydrate me"* → delivers the full session context briefing
- *"Why was MongoDB rejected?"* → cites the session decision and the PR review
- *"What files are in flight?"* → from the compressed memory pack

### Job 2: Operate Fivetran connectors live

The agent calls Fivetran MCP tools directly:
- List connectors and their sync status
- Trigger a manual sync of `stowed_register` (the MoDeX logs connector)
- Report pipeline health and data freshness

This is the **Fivetran superpower** — the memory agent can keep its own data
pipeline healthy without leaving the conversation.

### Job 3: Governed actions (human-in-the-loop)

Actions that modify state (export to GCS, write to Sheets) are gated behind
explicit user approval. The agent proposes, the user approves, the action runs.

---

## Fivetran — the synchronization backbone

Fivetran does three things in MoDeX:

| Connector | What it syncs | Why it matters |
|-----------|--------------|----------------|
| **stowed_register** (Google Sheets) | `MoDex_Logs` tab → `modex_logs.modex_logs` in BigQuery | Every IDE session's memory becomes queryable in the warehouse; other agents and Face 2 read from here |
| **GitHub connector** | PRs, reviews, commits → `github.*` tables | Grounds decisions in actual code review history, not just agent assertions |
| **Platform Connector** | Pipeline metadata, lineage, freshness | Face 2 can report data freshness and connector health live |

The **MCP superpower**: Face 2 uses the Fivetran MCP server to operate these
connectors live — triggering syncs, checking health, reading lineage — all from
within a conversation with a coding agent.

---

## The agent-to-agent handoff (the core demo)

This is the story MoDeX tells:

```
AGENT A (Cursor, Gagan, Windows):
  Works on the codebase. Every prompt, response, decision, file edit
  is captured automatically by hooks → BigQuery + Google Sheet.
  When done: hooks fire `stop` → context_compressed row written.
  Sheet column transcript_md now holds a complete briefing.

         ↓  Google Sheet  ↓  Fivetran  ↓  BigQuery

AGENT B (Antigravity, Maanya, Mac):
  Opens the repo. Calls load_context() via MCP.
  Receives the SAME context_compressed row from BigQuery.
  System context injected: decisions, rejected approaches,
  files in flight, last user question, last agent response.
  Continues exactly where Agent A left off. Zero cold start.
```

**The spreadsheet is not just logging — it is the handoff medium.** The
`transcript_md` cell in the `context_compressed` row is what Agent B's system
context is built from.

---

## Project layout

```
agentic-data-platform/
├── app/
│   ├── agent.py              # Face 2 root agent (Central Memory Guide)
│   ├── specialists.py        # memory_agent · pipeline_agent · action_agent
│   ├── mcp_api.py            # Hosted Face 1 API (/api/v1, bearer-auth)
│   ├── dashboard_api.py      # Dashboard + /setup for judges
│   └── memory_graph.py       # Context pack builder (fuses BQ + Fivetran)
├── modex_mcp/
│   ├── hook_runner.py        # IDE hook handler (UTF-16 safe, all events)
│   ├── handoff.py            # Deterministic handoff CLI (snapshot/hydrate)
│   ├── context_compress.py   # Deterministic compression (no LLM)
│   ├── memory_store.py       # BQ + Sheet write/read
│   ├── remote_client.py      # Thin MCP client (URL + key only)
│   └── server.py             # Local MCP server (needs GCP)
├── .cursor/
│   ├── hooks.json            # Cursor hook definitions (direct python.exe)
│   └── modex.json            # Project config (repo, agent_tool)
├── .agents/
│   ├── hooks.json            # Antigravity hook definitions
│   └── modex.json            # Project config for Antigravity
├── frontend/                 # Dashboard React app
├── scripts/
│   ├── verify_pipeline_rigorous.py  # End-to-end pipeline proof
│   └── demo_missions.py             # Face 2 demo missions
└── tests/unit/
    ├── test_hook_runner.py
    └── test_context_compress.py
```

---

## For judges — test it now

| | |
|---|---|
| **Dashboard (Face 2, no install)** | https://agentic-data-platform-979112189932.asia-south1.run.app/dashboard/ |
| **Judge API key (Face 1 MCP)** | `msk-7079ba3cdcf863affee3bbdea41b0485` |
| **Judge MCP credentials (copy/paste)** | [docs/JUDGE_MCP_CREDENTIALS.md](docs/JUDGE_MCP_CREDENTIALS.md) |
| **Full setup guide** | [JUDGES.md](JUDGES.md) |

---

## Setup & run (full)

### Prerequisites

| Need | Notes |
|------|-------|
| Python 3.12+ | `.venv` in `agentic-data-platform/` |
| GCP project | `gen-lang-client-0795401430`; BigQuery + Vertex AI |
| GCP credentials | service-account JSON or `gcloud auth application-default login` |
| Fivetran (optional) | only for live connector ops |

### Install

```powershell
git clone https://github.com/Maanyaya/google-hackathon.git
cd google-hackathon\agentic-data-platform
uv sync          # or: python -m venv .venv && .venv\Scripts\pip install -e .
```

### Environment (.env)

```ini
GOOGLE_CLOUD_PROJECT=gen-lang-client-0795401430
GOOGLE_APPLICATION_CREDENTIALS=D:\...\gen-lang-client-0795401430-...json
MODEX_MEMORY_SHEET_ID=1NKxRyKBBgBzETtaaPO_gPC8vdM1i4vtt5yxrq6iCRck
MODEX_LOG_SHEET_RANGE=MoDex_Logs!A1
FIVETRAN_API_KEY=...
FIVETRAN_API_SECRET=...
```

### Create BigQuery memory store

```powershell
.venv\Scripts\python.exe scripts\setup_agent_memory.py
```

### Google Sheet header (MoDex_Logs tab, row 1, columns A–O)

```
event_id, session_id, developer_id, agent_tool, project_repo, event_type, file_path, commit_sha, summary, payload_json, parent_event_id, created_at, context_json, transcript_md, session_summary
```

### Enable Cursor hooks

1. Open workspace root in Cursor (the folder with `.cursor/`)
2. Edit `.cursor/modex.json` → set `project_repo` to your repo
3. Restart Cursor → Settings → Hooks → confirm `modex_*` entries appear
4. Send a message → check `.agents/modex-hook-debug.log` for `"parsed": true`

> **Windows:** hooks must call `python.exe` directly. Never route through `.cmd`/`.bat` — this drops stdin. Cursor pipes UTF-16LE; the runner decodes automatically.

### Verify end to end

```powershell
# Unit tests
.venv\Scripts\python.exe -m pytest tests\unit\ -q

# Full rigorous pipeline proof (UTF-16 hooks → BQ → Sheet → hydrate)
.venv\Scripts\python.exe scripts\verify_pipeline_rigorous.py
```

### Handoff CLI

```powershell
.venv\Scripts\python.exe -m modex_mcp.handoff snapshot --repo github.com/Maanyaya/google-hackathon
.venv\Scripts\python.exe -m modex_mcp.handoff hydrate  --repo github.com/Maanyaya/google-hackathon
.venv\Scripts\python.exe -m modex_mcp.handoff status   --repo github.com/Maanyaya/google-hackathon
```

---

**Google Cloud Rapid Agent Hackathon — Fivetran Track — June 2026**
