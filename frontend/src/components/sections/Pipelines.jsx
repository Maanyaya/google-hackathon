import { Section, SectionHead } from "../ui/Section";
import { Reveal, RevealGroup } from "../ui/Reveal";
import { fmtRelative } from "../../lib/format";

function statusTone(s = "") {
  const v = s.toLowerCase();
  if (v.includes("sync") && !v.includes("error")) return "ok";
  if (v.includes("error") || v.includes("fail")) return "err";
  if (v.includes("paused")) return "warn";
  return "idle";
}

function PipelineCard({ p }) {
  const tone = p.paused ? "warn" : statusTone(p.status);
  return (
    <Reveal className="pipe-card card card-hover">
      <div className="pipe-card-top">
        <span className={`pipe-dot pipe-${tone}`} />
        <div className="pipe-id">
          <strong>{p.name || p.id}</strong>
          <span>{p.service}</span>
        </div>
        <span className={`pipe-status pipe-${tone}`}>{p.paused ? "paused" : (p.status || "—")}</span>
      </div>
      <div className="pipe-meta mono">
        <span>last sync {p.succeeded_at ? fmtRelative(p.succeeded_at) : "—"}</span>
        {p.sync_frequency ? <span>every {p.sync_frequency}m</span> : null}
      </div>
    </Reveal>
  );
}

function FreshTile({ label, value, sub, tone }) {
  return (
    <div className={`fresh-tile tone-${tone}`}>
      <span className="fresh-val">{value}</span>
      <span className="fresh-label">{label}</span>
      {sub && <span className="fresh-sub mono">{sub}</span>}
    </div>
  );
}

export function Pipelines({ pipelines, freshness }) {
  const list = pipelines?.pipelines || [];
  const err = pipelines && pipelines.status === "error";
  const main = freshness?.main_table;
  const face1 = freshness?.face1_memory;
  const meta = freshness?.metadata;

  return (
    <Section id="pipelines" theme="light" className="section-alt">
      <SectionHead
        eyebrow="Fivetran · managed data movement"
        title='Pipelines the agents <span class="grad-text">operate live</span>'
        lead="The Pipeline Operator agent reads connection health, triggers syncs, and runs dbt transformations through the Fivetran MCP — keeping shared memory fresh and provable."
      />

      <div className="pipe-grid-wrap">
        <div className="pipe-col">
          <h4 className="pipe-col-head">Connections <span>group · BigQuery destination</span></h4>
          {err || !list.length ? (
            <div className="pipe-empty card">
              <span className="pipe-dot pipe-idle" />
              Connector status loads from the Fivetran MCP on the deployed service.
            </div>
          ) : (
            <RevealGroup className="pipe-list">
              {list.map((p) => <PipelineCard key={p.id} p={p} />)}
            </RevealGroup>
          )}
        </div>

        <Reveal className="pipe-col">
          <h4 className="pipe-col-head">Freshness <span>BigQuery row counts</span></h4>
          <div className="fresh-grid">
            <FreshTile
              label="Fivetran-synced log rows"
              value={main?.row_count ?? "—"}
              sub={main?.last_synced ? `synced ${fmtRelative(main.last_synced)}` : "—"}
              tone="teal"
            />
            <FreshTile
              label="Session memory events"
              value={face1?.event_count ?? "—"}
              sub={face1?.last_event ? fmtRelative(face1.last_event) : "—"}
              tone="amber"
            />
            <FreshTile
              label="Platform metadata events"
              value={meta?.event_count ?? "—"}
              sub={meta?.dataset || "metadata"}
              tone="violet"
            />
            <FreshTile
              label="Lineage tracked"
              value={(freshness?.analytics_tables?.length ?? 0) > 0 ? "active" : "ready"}
              sub="source → destination"
              tone="sky"
            />
          </div>
        </Reveal>
      </div>
    </Section>
  );
}
