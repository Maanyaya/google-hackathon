# MoDeX MCP — setup in a NEW repository

**Read this if:** you created a fresh GitHub repo and want MoDeX memory to work there.

**You do NOT need:** GCP credentials, BigQuery setup, or the hackathon repo cloned.

**You DO need:** Python, Cursor (or Antigravity), and 10 minutes.

---

## How it works (one sentence)

MoDeX stores memory under a **repo slug** like `github.com/yourname/your-repo`.  
Both agents must use **the same slug** when calling MCP tools.

---

## What you configure (3 places)

| # | Where | What | How often |
|---|--------|------|-----------|
| 1 | **GitHub** | Create the repo | Once |
| 2 | **Your PC** (`~/.cursor/mcp.json`) | Connect Cursor to MoDeX API | Once per machine |
| 3 | **Inside the new repo** (`.cursor/…`) | Tell the agent which repo slug to use | Once per project (commit to git) |

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

Example: if the repo is `https://github.com/maanya/demo-api`, the key is:

```
github.com/maanya/demo-api
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

Note the **full path** to `remote_client.py` — you need it in Step 4.

---

## Step 4 — Configure Cursor MCP (each PC, once)

This file is **NOT inside your new repo**. It lives in your user folder.

| OS | File path |
|----|-----------|
| **Windows** | `C:\Users\YOUR_WINDOWS_USER\.cursor\mcp.json` |
| **Mac** | `/Users/YOUR_MAC_USER/.cursor/mcp.json` |

Create or edit that file:

**Windows example:**

```json
{
  "mcpServers": {
    "modex-memory": {
      "command": "python",
      "args": ["C:\\Users\\YOUR_WINDOWS_USER\\remote_client.py"],
      "env": {
        "MODEX_API_URL": "https://agentic-data-platform-979112189932.asia-south1.run.app",
        "MODEX_API_KEY": "msk-7079ba3cdcf863affee3bbdea41b0485",
        "MODEX_AGENT_TOOL": "cursor",
        "MODEX_DEVELOPER_ID": "YOUR_NAME"
      }
    }
  }
}
```

**Mac example:**

```json
{
  "mcpServers": {
    "modex-memory": {
      "command": "python3",
      "args": ["/Users/YOUR_MAC_USER/remote_client.py"],
      "env": {
        "MODEX_API_URL": "https://agentic-data-platform-979112189932.asia-south1.run.app",
        "MODEX_API_KEY": "msk-7079ba3cdcf863affee3bbdea41b0485",
        "MODEX_AGENT_TOOL": "cursor",
        "MODEX_DEVELOPER_ID": "YOUR_NAME"
      }
    }
  }
}
```

Replace:

- `YOUR_WINDOWS_USER` / `YOUR_MAC_USER` — your login name
- `YOUR_NAME` — unique per person (`gagan`, `maanya`, `judge`, etc.)

**Antigravity:** same JSON in `~/.gemini/antigravity/mcp_config.json`, set `"MODEX_AGENT_TOOL": "antigravity"`.

---

## Step 5 — Add files INSIDE the new repo (commit once)

Open your **new repo folder** in Cursor. Create these two files:

### 5a — `.cursor/modex.json`

```json
{
  "project_repo": "github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME",
  "agent_tool": "cursor",
  "developer_id": "YOUR_NAME",
  "auto_hydrate": true
}
```

Replace `YOUR_GITHUB_USERNAME/YOUR_REPO_NAME` with your real repo slug from Step 1.

### 5b — `.cursor/rules/modex.mdc`

```markdown
---
description: MoDeX memory for this repo
alwaysApply: true
---

# MoDeX — this project only

Memory key for ALL MoDeX MCP calls:

`github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME`

## Session start
Call MCP `load_context` with:
`project_repo="github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME"`

## During work
After important decisions, call MCP `log_decision` with the same project_repo.

## Session end
Call MCP `compress_context` with the same project_repo so the next agent can resume.
```

Replace the slug in **all three places** in that file.

### 5c — Commit and push

```bash
git add .cursor/
git commit -m "Add MoDeX MCP config"
git push
```

Now anyone who clones this repo gets the correct memory key automatically.

---

## Step 6 — Restart Cursor

1. **Quit Cursor completely** (not just close the window).
2. Reopen Cursor.
3. **File → Open Folder** → select your **new repo root** (the folder that contains `.cursor/`).

---

## Step 7 — Verify MCP is connected

1. **Cursor → Settings → MCP**
2. Find **`modex-memory`**
3. It must show **Connected** and list these tools:
   - `load_context`
   - `append_codebase_log`
   - `log_decision`
   - `compress_context`
   - `save_session_memory`

If `modex-memory` is missing → fix Step 4 path, then repeat Step 6.

**Optional — test API key in terminal:**

```bash
curl -H "Authorization: Bearer msk-7079ba3cdcf863affee3bbdea41b0485" \
  https://agentic-data-platform-979112189932.asia-south1.run.app/api/v1/whoami
```

Expected: `{"status":"ok","developer_id":"..."}`

---

## Step 8 — Agent A: work and save memory (first person)

In Cursor chat, send:

```
Call load_context for github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.
If empty, say so and continue.
```

Do your coding work. When done, send:

```
For github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME:
1. log_decision for each important choice we made
2. call compress_context to save the handoff pack
```

Agent A's memory is now in the shared bus (BigQuery + Google Sheet).

---

## Step 9 — Agent B: continue on another PC (second person)

On the second machine:

1. Do **Step 2–4** (install mcp, download client, configure `~/.cursor/mcp.json`) — use a **different** `MODEX_DEVELOPER_ID`.
2. Clone the same repo:

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

3. **Step 6–7** (restart Cursor, verify MCP).
4. In chat:

```
Call load_context for github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.
Summarize: decisions, rejected approaches, files touched, last user ask.
Continue from there.
```

Agent B receives Agent A's full context. Demo complete.

---

## Checklist (print this)

```
[ ] GitHub repo exists
[ ] Memory key written down: github.com/___/___
[ ] pip install mcp
[ ] remote_client.py downloaded (full path noted)
[ ] ~/.cursor/mcp.json created with absolute path to remote_client.py
[ ] MODEX_DEVELOPER_ID set to my unique name
[ ] .cursor/modex.json in repo with correct project_repo
[ ] .cursor/rules/modex.mdc in repo with correct project_repo (3 places)
[ ] Files committed and pushed
[ ] Cursor fully restarted
[ ] Settings → MCP → modex-memory → Connected
[ ] load_context works
[ ] compress_context at end of session
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| MCP server not listed | Wrong path in `mcp.json` `args` — use **absolute** path to `remote_client.py` |
| MCP listed but red / error | Run `pip install mcp` again; check `MODEX_API_URL` and `MODEX_API_KEY` |
| `load_context` returns empty | Normal on first session — Agent A must run `compress_context` before Agent B can hydrate |
| Agent B sees nothing | Both used **different** `project_repo` strings — must match exactly |
| Tools work but wrong repo | Fix `.cursor/modex.json` and `.cursor/rules/modex.mdc`, commit, restart Cursor |

---

## What NOT to do

- Do **not** put GCP service account JSON in the new repo.
- Do **not** copy the hackathon `.cursor/hooks.json` unless you also set up GCP credentials locally.
- Do **not** use `github.com/Maanyaya/google-hackathon` as `project_repo` for your new repo — use **your** repo slug.

---

## Links

| Resource | URL |
|----------|-----|
| Live dashboard (Face 2) | https://agentic-data-platform-979112189932.asia-south1.run.app/dashboard/ |
| Full config (hooks, Face 2 local) | [CONFIGURATION.md](../CONFIGURATION.md) |
| Judge quick test | [JUDGES.md](../JUDGES.md) |
