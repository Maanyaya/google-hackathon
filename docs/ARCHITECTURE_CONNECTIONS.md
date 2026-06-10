# MoDeX — How Everything Connects

> One page: what talks to what, and in which direction.

---

## 1. Bird's-eye view (two faces, one bus)

```mermaid
flowchart TB
    subgraph FACE1["FACE 1 — Developer edge"]
        IDE["Google Antigravity"]
        HOOKS["hook_runner.py"]
        MCP1["MoDeX MCP\n(remote_client.py)"]
        IDE -->|"prompts, edits, decisions"| HOOKS
        IDE -->|"load_context · log_decision · compress_context"| MCP1
    end

    subgraph API["Hosted API — Cloud Run"]
        F1API["Face 1 API\n/api/v1/*"]
        F2API["Face 2 ADK\nMission Control"]
        MCP1 -->|"HTTPS + API key"| F1API
        DASH["Dashboard UI"] --> F2API
    end

    subgraph BUS["MEMORY BUS"]
        BQ1["BigQuery\nagent_memory.codebase_logs"]
        SHEET["Google Sheet\nMoDex_Logs"]
        F1API -->|"append rows"| BQ1
        F1API -->|"mirror rows"| SHEET
        FT["Fivetran\n3 connectors"]
        SHEET -->|"stowed_register"| FT
        GH["GitHub"] -->|"solve_unhurt"| FT
        FTPLAT["Fivetran Platform"] -->|"elemental_apparel"| FT
        FT --> BQ2["BigQuery warehouse\nmodex_logs · github.*"]
    end

    subgraph FACE2["FACE 2 — Central Memory Guide"]
        MEM["Memory Agent"]
        PIPE["Pipeline Operator"]
        GUARD["Guardian"]
        F2API --> MEM
        F2API --> PIPE
        F2API --> GUARD
        MEM -->|"SQL query"| BQ1
        MEM -->|"SQL query"| BQ2
        PIPE -->|"Fivetran MCP"| FTMC["fivetran-mcp tools"]
        FTMC --> FT
    end

    subgraph AGENTB["Next agent"]
        IDE2["Agent B IDE\n(different developer_id)"]
        MCP1B["MoDeX MCP"] --> F1API
        F1API -->|"load_context"| IDE2
        MEM -->|"hydrate briefing"| DASH
    end

    BQ1 -.->|"read on hydrate"| MCP1B
```

---

## 2. Connection table (who connects to whom)

| From | To | Protocol / tool | What flows |
|------|-----|-----------------|------------|
| **Developer IDE** | `hook_runner.py` | Antigravity hooks | Raw IDE events (prompt, file edit, stop) |
| **Developer IDE** | **MoDeX MCP** | MCP over stdio | `load_context`, `log_decision`, `compress_context` |
| **MoDeX MCP** | **Cloud Run Face 1 API** | HTTPS + Bearer `msk-*` | JSON logs, decisions, session compress |
| **Face 1 API** | **BigQuery** | Streaming insert | `agent_memory.codebase_logs` rows |
| **Face 1 API** | **Google Sheet** | Sheets API | Human-readable mirror (`MoDex_Logs` tab) |
| **Google Sheet** | **Fivetran** | Connector `stowed_register` | Sheet → warehouse sync |
| **GitHub** | **Fivetran** | Connector `solve_unhurt` | PRs + reviews → `github.*` tables |
| **Fivetran Platform** | **Fivetran** | Connector `elemental_apparel` | Lineage + metadata → BigQuery |
| **Fivetran** | **BigQuery** | Managed sync | `modex_logs.modex_logs`, `github.*`, metadata |
| **Dashboard user** | **Face 2 ADK** | HTTPS `/api/mission` | Natural-language questions |
| **Mission Control** | **Memory Agent** | ADK transfer | Memory / hydrate / why questions |
| **Mission Control** | **Pipeline Operator** | ADK transfer | Pipeline health, sync, lineage |
| **Mission Control** | **Guardian** | ADK transfer | Approve writes (sync, export) |
| **Memory Agent** | **BigQuery** | SQL | Read `codebase_logs`, GitHub tables |
| **Pipeline Operator** | **Fivetran MCP** | MCP tools | `list_connections`, `sync_connection`, `get_connector_lineage` |
| **Fivetran MCP** | **Fivetran API** | REST (via MCP server) | Live connector ops |
| **Agent B MCP** | **Face 1 API** | `load_context` | Compressed session → IDE system context |
| **Secret Manager** | **Cloud Run** | Runtime injection | Fivetran API key + secret |

---

## 3. Face 1 path (capture) — step by step

```mermaid
sequenceDiagram
    participant Dev as Developer (Agent A)
    participant IDE as Antigravity
    participant Hook as hook_runner
    participant MCP as MoDeX MCP
    participant API as Cloud Run API
    participant BQ as BigQuery
    participant Sheet as Google Sheet

    Dev->>IDE: types prompt, edits files
    IDE->>Hook: hook event (auto)
    Hook->>API: append_codebase_log
    API->>BQ: insert row
    API->>Sheet: append row

    Dev->>IDE: "log decision: use FastAPI"
    IDE->>MCP: log_decision
    MCP->>API: POST decision
    API->>BQ: event_type=decision
    API->>Sheet: mirror

    Dev->>IDE: session ends
    IDE->>MCP: compress_context
    MCP->>API: context_compressed
    API->>BQ: session_summary + transcript_md
    API->>Sheet: session_summary column
```

---

## 4. Fivetran path (memory bus) — step by step

```mermaid
flowchart LR
    subgraph SOURCES
        S1["Google Sheet\nMoDex_Logs"]
        S2["GitHub\nPRs + reviews"]
        S3["Fivetran Platform\nmetadata"]
    end

    subgraph FIVETRAN
        C1["stowed_register"]
        C2["solve_unhurt"]
        C3["elemental_apparel"]
    end

    subgraph BIGQUERY
        T1["modex_logs.modex_logs"]
        T2["github.pull_request\npull_request_review"]
        T3["platform metadata\nlineage tables"]
    end

    S1 --> C1 --> T1
    S2 --> C2 --> T2
    S3 --> C3 --> T3

    T1 --> F2["Face 2 Memory Agent"]
    T2 --> F2
    T3 --> F2P["Face 2 Pipeline Operator"]
```

---

## 5. Face 2 path (answer + operate) — step by step

```mermaid
sequenceDiagram
    participant User as Judge / user
    participant Dash as Dashboard
    participant MC as Mission Control
    participant Mem as Memory Agent
    participant Pipe as Pipeline Operator
    participant BQ as BigQuery
    participant FT as Fivetran MCP

    User->>Dash: "Hydrate me on repo X"
    Dash->>MC: mission prompt
    MC->>Mem: transfer
    Mem->>BQ: query codebase_logs
    BQ-->>Mem: latest context_compressed
    Mem-->>Dash: briefing + citations

    User->>Dash: "Pipeline sync status?"
    Dash->>MC: mission prompt
    MC->>Pipe: transfer
    Pipe->>FT: list_connections
    FT-->>Pipe: connector status
    Pipe->>FT: get_connector_lineage
    FT-->>Pipe: lineage metadata
    Pipe-->>Dash: status + trace
```

---

## 6. Agent-to-agent handoff (the demo loop)

```mermaid
flowchart TB
    A["Agent A · PC1 · Antigravity\ndeveloper_id: judge"]
    B["Agent B · PC2 · Antigravity\ndeveloper_id: judge2"]
    REPO["Same GitHub repo\ngithub.com/.../hackathon-demo"]
    MEM["Shared memory slug\nsame project_repo"]

    A -->|"code + git push"| REPO
    A -->|"log_decision · compress_context"| MEM
    MEM -->|"Fivetran sync"| BQ["BigQuery"]
    B -->|"git pull"| REPO
    B -->|"load_context"| MEM
    MEM -->|"decisions + rejected paths"| B

    style A fill:#1a3a5c
    style B fill:#1a4a3c
    style MEM fill:#3a2a1a
```

**Key rule:** Same `project_repo` slug + **different** `developer_id` = shared memory with two authors.

---

## 7. Google Cloud components (what runs where)

```mermaid
flowchart TB
    subgraph GCP["Google Cloud — gen-lang-client-0795401430"]
        CR["Cloud Run\nagentic-data-platform"]
        BQ["BigQuery\nagent_memory + modex_logs + github"]
        SM["Secret Manager\nFivetran credentials"]
        VAI["Vertex AI\nGemini 2.5 Flash"]
        CR --> BQ
        SM --> CR
        VAI --> CR
    end

    subgraph PARTNER["Fivetran — partner account"]
        FT["Fivetran MCP + 3 connectors"]
    end

    CR -->|"Pipeline Operator calls"| FT
    FT --> BQ
```

---

## 8. One-sentence summary

**Face 1** writes memory from the IDE → **BigQuery + Sheet** → **Fivetran** keeps the warehouse fresh → **Face 2** reads and operates on that bus → **Agent B** loads the same memory via **MCP** and continues where **Agent A** stopped.
