import { Section, SectionHead } from "../ui/Section";
import { Reveal, RevealGroup } from "../ui/Reveal";
import { AGENT_META, FACE2_AGENDA } from "../../lib/theme";

const FRAMEWORK = ["Gemini", "Google ADK", "Fivetran MCP", "Cloud Run"];

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

function AgentCard({ a }) {
  const meta = AGENT_META[a.id] || { letter: "AI", short: "" };
  return (
    <Reveal className="agent-card card card-hover" style={{ "--agent": a.color }}>
      <div className="agent-card-head">
        <span className="agent-badge">{meta.letter}</span>
        <div>
          <h3 className="agent-name">{a.label}</h3>
          <span className="agent-role">{meta.short}</span>
        </div>
      </div>
      <p className="agent-desc">{a.description}</p>
      <ToolChips tools={a.tools} max={5} />
      <div className="agent-foot">
        {a.mcp ? <span className="agent-mcp">{a.mcp}</span> : null}
        {a.policy ? <span className="agent-mcp agent-policy">{a.policy}</span> : null}
      </div>
    </Reveal>
  );
}

export function Agents({ topology, loading }) {
  const agents = topology?.agents || [];
  const byId = Object.fromEntries(agents.map((a) => [a.id, a]));
  const capabilityAgents = ["memory_agent", "pipeline_agent", "action_agent"]
    .map((id) => byId[id])
    .filter(Boolean);

  return (
    <Section id="agents" theme="light">
      <SectionHead
        eyebrow="Face 2 · why we built it"
        title='A <span class="grad-text">centralized memory guide</span> that actually answers'
        lead="Face 1 MCP proved agents can capture reasoning into the bus. Face 2 exists so anyone can ask that bus real questions — and operate the Fivetran-managed connectors that keep it fresh. No orchestrator theater: three clear jobs, cited answers."
      />

      <RevealGroup className="face2-agenda">
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

      <Reveal className="agent-framework">
        {FRAMEWORK.map((f) => <span key={f} className="agent-fw-badge">{f}</span>)}
      </Reveal>

      {loading && !topology ? (
        <div className="dec-empty">Loading capabilities…</div>
      ) : (
        <RevealGroup className="agent-grid">
          {capabilityAgents.map((a) => <AgentCard key={a.id} a={a} />)}
        </RevealGroup>
      )}
    </Section>
  );
}
