# MoDeX — Implementation Plan (Hackathon Sprint)

> **Goal:** Win the Google Cloud Rapid Agent Hackathon — Fivetran Track  
> **Deadline:** June 11, 2026  
> **Today:** June 8, 2026 (3 days left)  
> **North star:** A judge can clone the repo, open the live URL, watch the demo video, and see the full loop — Cursor MCP → Fivetran → BigQuery → 7 agents → provenance.

---

## Executive Summary

MoDeX (**Memory of Codex**) is shared reasoning memory for AI coding teams. Two faces:

| Face | Who | What |
|------|-----|------|
| **Face 1** | Developers in Cursor/Antigravity | MCP writes session memory → BigQuery + Sheet mirror |
| **Face 2** | Team leads / judges | 7 ADK agents query, sync, trace lineage, govern writes |

**Winning angle:** No tool today records *why* engineering decisions were made across isolated AI agent sessions. MoDeX + Fivetran makes that queryable, syncable, and governable.

---

## Current State (June 8 — post dashboard restore)

### ✅ Done and working

| Component | Status | Evidence |
|-----------|--------|----------|
| Face 1 MCP (`modex_mcp/`) | Live | Cursor connected, 18+ events in `codebase_logs` |
| 7 ADK agents | Code complete | `app/agent.py` + `specialists.py` |
| Fivetran MCP tools | Wired | Ingestion agent, 11 MCP tools |
| BigQuery memory | Working | Tool smoke test passed |
| RAG + dbt + lineage | Configured | `.env.example`, agents wired |
| Guardian governance | Working | Session-state gate on writes |
| Dashboard API | Restored locally | `app/dashboard_api.py` — 15 endpoints |
| Command Center UI | Built locally | `frontend/dist/` from Vite build |
| Cloud Run (old deploy) | Live | Dashboard + Dev UI return 200 |
| Unit + tool tests | Passing | 5/5 unit, Face 2 smoke all green |
| Repo hygiene | Mostly done | LICENSE, metadata, `.env.example` |
| Demo script | Written | `SUBMISSION_DEMO.md` |

### ⚠️ In progress (uncommitted)

```
 M .cursor/mcp.json, .env.example, .gitignore, app/config.py, app/fast_api_app.py
 ?? SUBMISSION_DEMO.md, app/dashboard_api.py, frontend/, scripts/test_dashboard_api.py
```

### ❌ Not done yet

| Item | Blocker / note |
|------|----------------|
| Git push (dashboard restore) | Uncommitted changes |
| Cloud Run redeploy | Must match restored repo; `agents-cli deploy` |
| Local LLM mission (`run_mission.py`) | 403 on local SA — use Cloud Run Dev UI for demo |
| Demo video | Record June 10 |
| DevPost submission | Submit June 11 |
| IAM for local Vertex | Optional — Cloud Run app SA already has `aiplatform.user` |

---

## Phase 0 — Lock the story (30 min) ✅

**Objective:** One sentence judges remember.

> *"MoDeX gives every AI coding agent on your team the same shared context — decisions, rejections, and work-in-progress — powered by Fivetran pipelines into BigQuery."*

**Demo repo:** `github.com/demo/api-service`  
**Demo narrative:** Cursor agent chose PostgreSQL → Antigravity agent loads same context → no cold start.

No code changes. Use this in video + DevPost.

---

## Phase 1 — Ship the repo (2 hours) 🔴 TODAY

**Objective:** GitHub matches what judges see on Cloud Run.

### 1.1 Commit dashboard restore

Files to include:

- `app/dashboard_api.py`
- `app/fast_api_app.py` (router + static mount)
- `frontend/` (src + `dist/` — judges need reproducible Docker build)
- `scripts/test_dashboard_api.py`
- `SUBMISSION_DEMO.md`
- Config/security fixes (`.env.example`, `.gitignore`, `.cursor/mcp.json`)

Files to **exclude**:

- `.env`, SA key JSON, `node_modules/`, `.venv/`

### 1.2 Push to GitHub

```powershell
cd agentic-data-platform
git add app/dashboard_api.py app/fast_api_app.py frontend/ scripts/test_dashboard_api.py
git add SUBMISSION_DEMO.md .env.example .gitignore .cursor/mcp.json app/config.py
git commit -m "Restore MoDeX Command Center and align repo with live deployment"
git push origin main
```

### 1.3 Verify GitHub About section

- [ ] LICENSE visible (Apache 2.0)
- [ ] README renders with live URLs
- [ ] No secrets in any committed file

**Exit criteria:** Clone → `npm run build` in frontend → `docker build` succeeds.

---

## Phase 2 — Redeploy Cloud Run (1 hour) 🔴 TODAY

**Objective:** Live URL serves the restored MoDeX dashboard (memory timeline, MoDeX charts, 7 agents).

```powershell
cd agentic-data-platform/frontend
npm run build
cd ..
agents-cli deploy --project gen-lang-client-0795401430 --region asia-south1
```

### Post-deploy smoke

| URL | Expected |
|-----|----------|
| `/api/dashboard/overview` | `product_name: "MoDeX — Memory of Codex"`, `agent_count: 7` |
| `/api/dashboard/memory` | 18+ memories from `codebase_logs` |
| `/dashboard/` | MoDeX branding, memory timeline, agent topology |
| `/dev-ui/?app=app` | ADK playground loads |

**Exit criteria:** All four return 200 with MoDeX-branded content.

---

## Phase 3 — Validate the full loop (1 hour) 🟡 June 9

**Objective:** Every demo beat works end-to-end before recording.

### 3.1 Face 1 (Cursor MCP)

```powershell
# In Cursor chat:
"Load team context for github.com/demo/api-service"
# Then append:
"Log decision: Redis for session cache — rejected in-memory dict"
```

Verify in BigQuery: new row in `agent_memory.codebase_logs`.

### 3.2 Fivetran sync (optional but strong)

- Trigger sync on `stowed_register` via ingestion agent (with Guardian approval)
- Confirm row appears in `modex_logs.modex_logs` with fresh `_fivetran_synced`

### 3.3 Face 2 mission (Cloud Run Dev UI or dashboard console)

Prompt from `SUBMISSION_DEMO.md`:

> "What architecture decisions has the team made on github.com/demo/api-service? Is our MoDeX data fresh? Cite provenance."

Expected: delegation to knowledge + lineage agents, answer cites `created_at` or `_fivetran_synced`.

### 3.4 Automated checks (no LLM)

```powershell
uv run python scripts/face2_tools_smoke.py      # ALL PASSED
uv run python scripts/test_dashboard_api.py       # overview + memory OK
uv run pytest tests/unit -q                       # 5/5
```

**Exit criteria:** Demo script runs without errors on first take.

---

## Phase 4 — Record demo video (2 hours) 🟡 June 10

**Objective:** 3-minute video judges will actually watch.

Follow `SUBMISSION_DEMO.md` exactly:

| Act | Duration | Show |
|-----|----------|------|
| Problem | 20s | Cold-start pain |
| Face 1 Cursor | 45s | Load context + log decision |
| Fivetran bus | 30s | Dashboard pipelines + freshness |
| 7-agent mission | 60s | Mission console answer with provenance |
| Close | 15s | Governance + tagline |

**Recording tips:**

- 1080p, Cursor + browser side by side
- Seed 1 fresh MCP event before recording
- Use Quick Mission buttons if LLM is slow
- Upload to YouTube (unlisted) or DevPost-native

**Exit criteria:** Video uploaded, link ready for DevPost.

---

## Phase 5 — DevPost submission (1 hour) 🟢 June 11

### Required fields

| Field | Value |
|-------|-------|
| Project name | MoDeX — Memory of Codex |
| Tagline | Shared reasoning memory for AI coding teams |
| Track | **Fivetran** |
| Try it link | `https://agentic-data-platform-979112189932.asia-south1.run.app` |
| Dashboard | `…/dashboard/` |
| GitHub | `https://github.com/Maanyaya/google-hackathon` |
| License | Apache 2.0 |
| Video | Link from Phase 4 |

### Judge-facing bullets (copy-paste)

- **Problem:** 15 devs, 15 AI agents, zero shared reasoning memory
- **Solution:** Two-face MoDeX — IDE MCP writes, platform agents query + govern
- **Fivetran depth:** MCP pipeline ops, Sheet→BQ sync bus, Platform Connector lineage, dbt transforms
- **Google stack:** ADK, Gemini, BigQuery, Vertex AI RAG, Cloud Run
- **Governance:** Guardian human-in-the-loop on every write
- **Live demo:** Hosted URL + public GitHub

**Exit criteria:** DevPost submitted before deadline.

---

## Timeline

```
June 8 (TODAY)
  ├── Phase 1: Commit + push dashboard restore
  └── Phase 2: Redeploy Cloud Run

June 9
  └── Phase 3: Full loop validation + fix any breakages

June 10
  └── Phase 4: Record + upload demo video

June 11
  └── Phase 5: DevPost submission (buffer until deadline)
```

---

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| Cloud Run still on old image | Judges see stale UI | Phase 2 redeploy today |
| LLM 403 locally | Can't demo `run_mission.py` | Use Cloud Run Dev UI / dashboard console |
| Fivetran sync slow | Stale `_fivetran_synced` in demo | Pre-sync `stowed_register` morning of recording |
| LLM latency in video | Awkward silence | Quick Mission buttons + pre-tested prompt |
| GitHub missing dashboard | Clone fails | Phase 1 push includes `frontend/dist` |
| SA key in git | Disqualification / security | Never commit; `.gitignore` covers `gen-lang-client-*.json` |

---

## Success Criteria (what "win-ready" looks like)

- [ ] GitHub repo cloneable with dashboard source + built dist
- [ ] Cloud Run URL matches GitHub (MoDeX branding, 7 agents, memory timeline)
- [ ] Face 1 MCP works in Cursor (load + append)
- [ ] Face 2 mission returns grounded answer with provenance on Cloud Run
- [ ] 3-min demo video uploaded
- [ ] DevPost submitted with Fivetran track selected
- [ ] No secrets in public repo

---

## Out of scope (do NOT do before deadline)

- Agent Runtime Playground fixes (Cloud Run is primary)
- New features (Action Agent Sheets/webhook config, new connectors)
- Eval dataset expansion
- Refactoring agent code
- Local Vertex IAM fix (nice-to-have, not blocking)

---

## Quick reference

| Resource | Path / URL |
|----------|------------|
| Live app | https://agentic-data-platform-979112189932.asia-south1.run.app |
| Dashboard | …/dashboard/ |
| Dev UI | …/dev-ui/?app=app |
| GitHub | https://github.com/Maanyaya/google-hackathon |
| Demo script | `SUBMISSION_DEMO.md` |
| Architecture | `ARCHITECTURE.md` |
| Tool smoke | `scripts/face2_tools_smoke.py` |
| Dashboard smoke | `scripts/test_dashboard_api.py` |

---

*Last updated: June 8, 2026 — supersedes parent `changed implementation plan.md`*
