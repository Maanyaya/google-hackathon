# MoDeX — Configuration reference

Step-by-step wiring for both faces. Every command is copy-pasteable.

> **Setting up MCP in a brand-new GitHub repo?**  
> Start here first → **[docs/NEW_REPO_MCP_SETUP.md](docs/NEW_REPO_MCP_SETUP.md)**  
> (9 numbered steps, checklist, copy-paste templates — no GCP needed.)

---

## Quick orientation

| Face | What you configure | Where it runs |
|------|-------------------|---------------|
| **Face 1** | Antigravity MCP + optional `.agents/hooks.json` / `.agents/modex.json` | Your machine (calls hosted API) |
| **Face 2** | Already deployed on Cloud Run | https://agentic-data-platform-979112189932.asia-south1.run.app |

Face 2 requires no local setup — open the dashboard and use it. Face 1 uses **Google Antigravity** (Section 7B). See [docs/HACKATHON_COMPLIANCE.md](docs/HACKATHON_COMPLIANCE.md).

---

## Face 1 — Antigravity configuration (recommended)

For judges and new repos, use the **hosted remote client** — no GCP on your machine:

→ **[docs/NEW_REPO_MCP_SETUP.md](docs/NEW_REPO_MCP_SETUP.md)**  
→ **[docs/ANTIGRAVITY_MCP_SETUP.md](docs/ANTIGRAVITY_MCP_SETUP.md)**

Quick summary:

1. `pip install mcp` + download `remote_client.py`
2. Paste [docs/mcp-antigravity-judge.json](docs/mcp-antigravity-judge.json) into `~/.gemini/antigravity/mcp_config.json`
3. Add `.agents/modex.json` in your repo (`agent_tool`: `antigravity`)
4. Optional: `.agents/hooks.json` from `.agents/hooks.json.example`

---

## Face 1 — Owner / local BigQuery setup (advanced)

### Step 1 — Clone and install

```powershell
git clone https://github.com/Maanyaya/google-hackathon.git
cd google-hackathon\agentic-data-platform

# Option A: uv (recommended)
uv sync

# Option B: plain venv
python -m venv .venv
.venv\Scripts\pip install -e .
```

### Step 2 — Create `.env`

Copy `.env.example` → `.env` and fill in:

```ini
# Required
GOOGLE_CLOUD_PROJECT=gen-lang-client-0795401430
GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\gen-lang-client-0795401430-...json

# Google Sheet mirror (Face 1 → Fivetran source)
MODEX_MEMORY_SHEET_ID=1NKxRyKBBgBzETtaaPO_gPC8vdM1i4vtt5yxrq6iCRck
MODEX_LOG_SHEET_RANGE=MoDex_Logs!A1

# Fivetran (only needed for Face 2 live connector ops)
FIVETRAN_API_KEY=your-key
FIVETRAN_API_SECRET=your-secret
```

> The GCP service account JSON lives in the workspace root folder (one level above `agentic-data-platform/`). The hook runner auto-detects it there — you do not have to set `GOOGLE_APPLICATION_CREDENTIALS` if it is in that exact location.

### Step 3 — Wire `.agents/hooks.json` (optional)

Copy `.agents/hooks.json.example` → `.agents/hooks.json` **in the workspace root** and point commands at `modex_mcp/hook_runner.py` via `python.exe`.

> **Critical (Windows):** Commands must call `python.exe` directly — never via a `.cmd` or `.bat` wrapper. Some Windows IDEs pipe hook stdin as UTF-16LE; if you add a `cmd.exe` layer, stdin is dropped and nothing is logged.

### Step 4 — Set `.agents/modex.json`

```json
{
  "project_repo": "github.com/your-org/your-repo",
  "agent_tool": "antigravity",
  "developer_id": "your-email@example.com",
  "auto_hydrate": true
}
```

| Key | What it does |
|-----|--------------|
| `project_repo` | Repo slug stamped on every event — used to group sessions |
| `agent_tool` | Label for the IDE (use `antigravity`) |
| `developer_id` | Optional — defaults to git `user.email` if blank |
| `auto_hydrate` | `true` → on session start, loads last context pack automatically |

### Step 5 — Restart Antigravity and verify

1. Restart Antigravity (hooks load at startup)
2. Confirm MCP → `modex-memory` connected
3. Send any message in the agent
4. Check the debug log:

```powershell
# Windows — last 20 lines of the hook debug log
Get-Content ".agents\modex-hook-debug.log" -Tail 20
```

Each entry should show `"parsed": true` with a real `conversation_id`. If you see `"parsed": false` with `"raw_preview": ""`, the hook is firing but stdin is empty — go back to Step 3 and confirm `python.exe` is called directly.

---

## Face 1 — Antigravity configuration

### Step 1 — Create the hook scripts

Create folder `.agents/hooks/` in the workspace root and add these four files:

**`.agents/hooks/modex_run.cmd`** (shared runner — all hooks call this):
```batch
@echo off
setlocal
set "MODEX_ROOT=%~dp0..\..\agentic-data-platform"
set "GOOGLE_CLOUD_PROJECT=gen-lang-client-0795401430"
set "MODEX_AGENT_TOOL=antigravity"
if exist "C:\path\to\gen-lang-client-0795401430-...json" (
  set "GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\gen-lang-client-0795401430-...json"
)
set "PYTHONPATH=%MODEX_ROOT%"
"%MODEX_ROOT%\.venv\Scripts\python.exe" -m modex_mcp.hook_runner %1
```

**`.agents/hooks/modex_pre_invocation.cmd`**:
```batch
@echo off
call "%~dp0modex_run.cmd" beforeSubmitPrompt
```

**`.agents/hooks/modex_post_tool.cmd`**:
```batch
@echo off
call "%~dp0modex_run.cmd" postToolUse
```

**`.agents/hooks/modex_post_invocation.cmd`**:
```batch
@echo off
call "%~dp0modex_run.cmd" afterAgentResponse
```

**`.agents/hooks/modex_stop.cmd`**:
```batch
@echo off
call "%~dp0modex_run.cmd" stop
```

### Step 2 — Wire `.agents/hooks.json`

```json
{
  "PreInvocation": [{
    "type": "command",
    "command": "cmd.exe /c .agents\\hooks\\modex_pre_invocation.cmd"
  }],
  "PostToolUse": [{
    "type": "command",
    "command": "cmd.exe /c .agents\\hooks\\modex_post_tool.cmd",
    "matcher": "edit_file|run_command|view_file|grep_search|list_dir|replace_file_content|multi_replace_file_content|write_to_file"
  }],
  "PostInvocation": [{
    "type": "command",
    "command": "cmd.exe /c .agents\\hooks\\modex_post_invocation.cmd"
  }],
  "Stop": [{
    "type": "command",
    "command": "cmd.exe /c .agents\\hooks\\modex_stop.cmd"
  }]
}
```

### Step 3 — Set `.agents/modex.json`

```json
{
  "project_repo": "github.com/your-org/your-repo",
  "agent_tool": "antigravity",
  "developer_id": "your-email@example.com",
  "auto_hydrate": true
}
```

### Step 4 — (Optional) Auto-hydrate via GEMINI.md

Antigravity injects context from a file rather than inline. Add to `.agents/GEMINI.md`:

```markdown
## Session start
Read `.agents/modex-hydration.md` if it exists. It contains the compressed
context from the previous coding session — decisions made, rejected approaches,
files in flight, and the last user request. Build on it; do not start fresh.
```

The hook runner writes `.agents/modex-hydration.md` on every `sessionStart` event when `auto_hydrate: true`.

---

## Face 1 — Hosted MCP (no GCP credentials needed)

Use this if you just want to log decisions and read context — no hooks, no local install.

### Antigravity `~/.gemini/antigravity/mcp_config.json`

Use [docs/mcp-antigravity-judge.json](docs/mcp-antigravity-judge.json) — set `"MODEX_AGENT_TOOL": "antigravity"`.

```json
{
  "mcpServers": {
    "modex-memory": {
      "command": "python",
      "args": ["C:\\path\\to\\remote_client.py"],
      "env": {
        "MODEX_API_URL": "https://agentic-data-platform-979112189932.asia-south1.run.app",
        "MODEX_API_KEY": "msk-7079ba3cdcf863affee3bbdea41b0485",
        "MODEX_AGENT_TOOL": "antigravity",
        "MODEX_DEVELOPER_ID": "your-name"
      }
    }
  }
}
```

> Section 7B: use Antigravity only for Face 1 setup. See [docs/HACKATHON_COMPLIANCE.md](docs/HACKATHON_COMPLIANCE.md).

Get `remote_client.py`:
```bash
curl -o remote_client.py \
  https://raw.githubusercontent.com/Maanyaya/google-hackathon/main/modex_mcp/remote_client.py
```

**Available MCP tools:**

| Tool | What it does |
|------|--------------|
| `load_context(project_repo)` | Returns full context pack — decisions, rejected, files, briefing |
| `append_codebase_log(...)` | Write any event (decision, note, error) to memory |
| `log_decision(decision, context)` | Shortcut for logging a significant engineering choice |
| `compress_context(project_repo)` | Force a handoff snapshot now (writes to BQ + Sheet) |
| `save_session_memory(...)` | End-of-session save with decisions list + rejected approaches |

---

## Face 2 — Using the deployed agent (no config needed)

Face 2 is already live. Open the dashboard and use **Ask Face 2**:

**URL:** https://agentic-data-platform-979112189932.asia-south1.run.app/dashboard/

Three demo missions:

| Mission | Prompt | What it demonstrates |
|---------|--------|----------------------|
| Hydrate me | `Hydrate me on github.com/Maanyaya/google-hackathon` | Memory answers — decisions, rejected, files |
| Why this? | `Why was python.exe chosen over .cmd for Antigravity hooks?` | Provenance — session decision + PR citation |
| Pipeline health | `What is the sync status of the MoDeX logs pipeline?` | Live Fivetran MCP — connector status, last sync |

---

## Face 2 — Running locally (optional, needs GCP)

```powershell
cd agentic-data-platform

# Set environment
copy .env.example .env
# fill in GOOGLE_CLOUD_PROJECT, GOOGLE_APPLICATION_CREDENTIALS, FIVETRAN_* keys

# Run the ADK app
uv run uvicorn app.fast_api_app:app --host 0.0.0.0 --port 8080 --reload
```

Open http://localhost:8080/dashboard/ or http://localhost:8080/dev-ui (ADK live agent UI).

**Required env vars for Face 2:**

| Var | Value |
|-----|-------|
| `GOOGLE_CLOUD_PROJECT` | `gen-lang-client-0795401430` |
| `GOOGLE_CLOUD_LOCATION` | `asia-south1` |
| `GOOGLE_GENAI_USE_VERTEXAI` | `True` |
| `GOOGLE_APPLICATION_CREDENTIALS` | path to service account JSON |
| `FIVETRAN_API_KEY` | Fivetran account API key |
| `FIVETRAN_API_SECRET` | Fivetran account API secret |
| `FIVETRAN_BQ_GROUP_ID` | `solve_unhurt` |
| `MODEX_MEMORY_SHEET_ID` | `1NKxRyKBBgBzETtaaPO_gPC8vdM1i4vtt5yxrq6iCRck` |

---

## Face 2 — Deploying your own instance

```powershell
cd agentic-data-platform

# Build image
gcloud builds submit \
  --tag asia-south1-docker.pkg.dev/YOUR_PROJECT/cloud-run-source-deploy/agentic-data-platform:latest \
  --project YOUR_PROJECT .

# Deploy to Cloud Run
gcloud run deploy agentic-data-platform \
  --image asia-south1-docker.pkg.dev/YOUR_PROJECT/cloud-run-source-deploy/agentic-data-platform:latest \
  --region asia-south1 \
  --project YOUR_PROJECT \
  --set-env-vars GOOGLE_CLOUD_PROJECT=YOUR_PROJECT,GOOGLE_CLOUD_LOCATION=asia-south1,GOOGLE_GENAI_USE_VERTEXAI=True \
  --set-env-vars FIVETRAN_API_KEY=...,FIVETRAN_API_SECRET=... \
  --platform managed \
  --allow-unauthenticated
```

Set the remaining secrets via Cloud Run secret manager or `--set-env-vars`.

---

## BigQuery setup

Create the memory tables (only needed once):

```powershell
.venv\Scripts\python.exe scripts\setup_agent_memory.py
```

This creates:
- `agent_memory.codebase_logs` — primary append-only event store (15 columns)
- `agent_memory.session_logs` — legacy summary table (backward compat)

**Google Sheet header** — paste in row 1 of the `MoDex_Logs` tab (columns A–O):
```
event_id	session_id	developer_id	agent_tool	project_repo	event_type	file_path	commit_sha	summary	payload_json	parent_event_id	created_at	context_json	transcript_md	session_summary
```

Share the sheet with the service account email (Editor role).

---

## Troubleshooting

### Face 1 hooks

| Symptom | Cause | Fix |
|---------|-------|-----|
| `"parsed": false, "raw_preview": ""` | stdin dropped — cmd.exe wrapper | Use `python.exe` directly in `hooks.json`, never via `.cmd` |
| `"parsed": false` with garbled text | Wrong encoding | Already handled — runner auto-decodes UTF-16LE/UTF-8/BOM |
| Hook fires but no BQ row | Credentials not found | Check `GOOGLE_APPLICATION_CREDENTIALS` or SA JSON at workspace root |
| `modex-hook-debug.log` not created | `hook_runner.py` path wrong | Verify the absolute path in `hooks.json` points to the correct `.venv` |
| `session_id` is `unknown` | `conversation_id` missing from payload | Ensure Antigravity hook payload includes session/conversation id |

### Face 1 MCP

| Symptom | Fix |
|---------|-----|
| `modex-memory` not appearing in Antigravity MCP list | Restart Antigravity after editing `mcp_config.json` |
| `load_context` returns empty | No events logged yet — send a message first, then call `load_context` |
| `401 Unauthorized` | Wrong API key in MCP env |

### Face 2

| Symptom | Fix |
|---------|-----|
| Answer takes 90+ seconds | Normal — Gemini 2.5 Flash cold start on Cloud Run. First query after idle warms it. |
| Fivetran tools return empty | Fivetran API key not set as env var on Cloud Run |
| `get_team_context` returns no decisions | No `context_compressed` events in BigQuery yet — run `handoff snapshot` |

---

## Verify the full pipeline

```powershell
# 1 — Unit tests
.venv\Scripts\python.exe -m pytest tests\unit\ -q

# 2 — End-to-end: fires hooks (UTF-16LE), writes to BQ + Sheet,
#     reads sheet cells back, hydrates as Agent B
.venv\Scripts\python.exe scripts\verify_pipeline_rigorous.py

# 3 — Handoff CLI smoke test
.venv\Scripts\python.exe -m modex_mcp.handoff status --repo github.com/Maanyaya/google-hackathon
.venv\Scripts\python.exe -m modex_mcp.handoff snapshot --repo github.com/Maanyaya/google-hackathon
.venv\Scripts\python.exe -m modex_mcp.handoff hydrate  --repo github.com/Maanyaya/google-hackathon
```

A passing `verify_pipeline_rigorous.py` run prints:
```
OVERALL: PASS — pipeline is genuinely working end to end
```
