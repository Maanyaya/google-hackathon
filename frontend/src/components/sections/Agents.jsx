import { Section, SectionHead } from "../ui/Section";
import { Reveal, RevealGroup } from "../ui/Reveal";
import { AGENT_META } from "../../lib/theme";

const FRAMEWORK = ["Gemini", "Google ADK", "MCP tools", "Cloud Run"];

function ToolChips({ tools = [], max = 5 }) {
  const shown = tools.slice(0, max);
  const extra = tools.length - shown.length;
  return (
    <div className="agent-tools">
      {shown.map((t) => <code key={t} className="agent-tool">{t}</code>)}
      {extra > 0 && <code className="agent-tool agent-tool-more">+{extra}</code>}
    </div>
  );
}

function AgentCard({ a, lead }) {
  const meta = AGENT_META[a.id] || { letter: "AI", short: "" };
  return (
    <Reveal className={`agent-card card card-hover ${lead ? "agent-lead" : ""}`} style={{ "--agent": a.color }}>
      <div className="agent-card-head">
        <span className="agent-badge">{meta.letter}</span>
        <div>
          <h3 className="agent-name">{a.label}</h3>
          <span className="agent-role">{lead ? "Orchestrator" : meta.short}</span>
        </div>
        {lead && <span className="agent-lead-tag">root agent</span>}
      </div>
      <p className="agent-desc">{a.description}</p>
      <ToolChips tools={a.tools} max={lead ? 4 : 5} />
      <div className="agent-foot">
        {a.mcp ? <span className="agent-mcp">⚙ {a.mcp}</span> : null}
        {a.policy ? <span className="agent-mcp agent-policy">🛡 {a.policy}</span> : null}
        {a.delegates_to?.length ? (
          <span className="agent-delegates">→ delegates to {a.delegates_to.length} specialists</span>
        ) : null}
      </div>
    </Reveal>
  );
}

export function Agents({ topology, loading }) {
  const agents = topology?.agents || [];
  const lead = agents.find((a) => a.id === "orchestrator_agent");
  const specialists = agents.filter((a) => a.id !== "orchestrator_agent");

  return (
    <Section id="agents" theme="light">
      <SectionHead
        eyebrow="Face 2 · the agent framework"
        title='A team of agents, <span class="grad-text">one governed brain</span>'
        lead="This is what runs on Face 2. Built on Google ADK and Gemini, Mission Control plans and delegates to three specialist sub-agents — each with its own MCP tools. Every write is gated by a human-in-the-loop Guardian policy."
      />

      <Reveal className="agent-framework">
        {FRAMEWORK.map((f) => <span key={f} className="agent-fw-badge">{f}</span>)}
      </Reveal>

      {loading && !topology ? (
        <div className="dec-empty">Loading agent topology…</div>
      ) : (
        <>
          {lead && (
            <RevealGroup className="agent-lead-wrap">
              <AgentCard a={lead} lead />
            </RevealGroup>
          )}
          <Reveal className="agent-delegate-rail" aria-hidden>
            <span className="agent-rail-label">delegates to</span>
          </Reveal>
          <RevealGroup className="agent-grid">
            {specialists.map((a) => <AgentCard key={a.id} a={a} />)}
          </RevealGroup>
        </>
      )}
    </Section>
  );
}
