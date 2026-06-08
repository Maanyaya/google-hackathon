import { Panel, MetricCard } from "../ui/Panel";
import { fmtRelative } from "../../lib/format";

export function HeroMetrics({ overview, freshness, memory, loading }) {
  const f1 = freshness?.face1_memory;
  const ft = freshness?.main_table;

  return (
    <section id="overview" className="ui-hero-metrics animate-in">
      <MetricCard
        accent="memory"
        label="Codebase events"
        value={f1?.event_count ?? "—"}
        hint={f1?.last_event ? `Last ${fmtRelative(f1.last_event)}` : "Face 1 · MCP writes"}
        loading={loading}
      />
      <MetricCard
        accent="pipeline"
        label="Fivetran synced rows"
        value={ft?.row_count ?? "—"}
        hint={ft?.last_synced ? `Synced ${fmtRelative(ft.last_synced)}` : "modex_logs bus"}
        loading={loading}
      />
      <MetricCard
        accent="agent"
        label="Active agents"
        value={overview?.agent_count ?? 7}
        hint="Mission Control + 6 specialists"
        loading={loading && !overview}
      />
      <MetricCard
        accent="code"
        label="Demo repo"
        value={memory?.memories?.length ? "live" : "—"}
        hint="github.com/demo/api-service"
        loading={loading && !memory}
      />
    </section>
  );
}

export function ArchitectureFlow({ overview }) {
  return (
    <Panel title="Memory pipeline" subtitle="Two faces · one shared reasoning bus" glow className="animate-in delay-1">
      <div className="ui-arch-flow">
        <div className="ui-arch-node ui-arch-face1">
          <span className="ui-arch-badge">Face 1</span>
          <h3>Developer edge</h3>
          <p>Cursor · Antigravity · Windsurf MCP append session events in real time.</p>
          <code>{overview?.agent_memory_table?.split(".").slice(-2).join(".") || "agent_memory.codebase_logs"}</code>
        </div>
        <div className="ui-arch-bridge">
          <div className="ui-arch-bridge-line" />
          <div className="ui-arch-bridge-chip">Fivetran</div>
          <div className="ui-arch-bridge-line" />
        </div>
        <div className="ui-arch-node ui-arch-face2">
          <span className="ui-arch-badge">Face 2</span>
          <h3>Agent platform</h3>
          <p>7 ADK agents query memory, operate pipelines, trace provenance, govern writes.</p>
          <code>{overview?.fivetran_modex_connection || "stowed_register"} → modex_logs</code>
        </div>
      </div>
    </Panel>
  );
}
