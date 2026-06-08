# MoDeX — Hackathon Demo Script (3 minutes)

**Deadline:** June 11, 2026  
**Track:** Fivetran  
**Live URL:** https://agentic-data-platform-979112189932.asia-south1.run.app  
**GitHub:** https://github.com/Maanyaya/google-hackathon

---

## The One-Liner (10 sec)

> "MoDeX is shared reasoning memory for AI coding teams — when Developer A's Cursor agent picks PostgreSQL over MongoDB, Developer B's Antigravity agent knows why, backed by Fivetran pipelines and BigQuery."

---

## Demo Flow (2:50)

### Act 1 — The Problem (20 sec)

Show a slide or speak:

- 15 devs, 15 AI agents, zero shared context
- Git shows *what* changed, not *why*
- Every new session = cold start

### Act 2 — Face 1: Developer Edge in Cursor (45 sec)

1. Open **Cursor** with MoDeX MCP connected
2. Run: *"Load team context for github.com/demo/api-service"*
3. Show hydration: PostgreSQL decision, JWT auth, clock skew error
4. Append a decision: *"We chose Redis for session cache — rejected in-memory"*
5. Point out: writes go to `agent_memory.codebase_logs` + Sheet mirror

**Judge hook:** Face 1 = MCP in the IDE, real developer workflow.

### Act 3 — Fivetran Bus (30 sec)

1. Open **Command Center:** `/dashboard/`
2. Show **Fivetran Pipelines** card — `stowed_register` connector
3. Show **Memory Freshness** — Face 1 logs vs Fivetran-synced `modex_logs` with `_fivetran_synced`
4. Say: *"Same events, two paths — real-time BQ + Fivetran-proven sync time"*

**Judge hook:** Meaningful Fivetran MCP — not just reading data, operating pipelines.

### Act 4 — Face 2: 7-Agent Mission (60 sec)

In **Agent Mission Console** on dashboard, run:

> "What architecture decisions has the team made on github.com/demo/api-service? Is our MoDeX data fresh? Cite provenance."

Watch delegation:

| Agent | What it does |
|-------|--------------|
| **Mission Control** | Plans steps |
| **Shared Memory Engine** | Queries `codebase_logs` + `modex_logs` |
| **Decision Provenance** | Cites `_fivetran_synced` / `created_at` |
| **Data Source Connector** | Checks Fivetran sync status via MCP |

**Judge hook:** Multi-step, beyond chat, grounded answers with provenance.

### Act 5 — Governance + Close (15 sec)

> "Every write — sync, transform, export — goes through the Access Governor."

Optional: approve a sync or GCS export.

**Closing line:**

> "MoDeX: because AI coding agents should share context, not start from scratch."

---

## Quick Mission Buttons (dashboard)

Use these if live LLM is slow:

1. **Session handoff** — replays Cursor → Antigravity handoff story
2. **Pipeline health** — Fivetran MCP list connections
3. **Memory freshness** — compares Face 1 vs Fivetran bus
4. **Engineering decisions** — decision timeline with provenance

---

## DevPost Checklist

| Field | Value |
|-------|-------|
| **Project name** | MoDeX — Memory of Codex |
| **Tagline** | Shared reasoning memory for AI coding teams |
| **Track** | Fivetran |
| **Try it link** | Cloud Run URL above |
| **Source code** | GitHub repo above |
| **License** | Apache 2.0 |
| **Built with** | Google ADK, Gemini, Fivetran MCP, BigQuery, Vertex AI RAG, Cloud Run |

### What makes this win

1. **Novel problem** — reasoning memory gap in AI-assisted dev teams
2. **Two-face architecture** — IDE MCP (Face 1) + platform agents (Face 2)
3. **Deep Fivetran integration** — MCP ops, Platform Connector lineage, dbt transforms, Sheet sync bus
4. **Full Google stack** — ADK, Gemini, BigQuery, RAG, Cloud Run, Agent Runtime
5. **Governance** — Guardian human-in-the-loop on every write
6. **Live + reproducible** — hosted demo + public GitHub

---

## Pre-Recording Checklist

- [ ] Redeploy Cloud Run after latest dashboard restore (`agents-cli deploy`)
- [ ] Verify `/dashboard/` shows MoDeX branding + memory timeline
- [ ] Seed 1 fresh MCP log event before recording
- [ ] Trigger Fivetran sync on `stowed_register` if stale
- [ ] Test one mission in Dev UI or dashboard console
- [ ] Record 1080p, show Cursor + browser side by side

---

## Redeploy (after code changes)

```powershell
cd agentic-data-platform
cd frontend; npm run build; cd ..
agents-cli deploy --project gen-lang-client-0795401430 --region asia-south1
```
