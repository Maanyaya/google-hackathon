/**
 * FivetranHub — partner-track centerpiece: connectors, lineage, sync bus.
 */
import { Section, SectionHead } from "../ui/Section";
import { Reveal, RevealGroup } from "../ui/Reveal";
import { fmtRelative } from "../../lib/format";

function FlowStep({ label, sub, tone }) {
  return (
    <div className={`ft-flow-step tone-${tone}`}>
      <span className="ft-flow-label">{label}</span>
      <span className="ft-flow-sub">{sub}</span>
    </div>
  );
}

function ConnectorCard({ c }) {
  const live = c.live;
  const tone = c.paused ? "warn" : live && String(c.status).toLowerCase().includes("synced") ? "ok" : live ? "idle" : "catalog";
  return (
    <div className={`ft-conn card${c.featured ? " ft-conn-featured" : ""}`}>
      <div className="ft-conn-top">
        <div>
          <strong className="ft-conn-name">{c.name}</strong>
          <code className="ft-conn-id">{c.id}</code>
        </div>
        <span className={`ft-conn-status ft-${tone}`}>
          {c.paused ? "paused" : c.status || "catalog"}
        </span>
      </div>
      <div className="ft-conn-flow">
        <span>{c.source}</span>
        <span className="ft-arrow">→</span>
        <span>{c.destination}</span>
      </div>
      <p className="ft-conn-role">{c.role}</p>
      {c.succeeded_at && (
        <span className="ft-conn-meta mono">last sync {fmtRelative(c.succeeded_at)}</span>
      )}
      {!live && (
        <span className="ft-conn-meta ft-catalog-note">Catalog entry · live status via Fivetran MCP</span>
      )}
    </div>
  );
}

export function FivetranHub({ hub, onNav }) {
  const connectors = hub?.connectors || [];
  const fresh = hub?.freshness?.main_table;
  const face1 = hub?.freshness?.face1_memory;
  const meta = hub?.freshness?.metadata;
  const lineage = hub?.lineage || [];
  const timeline = hub?.sync_timeline || [];
  const sheetUrl = hub?.sheet_url;

  return (
    <Section id="fivetran" theme="dark" aurora className="section-fivetran">
      <SectionHead
        eyebrow="Fivetran track · partner superpower"
        title={`The <span class="grad-text">memory bus</span> Fivetran keeps fresh`}
        lead="MoDeX is not MoDeX without Fivetran. Three connectors move session logs, GitHub PRs, and Platform Connector metadata into BigQuery — and the Pipeline Operator agent operates them live via fivetran-mcp."
      />

      {/* Data flow */}
      <Reveal className="ft-flow">
        <FlowStep label="IDE + Sheet" sub="Face 1 writes session memory" tone="sky" />
        <span className="ft-flow-arrow">→</span>
        <FlowStep label="Fivetran MCP" sub="list · sync · lineage" tone="teal" />
        <span className="ft-flow-arrow">→</span>
        <FlowStep label="BigQuery" sub="warehouse + metadata" tone="amber" />
        <span className="ft-flow-arrow">→</span>
        <FlowStep label="Face 2 agent" sub="answer + operate" tone="violet" />
      </Reveal>

      {hub?.mcp_error && (
        <Reveal className="ft-mcp-banner">
          <span className="ft-mcp-warn">MCP note:</span> {hub.mcp_error}
          {" "}Connectors below still show the configured catalog; live status requires Fivetran secrets on Cloud Run.
        </Reveal>
      )}

      {/* Connectors */}
      <RevealGroup className="ft-conn-grid">
        {connectors.map((c) => (
          <ConnectorCard key={c.id} c={c} />
        ))}
      </RevealGroup>

      {/* Freshness + actions */}
      <div className="ft-metrics-row">
        <Reveal className="ft-metrics card">
          <h4 className="ft-metrics-head">Warehouse freshness</h4>
          <div className="ft-metrics-grid">
            <div className="ft-metric">
              <span className="ft-metric-val">{fresh?.row_count ?? "—"}</span>
              <span className="ft-metric-label">Fivetran-synced log rows</span>
              {fresh?.last_synced && (
                <span className="ft-metric-sub mono">synced {fmtRelative(fresh.last_synced)}</span>
              )}
            </div>
            <div className="ft-metric">
              <span className="ft-metric-val">{face1?.event_count ?? "—"}</span>
              <span className="ft-metric-label">Face 1 memory events</span>
            </div>
            <div className="ft-metric">
              <span className="ft-metric-val">{meta?.event_count ?? "—"}</span>
              <span className="ft-metric-label">Platform metadata events</span>
            </div>
          </div>
          <div className="ft-metrics-actions">
            {sheetUrl && (
              <a className="btn btn-ghost btn-sm" href={sheetUrl} target="_blank" rel="noreferrer">
                Open Google Sheet ↗
              </a>
            )}
            <button type="button" className="btn btn-primary btn-sm" onClick={() => onNav?.("ask")}>
              Ask Face 2 — pipeline trust
            </button>
          </div>
        </Reveal>

        <Reveal className="ft-lineage card">
          <h4 className="ft-metrics-head">Lineage · Platform Connector</h4>
          {lineage.length ? (
            <ul className="ft-lineage-list scrollbar-thin">
              {lineage.slice(0, 6).map((row, i) => (
                <li key={i}>
                  <code>{row.source_table || "source"}</code>
                  <span className="ft-arrow">→</span>
                  <code>{row.destination_table || "dest"}</code>
                </li>
              ))}
            </ul>
          ) : (
            <p className="ft-empty">Lineage populates from `{hub?.destinations?.metadata_dataset || "fivetran_metadata"}`.table_lineage after Platform Connector syncs.</p>
          )}
        </Reveal>
      </div>

      {/* Sync timeline */}
      {timeline.length > 0 && (
        <Reveal className="ft-timeline card">
          <h4 className="ft-metrics-head">Recent sync events · Fivetran metadata log</h4>
          <ul className="ft-timeline-list scrollbar-thin">
            {timeline.slice(0, 8).map((ev, i) => (
              <li key={i}>
                <span className="mono ft-timeline-ts">
                  {ev.time_stamp ? fmtRelative(ev.time_stamp) : "—"}
                </span>
                <code className="ft-timeline-conn">{ev.connection_id || "—"}</code>
                <span>{ev.event || ev.message_event || "sync event"}</span>
              </li>
            ))}
          </ul>
        </Reveal>
      )}
    </Section>
  );
}
