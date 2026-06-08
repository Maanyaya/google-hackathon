import { Panel, Skeleton } from "../ui/Panel";
import { SyncRing } from "../../lib/icons";
import { fmtRelative } from "../../lib/format";

function PipelineRow({ p, highlight }) {
  const ok = !p.paused && (p.status === "scheduled" || p.status === "synced");
  const pct = ok ? 92 : p.paused ? 40 : 15;
  const color = ok ? "#0DDBBE" : p.paused ? "#FFBE4D" : "#FF6B6B";

  return (
    <div className={`ui-pipeline-row ${highlight ? "highlight" : ""}`}>
      <div className="ui-pipeline-ring">
        <SyncRing pct={pct} color={color} size={48} />
        <span className="ui-pipeline-pct">{pct}%</span>
      </div>
      <div className="ui-pipeline-body">
        <div className="ui-pipeline-title">{p.name || p.id}</div>
        <div className="ui-pipeline-meta">{p.service} · <span className="font-mono">{p.id}</span></div>
      </div>
      <div className="ui-pipeline-status">
        <span className={`ui-status-label ui-status-${ok ? "ok" : p.paused ? "warn" : "err"}`}>
          {p.paused ? "Paused" : p.status}
        </span>
        {p.succeeded_at && <span className="ui-pipeline-time">{fmtRelative(p.succeeded_at)}</span>}
      </div>
    </div>
  );
}

export function PipelineHealth({ pipelines, highlightId, timeline, loading }) {
  const items = pipelines?.pipelines || [];
  const events = timeline?.events || [];

  return (
    <section id="pipelines" className="ui-split-row animate-in delay-3">
      <Panel title="Fivetran pipelines" subtitle="Managed sync · MCP operable">
        {loading && !items.length ? (
          <div className="space-y-3">{[1, 2, 3].map((i) => <Skeleton key={i} className="h-16 rounded-xl" />)}</div>
        ) : items.length === 0 ? (
          <p className="ui-empty">No connections returned from Fivetran MCP.</p>
        ) : (
          items.map((p) => (
            <PipelineRow key={p.id} p={p} highlight={p.id === highlightId} />
          ))
        )}
      </Panel>

      <Panel title="Pipeline telemetry" subtitle="Platform Connector · last events">
        {events.length === 0 ? (
          <p className="ui-empty">No metadata events yet.</p>
        ) : (
          <div className="ui-event-list scrollbar-thin">
            {events.slice(0, 10).map((ev, i) => (
              <div key={i} className="ui-event-row">
                <span className={`ui-event-dot ui-event-${(ev.event || "").toLowerCase()}`} />
                <div className="ui-event-body">
                  <div className="ui-event-title">{ev.message_event || ev.event}</div>
                  <div className="ui-event-sub">{ev.message_data?.slice(0, 80) || ev.connection_id}</div>
                </div>
                <time className="ui-event-time">{fmtRelative(ev.time_stamp)}</time>
              </div>
            ))}
          </div>
        )}
      </Panel>
    </section>
  );
}
