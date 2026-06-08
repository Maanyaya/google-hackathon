import { useState } from "react";
import { Panel, Skeleton } from "../ui/Panel";
import { AGENT_META } from "../../lib/theme";

export function AgentConstellation({ agents, loading }) {
  const [active, setActive] = useState(null);
  if (loading && !agents?.length) {
    return (
      <Panel id="agents" title="Agent constellation" subtitle="Click a node to inspect tools">
        <div className="ui-agent-skeleton-grid">
          {Array.from({ length: 7 }).map((_, i) => (
            <Skeleton key={i} className="h-24 rounded-2xl" />
          ))}
        </div>
      </Panel>
    );
  }
  if (!agents?.length) return null;

  const hub = agents.find((a) => a.id === "orchestrator_agent");
  const ring = agents.filter((a) => a.id !== "orchestrator_agent");
  const selected = active ? agents.find((a) => a.id === active) : null;

  return (
    <Panel id="agents" title="Agent constellation" subtitle="Mission Control delegates to specialists · click to inspect" className="animate-in delay-2">
      <div className="ui-constellation">
        <svg className="ui-constellation-lines" viewBox="0 0 800 320" preserveAspectRatio="xMidYMid meet">
          {ring.map((a, i) => {
            const angle = (i / ring.length) * Math.PI * 2 - Math.PI / 2;
            const x = 400 + Math.cos(angle) * 280;
            const y = 160 + Math.sin(angle) * 110;
            return (
              <line key={a.id} x1="400" y1="160" x2={x} y2={y} stroke={active === a.id ? a.color : "rgba(255,255,255,0.06)"} strokeWidth={active === a.id ? 2 : 1} strokeDasharray={active === a.id ? "0" : "4 4"} />
            );
          })}
        </svg>

        <div className="ui-constellation-hub">
          <button type="button" className={`ui-agent-node ui-agent-hub ${active === hub?.id ? "active" : ""}`} style={{ "--c": hub?.color }} onClick={() => setActive(hub?.id)}>
            <span className="ui-agent-node-letter">{AGENT_META[hub?.id]?.letter || "MC"}</span>
            <span className="ui-agent-node-name">{hub?.label}</span>
          </button>
        </div>

        <div className="ui-constellation-ring">
          {ring.map((a) => (
            <button
              key={a.id}
              type="button"
              className={`ui-agent-node ${active === a.id ? "active" : ""}`}
              style={{ "--c": a.color }}
              onClick={() => setActive(active === a.id ? null : a.id)}
            >
              <span className="ui-agent-node-letter">{AGENT_META[a.id]?.letter || "?"}</span>
              <span className="ui-agent-node-name">{a.label}</span>
              <span className="ui-agent-node-short">{AGENT_META[a.id]?.short}</span>
            </button>
          ))}
        </div>
      </div>

      {selected && (
        <div className="ui-agent-inspector animate-in">
          <div className="ui-agent-inspector-head">
            <span className="ui-agent-inspector-dot" style={{ background: selected.color }} />
            <strong>{selected.label}</strong>
            <span className="ui-agent-inspector-id">{selected.id}</span>
          </div>
          <p>{selected.description}</p>
          {selected.mcp && <div className="ui-agent-inspector-mcp">{selected.mcp}</div>}
          <div className="ui-tool-grid">
            {(selected.tools || selected.delegates_to || []).map((t) => (
              <span key={t} className="ui-tool-tag">{t}</span>
            ))}
          </div>
        </div>
      )}
    </Panel>
  );
}
