# Fivetran-centric environment — enhancement checklist

MoDeX is submitted on the **Fivetran track**. Judges expect Fivetran to be the **hero**, not background plumbing. Use this checklist to verify and strengthen the Fivetran story.

---

## What “Fivetran-centric” means for MoDeX

| Layer | What judges should see |
|-------|------------------------|
| **Data movement** | 3 connectors → BigQuery warehouse |
| **Partner MCP** | Pipeline Operator calls `fivetran-mcp` live in agent trace |
| **Metadata / trust** | Platform Connector lineage in BigQuery |
| **Action** | Sync triggered (Guardian-gated) — not read-only |
| **UI** | Dashboard **Fivetran** section shows connectors + freshness + lineage |

---

## Step 1 — Verify Cloud Run secrets (critical)

Fivetran MCP only works if these are set on Cloud Run:

```bash
# Secrets in Google Secret Manager:
#   fivetran-api-key
#   fivetran-api-secret

gcloud run services describe agentic-data-platform \
  --region asia-south1 \
  --project gen-lang-client-0795401430 \
  --format="yaml(spec.template.spec.containers[0].env)"
```

**Expected:** `FIVETRAN_API_KEY` and `FIVETRAN_API_SECRET` from Secret Manager refs.

**If missing:** add secrets and redeploy:

```bash
gcloud run deploy agentic-data-platform \
  --source . \
  --region asia-south1 \
  --set-secrets=FIVETRAN_API_KEY=fivetran-api-key:latest,FIVETRAN_API_SECRET=fivetran-api-secret:latest
```

---

## Step 2 — Verify connectors in Fivetran console

| Connector ID | Purpose | Destination table |
|--------------|---------|-------------------|
| `stowed_register` | MoDeX Logs (Google Sheet) | `modex_logs.modex_logs` |
| `solve_unhurt` | GitHub PRs + reviews | `github.*` |
| `elemental_apparel` | Platform Connector | `fivetran_metadata_solve_unhurt.*` |

In Fivetran UI: confirm all three are **connected** and have synced at least once.

---

## Step 3 — Verify BigQuery landed data

```sql
-- Fivetran-synced session logs
SELECT COUNT(*), MAX(_fivetran_synced)
FROM `gen-lang-client-0795401430.modex_logs.modex_logs`;

-- Platform metadata (lineage)
SELECT COUNT(*) FROM `gen-lang-client-0795401430.fivetran_metadata_solve_unhurt.table_lineage`;

-- Sync event log
SELECT time_stamp, connection_id, event
FROM `gen-lang-client-0795401430.fivetran_metadata_solve_unhurt.log`
ORDER BY time_stamp DESC LIMIT 10;
```

---

## Step 4 — Test Fivetran MCP from the dashboard API

```bash
curl https://agentic-data-platform-979112189932.asia-south1.run.app/api/dashboard/fivetran-hub
```

**Expected in response:**
- `connectors` — 3 catalog entries (live status if MCP works)
- `freshness` — row counts
- `lineage` — source → destination rows (if Platform Connector synced)
- `sync_timeline` — recent metadata log events

---

## Step 5 — Test Face 2 Fivetran missions (judge path)

Open dashboard → **Ask Face 2** → run:

```
What is the sync status of the MoDeX logs pipeline? Check Platform Connector metadata for freshness and lineage.
```

**Judge must see in agent trace:**
- Route to **Fivetran Operations** / Pipeline Operator
- Tool calls: `fivetran_list_connections`, `get_connection_details`, or BigQuery metadata queries

Optional write path:

```
Check stowed_register connector health. If stale, request approval to trigger a resync.
```

---

## Step 6 — Dashboard Fivetran section (UI)

After deploy, open:

https://agentic-data-platform-979112189932.asia-south1.run.app/dashboard/#fivetran

**Shows:**
- IDE → Fivetran MCP → BigQuery → Face 2 flow
- All 3 connectors with IDs (even if MCP partial)
- Warehouse freshness tiles
- Lineage from Platform Connector
- Link to Google Sheet + “Ask Face 2 — pipeline trust”

Nav item: **Fivetran** (first-class, not buried under Pipelines).

---

## Step 7 — Demo video beats (Fivetran-specific)

Ensure your video includes (~2:32 and ~3:37):

1. Fivetran console or dashboard connector cards
2. Google Sheet → BigQuery mention
3. Face 2 agent trace with Fivetran MCP tool names visible
4. Say: *“data trust, not just data sync”*

---

## Common gaps (why it feels “not built yet”)

| Symptom | Cause | Fix |
|---------|-------|-----|
| Pipelines section empty | Fivetran secrets missing on Cloud Run | Step 1 |
| Face 2 doesn’t call Fivetran tools | Prompt too memory-focused | Use pipeline trust chip |
| No lineage rows | Platform Connector never synced | Run sync in Fivetran UI |
| GitHub tables empty | GitHub connector paused | Unpause + sync in Fivetran |
| MCP timeout on Cloud Run | `uvx` cold start | Retry; increase Cloud Run timeout |

---

## Architecture reference

Full connection map: [ARCHITECTURE_CONNECTIONS.md](./ARCHITECTURE_CONNECTIONS.md)

Judge guide: [JUDGES.md](../JUDGES.md)
