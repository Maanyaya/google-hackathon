# MoDeX MCP — setup in a NEW repository

**Read this if:** you created a fresh GitHub repo and want MoDeX memory to work there.

**You do NOT need:** GCP credentials, BigQuery setup, or the hackathon repo cloned.

**You DO need:** Python, **Google Antigravity** (Section 7B–compliant), and 10 minutes.

---

## How it works (one sentence)

MoDeX stores memory under a **repo slug** like `github.com/yourname/your-repo`.  
Both agents must use **the same slug** when calling MCP tools.

---

## What you configure (3 places)

| # | Where | What | How often |
|---|--------|------|-----------|
| 1 | **GitHub** | Create the repo | Once |
| 2 | **Your PC** (`~/.gemini/antigravity/mcp_config.json`) | Connect Antigravity to MoDeX API | Once per machine |
| 3 | **Inside the new repo** (`.agents/modex.json`) | Tell the agent which repo slug to use | Once per project (commit to git) |

---

# STEP-BY-STEP

## Step 1 — Create the GitHub repo

On GitHub (or with `gh`):

```bash
gh repo create YOUR_GITHUB_USERNAME/YOUR_REPO_NAME --public
git clone https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

**Write down your memory key** (you will use this everywhere):

```
github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME
```

---

## Step 2 — Install Python package (each PC, once)

```bash
pip install mcp
```

---

## Step 3 — Download the MoDeX client (each PC, once)

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

## Step 4 — Antigravity MCP config (each PC, once)

**Windows:** `C:\Users\YOUR_USER\.gemini\antigravity\mcp_config.json`  
**Mac:** `/Users/YOUR_USER/.gemini/antigravity/mcp_config.json`

Use judge keys from [JUDGE_MCP_CREDENTIALS.md](./JUDGE_MCP_CREDENTIALS.md) or your own API key from the MoDeX host.

```json
{
  "mcpServers": {
    "modex-memory": {
      "command": "python",
      "args": ["C:\\Users\\YOUR_USER\\remote_client.py"],
      "env": {
        "MODEX_API_URL": "https://agentic-data-platform-979112189932.asia-south1.run.app",
        "MODEX_API_KEY": "YOUR-API-KEY",
        "MODEX_AGENT_TOOL": "antigravity",
        "MODEX_DEVELOPER_ID": "your-name"
      }
    }
  }
}
```

Restart Antigravity → MCP panel → `modex-memory` → **Connected**.

Tools you should see: `load_context`, `append_codebase_log`, `log_decision`, `compress_context`.

---

## Step 5 — Project config inside the repo (once, commit to git)

Create `.agents/modex.json`:

```json
{
  "project_repo": "github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME",
  "agent_tool": "antigravity",
  "auto_hydrate": true
}
```

Copy `.agents/hooks.json.example` → `.agents/hooks.json` if you want automatic capture (optional).

---

## Step 6 — Verify

In Antigravity chat:

```
Call load_context for github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME
```

```
Log a decision: "MoDeX MCP verified on new repo" for github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME
```

Open the [dashboard](https://agentic-data-platform-979112189932.asia-south1.run.app/dashboard/) → **Context pack** — your events should appear within seconds.

---

## Two-agent handoff (judge demo)

| Agent | API key | `developer_id` |
|-------|---------|----------------|
| A | `msk-7079ba3cdcf863affee3bbdea41b0485` | `judge` |
| B | `msk-1681c9a2c379d01e755fd0eb99de35ec` | `judge2` |

Same `project_repo`, different keys → shared memory with distinct authors.

---

## More

- [ANTIGRAVITY_MCP_SETUP.md](./ANTIGRAVITY_MCP_SETUP.md)
- [mcp-antigravity-judge.json](./mcp-antigravity-judge.json)
- [HACKATHON_COMPLIANCE.md](./HACKATHON_COMPLIANCE.md)
