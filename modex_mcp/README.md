# MoDeX Face 1 MCP — Developer-Edge Memory

Connect **Cursor**, **Antigravity**, or **Windsurf** to MoDeX shared memory.

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
`session_start` · `user_prompt` · `tool_call` · `file_edit` · `decision` · `error` · `session_end`

## Setup

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

### 3. Optional — mirror to Google Sheets (Fivetran path)

Set in `.env`:

```
MODEX_MEMORY_SHEET_ID=<your-google-sheet-id>
MODEX_MEMORY_SHEET_RANGE=MoDeX Memory!A1
```

Add a **MoDeX Memory** tab with headers:

`session_id, developer_id, agent_tool, project_repo, memory_type, summary, decisions_json, files_touched, rejected_approaches, created_at`

Fivetran Sheets connector syncs this tab → BigQuery for the full pipeline story.

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
