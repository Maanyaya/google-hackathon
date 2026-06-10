# Hackathon compliance — Section 7B (AI tools)

This project complies with **Google Cloud Rapid Agent Hackathon Section 7B**:

> Only **Google Cloud AI tools** (Gemini models, Google Cloud Agent Builder) and your **track partner's built-in AI** (Fivetran MCP) are permitted in the final product **and** in the development workflow.

## Permitted in this repository

| Category | Technology | Where used |
|----------|------------|------------|
| Core AI | **Gemini 2.5 Flash** (Vertex AI) | Face 2 multi-agent system (`app/`) |
| Agent framework | **Google ADK** | Orchestrator + specialists |
| Deployment | **Cloud Run**, BigQuery, Secret Manager | Hosted platform |
| Partner AI | **Fivetran MCP** (`fivetran-mcp`) | Pipeline Operator tools |
| Dev workflow | **Google Antigravity** | Face 1 MCP + optional hooks (`.agents/`) |

## Not present in this repository

The following are **not** dependencies, integrations, or documented setup paths:

- Claude / Anthropic
- Cursor
- GitHub Copilot
- OpenAI APIs (no `openai` usage in application code; runtime uses `google-adk` + Vertex only)
- Other competing coding assistants (Windsurf, etc.)

## Face 1 setup path for judges

Use **Antigravity only**:

1. [docs/ANTIGRAVITY_MCP_SETUP.md](./ANTIGRAVITY_MCP_SETUP.md)
2. [docs/mcp-antigravity-judge.json](./mcp-antigravity-judge.json)
3. [docs/JUDGE_MCP_CREDENTIALS.md](./JUDGE_MCP_CREDENTIALS.md)

Config file: `~/.gemini/antigravity/mcp_config.json`  
Project config: `.agents/modex.json` in your repo

## Verify before submission

From the repo root:

```powershell
python scripts/check_hackathon_compliance.py
```

Exit code `0` = no forbidden competitor references in tracked source/docs (excluding CSS `cursor: pointer` and compliance docs that name forbidden tools).

## What we removed from git

- `.cursor/` IDE config (competitor product)
- `docs/mcp-cursor-judge.json` and `docs/new-repo-mcp-cursor.json`

Local developer machines may still have personal IDE configs **outside** this repo; they are not part of the submission artifact.

## Runtime AI stack (Face 2)

All LLM calls go through **Vertex AI Gemini** via ADK. See dashboard **Stack** section or `app/specialists.py` — no alternate model providers.
