# MoDeX — Judge MCP credentials (public)

Use these keys to test **Face 1 MCP** in Cursor. No GCP setup required.

| Field | Value |
|-------|--------|
| **Service URL** | `https://agentic-data-platform-979112189932.asia-south1.run.app` |
| **Judge API key** | `msk-7079ba3cdcf863affee3bbdea41b0485` |
| **Judge 2 API key** | `msk-1681c9a2c379d01e755fd0eb99de35ec` |
| **Demo repo slug** | `github.com/demo/api-service` |

Verify a key:

```bash
curl -H "Authorization: Bearer msk-7079ba3cdcf863affee3bbdea41b0485" \
  https://agentic-data-platform-979112189932.asia-south1.run.app/api/v1/whoami
# → {"status":"ok","developer_id":"judge"}
```

## Cursor — copy/paste `~/.cursor/mcp.json`

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

**One-time install:**

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
