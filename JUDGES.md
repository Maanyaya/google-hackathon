# MoDeX — Judge & evaluator setup

Use this guide to test **Face 1 (MCP)** and **Face 2 (Central Memory Guide)** without any GCP credentials.

**GitHub repo:** https://github.com/Maanyaya/google-hackathon  
**Live dashboard:** https://agentic-data-platform-979112189932.asia-south1.run.app/dashboard/  
**Setup panel in UI:** scroll to **Setup & docs** on the dashboard

---

## Architecture (30 seconds)

```
Face 1 MCP (Cursor/Antigravity)  ──write/read──►  BigQuery memory bus  ◄── Fivetran (GitHub, Sheets)
                                                          │
Face 2 Central Memory Guide  ◄── answers + Fivetran ops ──┘
Dashboard  ◄── live context pack, decisions, pipelines
```

| Face | What it does | How judges test it |
|------|----------------|-------------------|
| **Face 1** | Captures & hydrates coding-agent reasoning via MCP | Install MCP below, call `load_context` |
| **Bus** | Fivetran + BigQuery — centralized, cited memory | See **Pipelines** + **Context pack** on dashboard |
| **Face 2** | Answers memory questions + operates Fivetran | Click **Ask Face 2** → *Hydrate me* |

---

## Judge MCP credentials (Face 1)

| Field | Value |
|-------|--------|
| **Service URL** | `https://agentic-data-platform-979112189932.asia-south1.run.app` |
| **Judge API key** | `msk-7079ba3cdcf863affee3bbdea41b0485` |
| **Developer ID** | `judge` (stamped on every event you log) |
| **Demo repo** | `github.com/demo/api-service` |

### Verify the key

```bash
curl -H "Authorization: Bearer msk-7079ba3cdcf863affee3bbdea41b0485" \
  https://agentic-data-platform-979112189932.asia-south1.run.app/api/v1/whoami
```

Expected: `{"status":"ok","developer_id":"judge"}`

---

## Install Face 1 MCP (5 minutes)

### 1. Install dependency

```bash
pip install mcp
```

### 2. Download the thin client (one file)

```bash
curl -o remote_client.py \
  https://raw.githubusercontent.com/Maanyaya/google-hackathon/main/modex_mcp/remote_client.py
```

Or copy from this repo: `modex_mcp/remote_client.py`

### 3. Configure your IDE

**Cursor** — `~/.cursor/mcp.json` (Windows: `%USERPROFILE%\.cursor\mcp.json`)

Copy from [`docs/mcp-cursor-judge.json`](docs/mcp-cursor-judge.json) and set `args` to the **absolute path** of `remote_client.py`.

**Antigravity** — `~/.gemini/antigravity/mcp_config.json`

Copy from [`docs/mcp-antigravity-judge.json`](docs/mcp-antigravity-judge.json).

### 4. Restart IDE → confirm MCP connected

In Cursor: Settings → MCP → `modex-memory` should show tools:
`load_context`, `append_codebase_log`, `log_decision`, …

### 5. Test prompts

Ask your coding agent:

```
Call load_context for github.com/demo/api-service and summarize adopted decisions and rejected approaches.
```

```
Log a decision: "Judge verified MoDeX MCP from hackathon eval" using append_codebase_log.
```

Refresh the dashboard **Context pack** section — your event should appear.

---

## Face 2 (no install)

Open the dashboard → **Ask Face 2** → try:

1. **Hydrate me** — memory answer with PR citations  
2. **Why this stack?** — PostgreSQL vs MongoDB provenance  
3. **Pipeline health** — live Fivetran MCP  

---

## Fivetran integration (what to look for)

| Connector | ID | Feeds |
|-----------|-----|--------|
| MoDeX logs (Sheet) | `stowed_register` | `modex_logs.modex_logs` |
| GitHub | (group `solve_unhurt`) | PRs, reviews → decision cross-reference |
| Platform Connector | `elemental_apparel` | Lineage + freshness metadata |

Face 2 **Pipeline health** mission calls Fivetran MCP live.

---

## Links

| Resource | URL |
|----------|-----|
| Dashboard | https://agentic-data-platform-979112189932.asia-south1.run.app/dashboard/ |
| API health | …/api/v1/health |
| MCP README | [modex_mcp/README.md](modex_mcp/README.md) |
| Architecture | [ARCHITECTURE.md](ARCHITECTURE.md) |

---

*MoDeX — Face 1 proved capture. Face 2 proved the bus is answerable. Fivetran keeps it fresh.*
