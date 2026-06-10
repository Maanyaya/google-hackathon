# MoDeX — Hackathon Submission

> **Google Cloud Rapid Agent Hackathon** · **Fivetran Track** · Team MoDeX

---

## Try it now

| Resource | Link |
|----------|------|
| **Hosted project (live dashboard)** | https://agentic-data-platform-979112189932.asia-south1.run.app/dashboard/ |
| **Demo video (≤ 3 min)** | https://youtu.be/_-O5sinN4qY |
| **GitHub repository** | https://github.com/Maanyaya/google-hackathon |
| **License** | Apache 2.0 — visible in repo About section |
| **DevPost** | https://rapid-agent.devpost.com/ |
| **Judge guide + MCP keys** | [JUDGES.md](JUDGES.md) |

---

## What we submitted

**Project name:** MoDeX — Memory of Codex

**Elevator pitch:** AI coding agents forget everything when sessions end. MoDeX gives them shared persistent memory — captured live, synced by Fivetran to BigQuery, recalled by Gemini ADK.

**Track:** Fivetran

**Built with:** Gemini 2.5 Flash · Google ADK · Cloud Run · BigQuery · Secret Manager · Fivetran MCP

---

## How judges can evaluate (3 steps)

### 1. Try Face 2 — no install (2 minutes)

Open the [dashboard](https://agentic-data-platform-979112189932.asia-south1.run.app/dashboard/) → **Ask Face 2** → try:

```
Hydrate me on github.com/Maanyaya/google-hackathon
```

```
What is the sync status of the MoDeX logs pipeline? Check Platform Connector metadata for freshness and lineage.
```

### 2. Test Face 1 MCP (5 minutes)

See [JUDGES.md](JUDGES.md) for pre-provisioned API keys (`judge` + `judge2`). No GCP signup required.

### 3. Watch the demo video

[YouTube — full walkthrough](https://youtu.be/_-O5sinN4qY) · timestamps synced on the [dashboard Demo section](https://agentic-data-platform-979112189932.asia-south1.run.app/dashboard/#demo)

| Time | Chapter |
|------|---------|
| 0:00 | Meet MoDeX |
| 0:14 | Two faces, one system |
| 0:27 | The memory bus (Fivetran + BigQuery) |
| 0:45 | Face 1 — MCP in the IDE |
| 1:28 | Agent handoff — zero cold start |
| 2:32 | Fivetran connectors → BigQuery |
| 3:37 | Face 2 — pipeline trust (Fivetran MCP live) |
| 4:02 | Try it yourself |

---

## Architecture (one line)

**Face 1 MCP** captures IDE memory → **BigQuery + Google Sheet** → **Fivetran** syncs warehouse → **Face 2 ADK** answers and operates pipelines live → **Agent B** hydrates via `load_context`.

See [docs/ARCHITECTURE_CONNECTIONS.md](docs/ARCHITECTURE_CONNECTIONS.md) for the full connection map.

---

## Hosted infrastructure

MoDeX runs on our **Google Cloud** project (`gen-lang-client-0795401430`) with **Fivetran** connectors pre-configured. Judges test with public API keys — the architecture is multi-tenant: any team can point MCP at the hosted URL with their own `project_repo` slug.
