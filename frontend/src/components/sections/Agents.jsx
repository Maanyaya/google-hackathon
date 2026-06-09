/**
 * Agents — Face 2 agent framework explanation.
 * Leads with the ADK architecture (what framework, what pattern), then shows
 * the three specialist agents with their actual tool lists.
 */
import { Section, SectionHead } from "../ui/Section";
import { Reveal, RevealGroup } from "../ui/Reveal";
import { AGENT_META, FACE2_AGENDA } from "../../lib/theme";

/* ── ADK framework overview ── */
const FRAMEWORK_STACK = [
  {
    name: "Google ADK",
    color: "var(--violet)",
    desc: "Agent Development Kit — the orchestration layer. Defines agents, tools, and routing rules declaratively.",
    detail: "Multi-agent pattern: one orchestrator routes to three specialists. Each specialist has a bounded tool set — no agent can call a tool it doesn't own.",
  },
  {
    name: "Gemini 2.5 Flash",
    color: "var(--amber)",
    desc: "Model powering every specialist. Fast enough for interactive demo queries (30–90s end-to-end).",
    detail: "gemini-2.5-flash · Vertex AI · retry_options(attempts=3) to survive transient quota errors.",
  },
  {
    name: "Fivetran MCP",
    color: "var(--teal)",
    desc: "The pipeline_agent calls Fivetran MCP tools live — not mocked, not hardcoded.",
    detail: "fivetran_list_connections · fivetran_get_connector_details · fivetran_sync_connector. Operates the real stowed_register + GitHub connectors.",
  },
  {
    name: "Cloud Run",
    color: "var(--sky)",
    desc: "Both the MCP API (Face 1) and the ADK agent app (Face 2) are deployed on the same Cloud Run service.",
    detail: "One URL, two surfaces: /api/v1 (MCP + bearer auth) and /dev-ui (ADK live agent). Scales to zero between sessions.",
  },
];

/* ── three specialist agents with concrete tool lists ── */
const SPECIALISTS = [
  {
    id: "memory_agent",
    letter: "MA",
    color: "var(--amber)",
    name: "Memory Agent",
    tagline: "Retrieval brain — answers from the shared bus",
    role: "Handles all 'what did the team decide / why / what was rejected / hydrate me' questions. Fuses coding-agent session logs with GitHub PR reviews synced by Fivetran.",
    tools: [
      { name: "get_team_context", desc: "Builds context pack from session logs + GitHub PRs" },
      { name: "get_decision_memory", desc: "Decision graph with freshness counts" },
      { name: "get_codebase_log_timeline", desc: "Raw session event replay" },
      { name: "get_modex_fivetran_logs", desc: "Events on the Fivetran bus" },
      { name: "query_bigquery", desc: "SELECT-only SQL (incl. GitHub tables)" },
      { name: "search_knowledge_base", desc: "Vertex AI RAG for conceptual questions" },
    ],
  },
  {
    id: "pipeline_agent",
    letter: "FO",
    color: "var(--teal)",
    name: "Pipeline Agent",
    tagline: "Fivetran operator — health, sync, lineage",
    role: "Operates the Fivetran connectors that keep the memory bus fresh. Reports health, triggers syncs, reads lineage — all within the conversation.",
    tools: [
      { name: "fivetran_list_connections", desc: "List connectors + group membership" },
      { name: "fivetran_get_connector_details", desc: "Status, succeeded_at, schema" },
      { name: "fivetran_sync_connector", desc: "Trigger a manual sync" },
      { name: "fivetran_get_connector_schema", desc: "Column-level lineage" },
      { name: "get_data_catalog", desc: "Discover BigQuery tables" },
      { name: "get_table_schema", desc: "Column types + descriptions" },
    ],
  },
  {
    id: "action_agent",
    letter: "GA",
    color: "var(--violet)",
    name: "Action Agent",
    tagline: "Governed writes — you approve before anything changes",
    role: "Prepares exports and writes (GCS, Sheets, notifications), but never executes silently. Every action is gated behind an explicit human approval step.",
    tools: [
      { name: "export_decisions_to_gcs", desc: "Stage a standup export to Cloud Storage" },
      { name: "push_report_to_sheet", desc: "Append a summary row to Google Sheets" },
      { name: "guardian_approve", desc: "Human approval gate — required before any write" },
      { name: "get_team_context", desc: "Load context before preparing export" },
    ],
  },
];

function ToolRow({ tool }) {
  return (
    <div className="spec-tool-row">
      <code className="spec-tool-name">{tool.name}</code>
      <span className="spec-tool-desc">{tool.desc}</span>
    </div>
  );
}

function SpecialistCard({ s }) {
  return (
    <Reveal className="spec-card card" style={{ "--sc": s.color }}>
      <div className="spec-card-head">
        <span className="spec-badge">{s.letter}</span>
        <div>
          <h3 className="spec-name">{s.name}</h3>
          <span className="spec-tagline">{s.tagline}</span>
        </div>
      </div>
      <p className="spec-role">{s.role}</p>
      <div className="spec-tools-label">Tools</div>
      <div className="spec-tools">
        {s.tools.map((t) => <ToolRow key={t.name} tool={t} />)}
      </div>
    </Reveal>
  );
}

function FrameworkCard({ f }) {
  return (
    <div className="fw-card card" style={{ "--fwc": f.color }}>
      <div className="fw-card-name" style={{ color: f.color }}>{f.name}</div>
      <p className="fw-card-desc">{f.desc}</p>
      <p className="fw-card-detail mono">{f.detail}</p>
    </div>
  );
}

export function Agents({ topology, loading }) {
  const agents = topology?.agents || [];
  const byId = Object.fromEntries(agents.map((a) => [a.id, a]));

  return (
    <Section id="agents" theme="light">
      <SectionHead
        eyebrow="Face 2 · agent framework"
        title={`Built with Google ADK + <span class="grad-text">Gemini 2.5 Flash</span>`}
        lead="Face 2 is not a generic chatbot. It is a multi-agent system built on Google ADK where each specialist agent has a bounded tool set and a single clear job. The orchestrator routes silently — users get answers, not delegation narration."
      />

      {/* ADK framework stack */}
      <Reveal>
        <div className="fw-stack-label eyebrow" style={{ marginBottom: "1.2rem" }}>Framework stack</div>
        <div className="fw-grid">
          {FRAMEWORK_STACK.map((f) => <FrameworkCard key={f.name} f={f} />)}
        </div>
      </Reveal>

      {/* orchestration pattern */}
      <Reveal className="adk-pattern card">
        <div className="adk-pattern-left">
          <div className="adk-pattern-title">Multi-agent routing pattern</div>
          <p className="adk-pattern-desc">
            One <strong>orchestrator_agent</strong> receives every question. It decides which
            specialist can answer — it never answers directly. This keeps tool permissions
            minimal and makes the trace readable.
          </p>
        </div>
        <div className="adk-pattern-diagram">
          <div className="adk-orch-box">orchestrator_agent</div>
          <div className="adk-routes">
            {["memory_agent", "pipeline_agent", "action_agent"].map((id) => (
              <div key={id} className="adk-route-line">
                <svg width="32" height="2" viewBox="0 0 32 2" fill="none">
                  <line x1="0" y1="1" x2="32" y2="1" stroke="currentColor" strokeWidth="1.2" strokeDasharray="3 2" />
                </svg>
                <code className="adk-spec-label">{id}</code>
              </div>
            ))}
          </div>
        </div>
      </Reveal>

      {/* three specialists */}
      <div className="spec-grid-label eyebrow" style={{ marginTop: "3rem", marginBottom: "1.2rem" }}>
        Three specialists — each with its own tool set
      </div>
      {loading && !topology ? (
        <div className="dec-empty">Loading agent capabilities…</div>
      ) : (
        <RevealGroup className="spec-grid">
          {SPECIALISTS.map((s) => <SpecialistCard key={s.id} s={s} />)}
        </RevealGroup>
      )}

      {/* Face 2 agenda recap */}
      <RevealGroup className="face2-agenda" style={{ marginTop: "3rem" }}>
        {FACE2_AGENDA.map((item) => (
          <div key={item.id} className="face2-agenda-card card">
            <span className="face2-agenda-n">{item.n}</span>
            <h3 className="face2-agenda-title">{item.title}</h3>
            <p className="face2-agenda-desc">{item.desc}</p>
            <ul className="face2-agenda-examples">
              {item.examples.map((ex) => (
                <li key={ex}>{ex}</li>
              ))}
            </ul>
          </div>
        ))}
      </RevealGroup>
    </Section>
  );
}
