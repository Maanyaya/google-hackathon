/**
 * FlowDiagram — full data-pipeline visualization.
 * Shows the exact path from IDE keystrokes → BigQuery → Sheet → Fivetran → Agent B.
 * Rendered as pure React/CSS (no external library required).
 */
import { Reveal } from "../ui/Reveal";
import { Section, SectionHead } from "../ui/Section";

/* ---------- primitive pieces ---------- */

function Node({ color, icon, title, sub, chips = [], mono, wide }) {
  return (
    <div className={`fd-node${wide ? " fd-node-wide" : ""}`} style={{ "--nc": color }}>
      <div className="fd-node-icon" aria-hidden>{icon}</div>
      {mono
        ? <code className="fd-node-title fd-mono">{title}</code>
        : <div className="fd-node-title">{title}</div>}
      {sub && <div className="fd-node-sub">{sub}</div>}
      {chips.length > 0 && (
        <div className="fd-chips">
          {chips.map((c) => <span key={c} className="fd-chip">{c}</span>)}
        </div>
      )}
    </div>
  );
}

function Arrow({ label, vertical, dim }) {
  return (
    <div className={`fd-arrow${vertical ? " fd-arrow-v" : ""}${dim ? " fd-arrow-dim" : ""}`}>
      {label && <span className="fd-arrow-label">{label}</span>}
      <svg
        className="fd-arrow-svg"
        width={vertical ? 14 : 48}
        height={vertical ? 48 : 14}
        viewBox={vertical ? "0 0 14 48" : "0 0 48 14"}
        fill="none"
      >
        {vertical ? (
          <>
            <line x1="7" y1="0" x2="7" y2="40" stroke="currentColor" strokeWidth="1.4" strokeDasharray="3 2" />
            <path d="M3 37l4 6 4-6" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" fill="none" />
          </>
        ) : (
          <>
            <line x1="0" y1="7" x2="40" y2="7" stroke="currentColor" strokeWidth="1.4" strokeDasharray="3 2" />
            <path d="M37 3l6 4-6 4" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" fill="none" />
          </>
        )}
      </svg>
    </div>
  );
}

function Lane({ label, color, children }) {
  return (
    <div className="fd-lane" style={{ "--lc": color }}>
      <span className="fd-lane-label">{label}</span>
      <div className="fd-lane-body">{children}</div>
    </div>
  );
}

function SplitRow({ children }) {
  return <div className="fd-split">{children}</div>;
}

/* ---------- icon SVGs (inline, minimal) ---------- */
const Ico = {
  ide: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
      <rect x="2.5" y="4" width="19" height="14" rx="2.5" stroke="currentColor" strokeWidth="1.6" />
      <path d="M7 9l2.5 2.5L7 14M12 14h5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  ),
  hook: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
      <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  ),
  bq: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
      <ellipse cx="12" cy="7" rx="8" ry="3" stroke="currentColor" strokeWidth="1.6" />
      <path d="M4 7v5c0 1.657 3.582 3 8 3s8-1.343 8-3V7" stroke="currentColor" strokeWidth="1.6" />
      <path d="M4 12v5c0 1.657 3.582 3 8 3s8-1.343 8-3v-5" stroke="currentColor" strokeWidth="1.6" />
    </svg>
  ),
  sheet: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
      <rect x="3" y="3" width="18" height="18" rx="2.5" stroke="currentColor" strokeWidth="1.6" />
      <path d="M3 9h18M9 9v12M3 14h18" stroke="currentColor" strokeWidth="1.6" />
    </svg>
  ),
  fivetran: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
      <circle cx="5" cy="12" r="2.5" stroke="currentColor" strokeWidth="1.6" />
      <circle cx="19" cy="12" r="2.5" stroke="currentColor" strokeWidth="1.6" />
      <path d="M7.5 12h9" stroke="currentColor" strokeWidth="1.6" strokeDasharray="2 1.5" />
      <path d="M12 5v4M12 15v4" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
    </svg>
  ),
  github: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
      <path d="M12 2C6.48 2 2 6.48 2 12c0 4.42 2.87 8.17 6.84 9.49.5.09.68-.22.68-.48v-1.7c-2.78.6-3.37-1.34-3.37-1.34-.45-1.15-1.1-1.46-1.1-1.46-.9-.62.07-.6.07-.6 1 .07 1.53 1.02 1.53 1.02.89 1.52 2.34 1.08 2.91.83.09-.64.35-1.08.63-1.33-2.22-.25-4.55-1.11-4.55-4.94 0-1.09.39-1.98 1.03-2.68-.1-.25-.45-1.27.1-2.65 0 0 .84-.27 2.75 1.02A9.56 9.56 0 0112 6.8c.85 0 1.7.11 2.5.33 1.91-1.29 2.75-1.02 2.75-1.02.55 1.38.2 2.4.1 2.65.64.7 1.03 1.59 1.03 2.68 0 3.84-2.34 4.69-4.57 4.93.36.31.68.92.68 1.85v2.74c0 .27.18.58.69.48A10 10 0 0022 12c0-5.52-4.48-10-10-10z" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  ),
  agent: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
      <circle cx="12" cy="8" r="3.5" stroke="currentColor" strokeWidth="1.6" />
      <circle cx="5" cy="18" r="2.5" stroke="currentColor" strokeWidth="1.6" />
      <circle cx="19" cy="18" r="2.5" stroke="currentColor" strokeWidth="1.6" />
      <path d="M10 11l-3.5 5M14 11l3.5 5M7.5 18h9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  ),
};

/* ---------- main component ---------- */

export function FlowDiagram() {
  return (
    <Section id="flow" theme="dark" aurora>
      <SectionHead
        eyebrow="Data pipeline · end to end"
        title={`From IDE keystroke to <span class="grad-text">Agent B hydration</span>`}
        lead="Every captured thought travels through this exact path. Both agents share the same memory — not by passing files, but by reading from the same BigQuery + Fivetran bus."
      />

      <Reveal className="fd-root">
        {/* ── ROW 1: IDE capture ── */}
        <Lane label="FACE 1 — capture" color="var(--sky)">
          <div className="fd-row">
            <Node
              color="var(--sky)"
              icon={Ico.ide}
              title="Agent A works in Cursor"
              sub="types a prompt → edits files → makes decisions"
              chips={["beforeSubmitPrompt", "afterAgentResponse", "postToolUse", "afterFileEdit", "stop"]}
            />
            <Arrow label="hooks fire (UTF-16LE decoded)" />
            <Node
              color="var(--sky)"
              icon={Ico.hook}
              title="hook_runner.py"
              sub="Parses payload, maps to event_type, appends to memory store"
              chips={["user_prompt", "agent_response", "file_edit", "tool_call", "context_compressed"]}
              mono
            />
          </div>
        </Lane>

        <Arrow vertical label="write (streaming insert)" />

        {/* ── ROW 2: memory bus ── */}
        <Lane label="MEMORY BUS — Fivetran + BigQuery" color="var(--teal)">
          <SplitRow>
            <Node
              color="var(--amber)"
              icon={Ico.bq}
              title="BigQuery"
              sub="agent_memory.codebase_logs (append-only, 15 cols)"
              chips={["summary", "context_json", "transcript_md", "session_summary"]}
            />
            <Arrow label="mirrored in real-time" />
            <Node
              color="var(--teal)"
              icon={Ico.sheet}
              title="Google Sheet · MoDex_Logs"
              sub="Human-readable + Fivetran source"
              chips={["session_summary paragraph", "transcript_md briefing", "context_json pack"]}
            />
            <Arrow label="Fivetran stowed_register syncs" />
            <Node
              color="var(--teal)"
              icon={Ico.fivetran}
              title="modex_logs.modex_logs"
              sub="Warehouse table — queryable by Face 2 + any agent"
              chips={["_fivetran_synced", "provenance"]}
            />
          </SplitRow>

          <div className="fd-also-synced">
            <span className="fd-also-label">Also synced by Fivetran →</span>
            <Node
              color="var(--violet)"
              icon={Ico.github}
              title="GitHub PRs + reviews"
              sub="connector: solve_unhurt"
              chips={["pull_request", "pull_request_review"]}
            />
          </div>
        </Lane>

        <Arrow vertical label="load_context() or handoff hydrate" />

        {/* ── ROW 3: Face 2 + Agent B ── */}
        <Lane label="FACE 2 — answer + operate" color="var(--violet)">
          <div className="fd-row">
            <Node
              color="var(--violet)"
              icon={Ico.agent}
              title="Central Memory Guide"
              sub="ADK multi-agent · Gemini 2.5 Flash · Cloud Run"
              chips={["memory_agent", "pipeline_agent", "action_agent"]}
            />
            <Arrow label="delivers context pack" />
            <Node
              color="var(--green)"
              icon={Ico.ide}
              title="Agent B (any IDE)"
              sub="Antigravity · Cursor · Windsurf on any machine"
              chips={["decisions loaded", "rejected approaches known", "zero cold start"]}
            />
          </div>
        </Lane>
      </Reveal>

      {/* ── legend ── */}
      <Reveal className="fd-legend">
        {[
          { color: "var(--sky)", label: "Face 1 capture (MCP + hooks)" },
          { color: "var(--teal)", label: "Memory bus (Fivetran + BigQuery)" },
          { color: "var(--violet)", label: "Face 2 answer & operate" },
          { color: "var(--green)", label: "Agent B hydration" },
        ].map((l) => (
          <div key={l.label} className="fd-legend-item">
            <span className="fd-legend-dot" style={{ background: l.color }} />
            <span>{l.label}</span>
          </div>
        ))}
      </Reveal>
    </Section>
  );
}
