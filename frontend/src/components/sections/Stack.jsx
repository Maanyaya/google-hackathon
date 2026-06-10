/**
 * Stack — explicit Google Cloud + Fivetran integration showcase.
 * This section exists purely for judges and evaluators to verify
 * the full technology stack and partner integrations.
 */
import { Reveal, RevealGroup } from "../ui/Reveal";
import { Section, SectionHead } from "../ui/Section";

/* ── Google Cloud stack ─────────────────────────── */
const GCP_STACK = [
  {
    name: "Gemini 2.5 Flash",
    role: "Agent reasoning — all Face 2 multi-agent responses",
    detail: "Orchestrator + 3 specialist agents run on Gemini 2.5 Flash via Vertex AI. No OpenAI, no Anthropic.",
    color: "var(--amber)",
    badge: "Core AI",
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
        <path d="M12 2l2.5 7.5H22l-6.5 4.7 2.5 7.5L12 17l-6 4.7 2.5-7.5L2 9.5h7.5L12 2z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
      </svg>
    ),
  },
  {
    name: "ADK (Agent Dev Kit)",
    role: "Multi-agent orchestration framework",
    detail: "google.adk — Mission Control routes to Memory Agent, Pipeline Operator, Guardian. Each has a bounded tool set.",
    color: "var(--violet)",
    badge: "Framework",
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="7" r="3" stroke="currentColor" strokeWidth="1.6" />
        <circle cx="5" cy="18" r="2.5" stroke="currentColor" strokeWidth="1.6" />
        <circle cx="19" cy="18" r="2.5" stroke="currentColor" strokeWidth="1.6" />
        <path d="M10 9.5L6 15.6M14 9.5l4 6.1M7.5 18h9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    name: "BigQuery",
    role: "Ground truth memory store + destination",
    detail: "agent_memory.codebase_logs (append-only, 15 cols). Also: modex_logs.modex_logs (Fivetran destination) and github.* tables.",
    color: "var(--sky)",
    badge: "Destination",
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
        <ellipse cx="12" cy="7" rx="8" ry="3" stroke="currentColor" strokeWidth="1.6" />
        <path d="M4 7v5c0 1.66 3.58 3 8 3s8-1.34 8-3V7" stroke="currentColor" strokeWidth="1.6" />
        <path d="M4 12v5c0 1.66 3.58 3 8 3s8-1.34 8-3v-5" stroke="currentColor" strokeWidth="1.6" />
      </svg>
    ),
  },
  {
    name: "Cloud Run",
    role: "Serverless deployment — both faces on one service",
    detail: "Face 1 API + Face 2 ADK app + dashboard served from one Cloud Run revision (asia-south1). Scales to zero.",
    color: "var(--teal)",
    badge: "Deployed",
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
        <rect x="3" y="5" width="18" height="14" rx="2.5" stroke="currentColor" strokeWidth="1.6" />
        <path d="M8 12l3 3 5-6" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
  {
    name: "Secret Manager",
    role: "Fivetran API credentials — never in env vars",
    detail: "fivetran-api-key + fivetran-api-secret stored as GCP secrets. Cloud Run injects at runtime via secretKeyRef.",
    color: "var(--rose)",
    badge: "Security",
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
        <rect x="5" y="11" width="14" height="10" rx="2" stroke="currentColor" strokeWidth="1.6" />
        <path d="M8 11V7a4 4 0 0 1 8 0v4" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
        <circle cx="12" cy="16" r="1.2" fill="currentColor" />
      </svg>
    ),
  },
  {
    name: "Vertex AI RAG",
    role: "Knowledge grounding for Memory Agent",
    detail: "RAG corpus in europe-west3 (4.6T token budget). Memory Agent grounds answers in synced GitHub + session logs.",
    color: "#7C8AFF",
    badge: "Grounding",
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
        <path d="M4 6h16M4 10h10M4 14h12M4 18h8" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
        <circle cx="19" cy="16" r="3.5" stroke="currentColor" strokeWidth="1.5" />
        <path d="M21.5 18.5l1.5 1.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      </svg>
    ),
  },
];

/* ── Fivetran connectors ────────────────────────── */
const FIVETRAN_CONNECTORS = [
  {
    id: "stowed_register",
    name: "MoDeX Logs",
    source: "Google Sheets · MoDex_Logs tab",
    dest: "BigQuery · modex_logs.modex_logs",
    role: "Turns every IDE session's memory into a queryable warehouse table. Face 2 reads from this table.",
    badge: "Session memory",
    color: "var(--amber)",
  },
  {
    id: "solve_unhurt",
    name: "GitHub PRs",
    source: "GitHub · PRs + reviews",
    dest: "BigQuery · github.pull_request, github.pull_request_review",
    role: "Grounds decisions in code review history. Memory Agent cross-references decisions with PR #s.",
    badge: "Code context",
    color: "var(--sky)",
  },
  {
    id: "elemental_apparel",
    name: "Platform Connector",
    source: "Fivetran Platform Connector",
    dest: "BigQuery · pipeline metadata + lineage",
    role: "Provides data trust and lineage. Face 2 queries freshness, schema changes, and pipeline health.",
    badge: "Lineage + trust ★",
    color: "var(--violet)",
    star: true,
  },
];

/* ── Fivetran MCP tools ─────────────────────────── */
const MCP_TOOLS = [
  { name: "list_connections", desc: "All connector statuses in one call" },
  { name: "get_connection_details", desc: "Schema, sync history, error details" },
  { name: "sync_connection", desc: "Trigger resync — Guardian-gated" },
  { name: "get_transformation_details", desc: "dbt project status + run logs" },
  { name: "get_connector_lineage", desc: "Platform Connector OpenLineage metadata" },
];

export function Stack() {
  return (
    <Section id="stack" theme="light">
      <SectionHead
        eyebrow="Built with · full technology stack"
        title={`Google Cloud + Fivetran <span class="grad-text">integrations</span>`}
        lead="MoDeX is built entirely on Google Cloud (Gemini ADK, BigQuery, Cloud Run) with Fivetran as the data movement partner. Every connection and tool is real — not mocked."
      />

      {/* ── Google Cloud ── */}
      <Reveal>
        <h3 className="stack-group-head">
          <span className="stack-group-badge tone-amber">Google Cloud</span>
          Core platform
        </h3>
      </Reveal>
      <RevealGroup className="stack-grid">
        {GCP_STACK.map((s) => (
          <div className="stack-card card" key={s.name} style={{ "--sc": s.color }}>
            <div className="stack-card-top">
              <span className="stack-icon" style={{ color: s.color }}>{s.icon}</span>
              <span className="stack-badge" style={{ background: `${s.color}18`, color: s.color }}>{s.badge}</span>
            </div>
            <div className="stack-name">{s.name}</div>
            <div className="stack-role">{s.role}</div>
            <div className="stack-detail">{s.detail}</div>
          </div>
        ))}
      </RevealGroup>

      {/* ── Fivetran MCP (partner integration) ── */}
      <Reveal>
        <div className="stack-partner-banner">
          <div className="stack-partner-left">
            <span className="stack-partner-badge">Partner Integration · Fivetran MCP</span>
            <h3 className="stack-partner-head">The "partner superpower" — Fivetran MCP</h3>
            <p className="stack-partner-lead">
              Face 2's Pipeline Operator calls <strong>fivetran-mcp</strong> live. Not REST API — not simulated.
              The agent trace shows every tool call. Judges can see{" "}
              <code>list_connections</code>, <code>sync_connection</code>, and{" "}
              <code>get_connector_lineage</code> fire in real-time.
            </p>
            <div className="stack-mcp-tools">
              {MCP_TOOLS.map((t) => (
                <div className="stack-mcp-tool" key={t.name}>
                  <code>{t.name}</code>
                  <span>{t.desc}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="stack-partner-connectors">
            <span className="stack-partner-sub">3 live connectors → BigQuery</span>
            {FIVETRAN_CONNECTORS.map((c) => (
              <div className="stack-connector" key={c.id} style={{ "--cc": c.color }}>
                <div className="stack-conn-head">
                  <span className="stack-conn-name">{c.name}</span>
                  <span className="stack-conn-badge" style={{ color: c.color }}>{c.badge}</span>
                </div>
                <div className="stack-conn-flow">
                  <span className="stack-conn-source">{c.source}</span>
                  <svg width="20" height="10" viewBox="0 0 20 10" fill="none" aria-hidden>
                    <path d="M0 5h14M12 2l4 3-4 3" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                  <span className="stack-conn-dest">{c.dest}</span>
                </div>
                <div className="stack-conn-role">{c.role}</div>
              </div>
            ))}
          </div>
        </div>
      </Reveal>
    </Section>
  );
}
