# MoDeX MCP — Antigravity setup

Use this guide to connect **Google Antigravity** to the hosted MoDeX memory API (Face 1). No GCP credentials required on your machine.

**Related docs:**
- [NEW_REPO_MCP_SETUP.md](./NEW_REPO_MCP_SETUP.md) — full new-repo walkthrough (Antigravity)
- [JUDGE_MCP_CREDENTIALS.md](./JUDGE_MCP_CREDENTIALS.md) — public judge keys for handoff demo
- [mcp-antigravity-judge.json](./mcp-antigravity-judge.json) — copy-paste MCP snippet

---

## How it works

Antigravity is a **permitted** Google AI coding tool for this hackathon. MoDeX Face 1 runs as an MCP server that talks to our **hosted Cloud Run API** — your IDE never touches BigQuery directly.

| You configure | Where | Purpose |
|---|---|---|
| MCP client | `~/.gemini/antigravity/mcp_config.json` | Connect Antigravity → MoDeX API |
| Project slug | `.agents/modex.json` in repo | Which repo's memory to read/write |
| Hooks (optional) | `.agents/hooks.json` | Auto-capture prompts, edits, session end |

---

## Step 1 — Install once per machine

```bash
pip install mcp
```

**Download the remote client** (no hackathon repo clone needed):

**Windows (PowerShell):**
```powershell
curl -o "$env:USERPROFILE\remote_client.py" `
  https://raw.githubusercontent.com/Maanyaya/google-hackathon/main/modex_mcp/remote_client.py
```

**Mac / Linux:**
```bash
curl -o ~/remote_client.py \
  https://raw.githubusercontent.com/Maanyaya/google-hackathon/main/modex_mcp/remote_client.py
```

---

## Step 2 — Antigravity MCP config

**File path:**

| OS | Path |
|---|---|
| **Windows** | `C:\Users\YOUR_USER\.gemini\antigravity\mcp_config.json` |
| **Mac** | `/Users/YOUR_USER/.gemini/antigravity/mcp_config.json` |

Create the folder if it doesn't exist, then paste:

### Agent A (judge — first session)

```json
{
  "mcpServers": {
    "modex-memory": {
      "command": "python",
      "args": ["C:\\Users\\YOUR_USER\\remote_client.py"],
      "env": {
        "MODEX_API_URL": "https://agentic-data-platform-979112189932.asia-south1.run.app",
        "MODEX_API_KEY": "msk-7079ba3cdcf863affee3bbdea41b0485",
        "MODEX_AGENT_TOOL": "antigravity",
        "MODEX_DEVELOPER_ID": "judge"
      }
    }
  }
}
```

**Mac:** use `python3` and `/Users/YOUR_USER/remote_client.py`.

### Agent B (judge2 — handoff session)

Same file on a **second machine or second Antigravity profile**, but swap the key:

```json
"MODEX_API_KEY": "msk-1681c9a2c379d01e755fd0eb99de35ec",
"MODEX_DEVELOPER_ID": "judge2"
```

Restart Antigravity after saving.

---

## Step 3 — Project config inside your repo

In the repo you are working on, create **`.agents/modex.json`**:

```json
{
  "project_repo": "github.com/YOUR_ORG/YOUR_REPO",
  "agent_tool": "antigravity",
  "developer_id": "judge",
  "auto_hydrate": true
}
```

Replace `project_repo` with your real GitHub slug (must match what you pass to MCP tools).

**Optional — auto-hydrate on session start.** Add to `.agents/GEMINI.md`:

```markdown
## Session start
Read `.agents/modex-hydration.md` if it exists. It contains compressed context
from the previous session — decisions, rejected approaches, files in flight.
Build on it; do not start fresh.
```

---

## Step 4 — Verify MCP is connected

1. Open Antigravity → MCP / tools panel
2. Confirm **`modex-memory`** is connected
3. Tools should include:
   - `load_context`
   - `append_codebase_log`
   - `log_decision`
   - `compress_context`
   - `save_session_memory`

**Terminal check:**
```bash
curl -H "Authorization: Bearer msk-7079ba3cdcf863affee3bbdea41b0485" \
  https://agentic-data-platform-979112189932.asia-south1.run.app/api/v1/whoami
# → {"status":"ok","developer_id":"judge"}
```

---

## Step 5 — Test prompts in Antigravity

**Agent A — write memory:**
```
Log a decision: "Use token bucket rate limiting — fixed window causes burst spikes"
for github.com/demo/api-service, then compress_context for that repo.
```

**Agent B — read memory (different key / developer_id):**
```
Call load_context for github.com/demo/api-service.
What decisions did judge make that are not in git?
```

---

## Optional — auto-capture hooks

For automatic logging (prompts, file edits, session end), wire `.agents/hooks.json` in the **hackathon repo root**. See [CONFIGURATION.md](../CONFIGURATION.md) → "Face 1 — Antigravity configuration".

Hooks call `modex_mcp.hook_runner` and stamp events with `"ide": "antigravity"`.

---

## Antigravity configuration reference

| Setting | Value |
|---|---|
| MCP config file | `~/.gemini/antigravity/mcp_config.json` |
| `MODEX_AGENT_TOOL` | `antigravity` |
| Project config | `.agents/modex.json` |
| Hydration | `.agents/modex-hydration.md` file |

All Face 1 clients talk to the **same hosted MoDeX API** and the **same BigQuery memory bus**.

---

## Hosted vs bring-your-own

**What we run (demo / judges):**
- MoDeX API + Face 2 ADK agent → **our Google Cloud Run** (`gen-lang-client-0795401430`)
- Fivetran connectors → **our Fivetran account** (3 connectors → BigQuery)
- Judge API keys → pre-provisioned, no signup needed

**What anyone can do:**
- Point `MODEX_API_URL` + `MODEX_API_KEY` at the hosted service (or self-host the open-source backend)
- Use their own Fivetran trial + BigQuery destination with the same connector pattern
- Same MCP config shape — swap URL, key, and `project_repo` slug

The architecture is **multi-tenant by design**: memory is keyed by `project_repo` + `developer_id`, not by our personal accounts.
