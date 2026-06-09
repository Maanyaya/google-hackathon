# MoDeX Face 1 MCP — Developer-Edge Memory

Connect **Cursor**, **Antigravity**, or **Windsurf** to MoDeX shared memory.

> **Judges:** use [JUDGES.md](../JUDGES.md) or the dashboard **Setup** section for ready-made credentials and copy-paste MCP config (`docs/mcp-cursor-judge.json`).

---

## Use MoDeX from anywhere (hosted — recommended)

MoDeX is **served over the web**. The Cloud Run service holds the Google Cloud
credentials and owns the one shared BigQuery memory bus. Each teammate only needs
**a personal API key + the service URL** — no GCP key file, no cloning the repo.

```
Maya (Mac · Antigravity) ─┐                         ┌─ same shared memory
                          ├─► remote_client.py ─► Hosted MoDeX API (Cloud Run)
Gagan (Win · Cursor) ─────┘     (just URL+KEY)        └─► agent_memory.codebase_logs (BigQuery)
```

### Face 1 — install the memory client (any OS, any IDE)

1. **Get two things from the MoDeX owner:** the service URL and your personal key.
   - URL: `https://<your-cloud-run-host>.run.app`
   - Key: e.g. `msk-...` (the server maps it to your `developer_id`)
2. **Grab the client.** Either:
   - copy the single file `modex_mcp/remote_client.py` and run `pip install mcp`, **or**
   - if the repo is public: `uvx --from git+https://github.com/Maanyaya/google-hackathon modex-memory-remote`
3. **Point your IDE at it.**

**Cursor** — `%USERPROFILE%\.cursor\mcp.json` (Win) or `~/.cursor/mcp.json` (Mac):

```json
{
  "mcpServers": {
    "modex-memory": {
      "command": "python",
      "args": ["/abs/path/to/remote_client.py"],
      "env": {
        "MODEX_API_URL": "https://<your-cloud-run-host>.run.app",
        "MODEX_API_KEY": "your-personal-key",
        "MODEX_AGENT_TOOL": "cursor"
      }
    }
  }
}
```

**Antigravity** — `~/.gemini/antigravity/mcp_config.json` (Mac/Win), same shape:

```json
{
  "mcpServers": {
    "modex-memory": {
      "command": "python",
      "args": ["/abs/path/to/remote_client.py"],
      "env": {
        "MODEX_API_URL": "https://<your-cloud-run-host>.run.app",
        "MODEX_API_KEY": "your-personal-key",
        "MODEX_AGENT_TOOL": "antigravity"
      }
    }
  }
}
```

> If you installed via `uvx`, set `"command": "uvx"` and
> `"args": ["--from", "git+https://github.com/Maanyaya/google-hackathon", "modex-memory-remote"]`.

That's it — restart the IDE, and `load_context` / `append_codebase_log` write into
the **same** shared memory as everyone else.

### Face 2 — open the Command Center (no install)

Face 2 (the agent platform + dashboard) is already on the web. Just open:

```
https://<your-cloud-run-host>.run.app/dashboard/
```

Anyone with the link sees the live memory graph, decisions, pipelines, and the
agent team — nothing to install.

### Verify your key works

```bash
curl -H "Authorization: Bearer your-personal-key" \
  https://<your-cloud-run-host>.run.app/api/v1/whoami
# -> {"status":"ok","developer_id":"maya"}
```

### Owner setup (one time)

The owner sets per-user keys as an env var on Cloud Run, then shares one key per
teammate:

```bash
gcloud run services update agentic-data-platform --region <region> \
  --update-env-vars 'MODEX_API_KEYS=gagan:msk-AAA,maya:msk-BBB'
```

Hosted API surface (all under `/api/v1`, bearer-auth except `/health`):
`POST /memory/append` · `POST /memory/decision` · `POST /memory/session_end` ·
`GET /memory/context` · `GET /memory/timeline` · `GET /memory/history` ·
`GET /memory/catalog` · `GET /whoami` · `GET /health`.

---

## What it does

**Primary store:** `agent_memory.codebase_logs` (append-only events)

| Tool | Direction | When |
|------|-----------|------|
| `append_codebase_log` | **Write** | Every meaningful action (file_edit, tool_call, decision, error) |
| `load_context_from_logs` | **Read** | **Start of new session** — replay event timeline |
| `log_decision` | **Write** | Single decision event |
| `save_session_memory` | **Write** | End of session → `session_end` + decision events |
| `load_team_context` | **Read** | Alias for `load_context_from_logs` |
| `load_session_history` | **Read** | Same dev, new tool (Cursor → Antigravity) |
| `get_memory_catalog` | **Read** | Repos with log activity |

### Event types
`session_start` · `user_prompt` · `agent_response` · `tool_call` · `file_edit` · `decision` · `error` · `session_end` · `context_compressed`

## Automated logging (Cursor hooks)

MoDeX logs **without** asking the agent to call MCP tools. Project hooks live at
the workspace root in `.cursor/hooks.json` and call the runner **directly** with
`python.exe`:

| Event | Auto action |
|-------|-------------|
| `sessionStart` | Log session start + **inject context pack** into the agent |
| `beforeSubmitPrompt` | Log the full user message (also opens the session on resumed chats) |
| `afterAgentResponse` | Log the agent's full reply |
| `afterFileEdit` | Log file edits (skips empty/no-path noise) |
| `postToolUse` | Log tool calls with full input |
| `afterShellExecution` | Log shell commands + output |
| `afterMCPExecution` | Log MCP tool calls (skips modex-memory) |
| `postToolUseFailure` | Log errors |
| `stop` | Refresh the compressed handoff (`context_compressed`) |
| `sessionEnd` | Log session end + compress + write `.agents/modex-transcript.md` |

> **Windows critical:** hooks must invoke `python.exe` directly. Routing through
> a `.cmd`/`.bat` wrapper drops stdin (hooks fire with empty payloads). Cursor
> also pipes stdin as **UTF-16LE**; the runner decodes UTF-16/UTF-8/BOM
> automatically.

**Enable:** open the workspace root in Cursor → hooks load from
`.cursor/hooks.json`. Restart Cursor. Check **Settings → Hooks**, then send a
message and confirm `.agents/modex-hook-debug.log` shows `"parsed": true` with a
real `conversation_id`.

**Configure:** edit `.cursor/modex.json` (and `.agents/modex.json`):

```json
{
  "project_repo": "github.com/Maanyaya/google-hackathon",
  "agent_tool": "cursor",
  "developer_id": "",
  "auto_hydrate": true
}
```

## Deterministic handoff CLI (hook-independent backbone)

Guarantees context transfer even if an IDE's hooks misbehave:

```bash
# Agent A — compress repo memory into one handoff row (BigQuery + Sheet) + self-verify
python -m modex_mcp.handoff snapshot --repo github.com/Maanyaya/google-hackathon

# Agent B (any tool/OS) — load the SAME system context to resume
python -m modex_mcp.handoff hydrate  --repo github.com/Maanyaya/google-hackathon

# Show memory counts + freshness
python -m modex_mcp.handoff status   --repo github.com/Maanyaya/google-hackathon
```

`hydrate` returns a **system-context briefing** (decisions, files in flight,
unresolved errors, last user ask, last agent reply) followed by the full
transcript — identical to what `load_context` serves over MCP.

**Verify the pipeline end to end** (fires hooks exactly like Cursor via UTF-16LE
stdin, writes to BQ + Sheet, reads the sheet cells back, hydrates as Agent B):

```bash
python scripts/verify_pipeline_rigorous.py   # prints OVERALL: PASS
```

For **Antigravity**, hooks live in `.agents/hooks.json` (project root). Same auto-logging as Cursor:

| Antigravity event | Auto action |
|-------------------|-------------|
| `PreInvocation` | Session start + write `.agents/modex-hydration.md` + log user prompt |
| `PostToolUse` | Log `edit_file`, `run_command`, etc. |
| `Stop` | Log session end |

**Enable in Antigravity:**

1. Open the **hackathon repo root** in Antigravity (not only `agentic-data-platform/`)
2. Agent panel → **⋯** → **MCP Servers** → confirm `modex-memory` is connected
3. **Settings → Customizations → Installed hooks → Refresh**
4. Config: `.agents/modex.json` sets `"agent_tool": "antigravity"`
5. Rules: `.agents/GEMINI.md` tells the agent to read `modex-hydration.md` each session

Antigravity injects context via the hydration **file** (not inline like Cursor), because hook APIs differ.

## Host / local-credentials setup (advanced)

> Most teammates should use the **hosted** path above and never touch this. This
> section is for the person who runs MoDeX locally with direct GCP credentials
> (e.g. the owner developing the server, or an offline single-machine setup).

### 1. Create BigQuery table

```powershell
cd agentic-data-platform
uv run python scripts/setup_agent_memory.py
```

### 2. Add to Cursor MCP config

Edit `%USERPROFILE%\.cursor\mcp.json` (or project `.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "modex-memory": {
      "command": "uv",
      "args": ["run", "python", "-m", "modex_mcp.server"],
      "cwd": "D:\\Google cloud rapid agent hackathon\\agentic-data-platform",
      "env": {
        "GOOGLE_CLOUD_PROJECT": "gen-lang-client-0795401430",
        "GOOGLE_APPLICATION_CREDENTIALS": "C:\\path\\to\\your\\adc-or-sa-key.json"
      }
    }
  }
}
```

Use Application Default Credentials (`gcloud auth application-default login`) if you omit `GOOGLE_APPLICATION_CREDENTIALS`.

### 3. Google Sheets mirror (Fivetran bus)

Every Face 1 event is mirrored to the spreadsheet so Fivetran can sync it to BigQuery for **other developers' agents**.

**Tab `MoDex_Logs`** (every raw event + compressed handoff pack):

`event_id, session_id, developer_id, agent_tool, project_repo, event_type, file_path, commit_sha, summary, payload_json, parent_event_id, created_at, context_json, transcript_md`

| event_type | What lands in the sheet |
|------------|-------------------------|
| `file_edit`, `tool_call`, `user_prompt`, … | One row per IDE action; `summary` = short label; `payload_json` = structured extras |
| `context_compressed` | **Full handoff** in `context_json` + **`transcript_md`** (complete chat as Markdown) |
| `session_end` | Session boundary; triggers auto-compress via hooks |

Fivetran connector `stowed_register` syncs `MoDex_Logs` → `modex_logs.modex_logs` in BigQuery.

**Tab `MoDeX Memory`** (session handoff row — one per `save_session_memory`):

`session_id, developer_id, agent_tool, project_repo, memory_type, summary, decisions_json, files_touched, rejected_approaches, context_json, created_at`

The `context_json` column holds the same structured pack so teammates loading via Fivetran get dense, machine-readable context.

**Compress manually:** call MCP tool `compress_context(project_repo=...)` or `POST /api/v1/memory/compress`.

## Demo flow (session handoff)

**Session A (Cursor):**
```
save_session_memory(
  developer_id="gagan@team.dev",
  agent_tool="cursor",
  project_repo="github.com/team/api-service",
  summary="Implemented JWT auth. Chose PostgreSQL.",
  decisions=["PostgreSQL over MongoDB"],
  rejected_approaches=["MongoDB for auth"]
)
```

**Session B (Antigravity — new agent):**
```
load_team_context(project_repo="github.com/team/api-service")
```

Paste `hydration_prompt` into the new agent's context — it continues where Cursor left off.

## Run server manually

```powershell
uv run python -m modex_mcp.server
```

Stdio MCP — intended for IDE integration, not HTTP.
