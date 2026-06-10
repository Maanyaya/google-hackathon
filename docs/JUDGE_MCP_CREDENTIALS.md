# MoDeX — Judge MCP credentials (public)

Use these keys to test **Face 1 MCP** in Cursor. No GCP setup required.

## Why two keys?

Shared memory only proves itself when **two different people** write to the **same repo slug**.

| Key | `developer_id` | Role in demo |
|-----|----------------|--------------|
| **Judge** | `judge` | **Agent A** — first session: code, `log_decision`, `compress_context` |
| **Judge 2** | `judge2` | **Agent B** — second session: `load_context`, continues with A's memory |

Same `project_repo` (e.g. `github.com/demo/api-service`), **different API keys** → logs show two distinct authors on one shared memory bus. That is the handoff story judges should see.

| Field | Value |
|-------|--------|
| **Service URL** | `https://agentic-data-platform-979112189932.asia-south1.run.app` |
| **Judge API key (Agent A)** | `msk-7079ba3cdcf863affee3bbdea41b0485` |
| **Judge 2 API key (Agent B)** | `msk-1681c9a2c379d01e755fd0eb99de35ec` |
| **Demo repo slug** | `github.com/demo/api-service` |

Verify each key maps to a different identity:

```bash
curl -H "Authorization: Bearer msk-7079ba3cdcf863affee3bbdea41b0485" \
  https://agentic-data-platform-979112189932.asia-south1.run.app/api/v1/whoami
# → {"status":"ok","developer_id":"judge"}

curl -H "Authorization: Bearer msk-1681c9a2c379d01e755fd0eb99de35ec" \
  https://agentic-data-platform-979112189932.asia-south1.run.app/api/v1/whoami
# → {"status":"ok","developer_id":"judge2"}
```

## Agent A — Cursor `~/.cursor/mcp.json` (judge)

**Windows:** `C:\Users\YOUR_USER\.cursor\mcp.json`  
**Mac:** `/Users/YOUR_USER/.cursor/mcp.json`

```json
{
  "mcpServers": {
    "modex-memory": {
      "command": "python",
      "args": ["C:\\Users\\YOUR_USER\\remote_client.py"],
      "env": {
        "MODEX_API_URL": "https://agentic-data-platform-979112189932.asia-south1.run.app",
        "MODEX_API_KEY": "msk-7079ba3cdcf863affee3bbdea41b0485",
        "MODEX_AGENT_TOOL": "cursor",
        "MODEX_DEVELOPER_ID": "judge"
      }
    }
  }
}
```

On Mac use `python3` and `/Users/YOUR_USER/remote_client.py`.

## Agent B — second Cursor window / second machine (judge2)

Use the **other** key so logs are stamped as a different developer:

```json
{
  "mcpServers": {
    "modex-memory": {
      "command": "python",
      "args": ["C:\\Users\\YOUR_USER\\remote_client.py"],
      "env": {
        "MODEX_API_URL": "https://agentic-data-platform-979112189932.asia-south1.run.app",
        "MODEX_API_KEY": "msk-1681c9a2c379d01e755fd0eb99de35ec",
        "MODEX_AGENT_TOOL": "cursor",
        "MODEX_DEVELOPER_ID": "judge2"
      }
    }
  }
}
```

Then in chat:

```
Call load_context for github.com/demo/api-service.
Summarize decisions judge made that are not in git.
```

## Two-agent handoff script (60 seconds)

1. **Agent A** (`judge` key): work → `log_decision` → `compress_context`
2. **Agent B** (`judge2` key): same repo slug → `load_context` → sees A's decisions
3. **Proof:** Google Sheet / dashboard shows rows from both `judge` and `judge2` on the same `project_repo`

**One-time install (both agents):**

```bash
pip install mcp
curl -o ~/remote_client.py \
  https://raw.githubusercontent.com/Maanyaya/google-hackathon/main/modex_mcp/remote_client.py
```

Restart Cursor → **Settings → MCP** → `modex-memory` should show **Connected**.

## Ready-made config files

| File | Purpose |
|------|---------|
| [mcp-cursor-judge.json](./mcp-cursor-judge.json) | Cursor MCP snippet |
| [mcp-antigravity-judge.json](./mcp-antigravity-judge.json) | Antigravity MCP snippet |
| [NEW_REPO_MCP_SETUP.md](./NEW_REPO_MCP_SETUP.md) | Full setup for your own repo |

## More

- [JUDGES.md](../JUDGES.md) — Face 2 demo prompts + full judge guide
- [Dashboard](https://agentic-data-platform-979112189932.asia-south1.run.app/dashboard/)
