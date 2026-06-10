# MoDeX Face 1 MCP — Developer-Edge Memory

Connect **Google Antigravity** to MoDeX shared memory (Section 7B–compliant workflow).

> **Judges:** [JUDGES.md](../JUDGES.md) or dashboard **Setup** — copy-paste config from [docs/mcp-antigravity-judge.json](../docs/mcp-antigravity-judge.json).

> **New GitHub repo?** [docs/NEW_REPO_MCP_SETUP.md](../docs/NEW_REPO_MCP_SETUP.md)

> **Compliance:** [docs/HACKATHON_COMPLIANCE.md](../docs/HACKATHON_COMPLIANCE.md)

---

## Use MoDeX from anywhere (hosted — recommended)

MoDeX is **served over the web**. Cloud Run holds Google Cloud credentials and the shared BigQuery memory bus. Each teammate only needs **a personal API key + the service URL**.

```
Maya (Mac · Antigravity) ─┐                         ┌─ same shared memory
                          ├─► remote_client.py ─► Hosted MoDeX API (Cloud Run)
Gagan (Win · Antigravity) ┘     (just URL+KEY)        └─► agent_memory.codebase_logs (BigQuery)
```

### Face 1 — install the memory client

1. **Get** service URL + personal API key from [JUDGE_MCP_CREDENTIALS.md](../docs/JUDGE_MCP_CREDENTIALS.md).
2. `pip install mcp` and download `modex_mcp/remote_client.py`.
3. **Antigravity** — `~/.gemini/antigravity/mcp_config.json`:

```json
{
  "mcpServers": {
    "modex-memory": {
      "command": "python",
      "args": ["/abs/path/to/remote_client.py"],
      "env": {
        "MODEX_API_URL": "https://agentic-data-platform-979112189932.asia-south1.run.app",
        "MODEX_API_KEY": "your-personal-key",
        "MODEX_AGENT_TOOL": "antigravity"
      }
    }
  }
}
```

4. In your repo, add `.agents/modex.json` (see `.agents/modex.json.example`).

Restart Antigravity → MCP → `modex-memory` connected.

### Face 2 — Command Center (no install)

https://agentic-data-platform-979112189932.asia-south1.run.app/dashboard/

---

## MCP tools

| Tool | When |
|------|------|
| `load_context` | Start of session — full briefing |
| `append_codebase_log` | Explicit event write |
| `log_decision` | Record a significant choice |
| `compress_context` | Force handoff pack |

Event types: `session_start` · `user_prompt` · `agent_response` · `tool_call` · `file_edit` · `decision` · `error` · `session_end` · `context_compressed`

---

## Automated logging (Antigravity hooks)

Optional hooks in `.agents/hooks.json` call `modex_mcp.hook_runner` via `python.exe` (never through `.cmd` wrappers on Windows).

| Event | Auto action |
|-------|-------------|
| `PreInvocation` | Session start + hydration file + user prompt |
| `PostToolUse` | Log edits / commands |
| `PostInvocation` | Log agent response |
| `Stop` | Session end + `context_compressed` |

**Enable:**

1. Copy `.agents/hooks.json.example` → `.agents/hooks.json`
2. Set `.agents/modex.json` with `"agent_tool": "antigravity"`
3. Restart Antigravity → confirm `.agents/modex-hook-debug.log` shows `"parsed": true`

---

## Handoff CLI

```bash
python -m modex_mcp.handoff snapshot --repo github.com/demo/api-service
python -m modex_mcp.handoff hydrate  --repo github.com/demo/api-service
python -m modex_mcp.handoff status   --repo github.com/demo/api-service
```

---

## Verify compliance before submit

```bash
python scripts/check_hackathon_compliance.py
```
