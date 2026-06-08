import { Section, SectionHead } from "../ui/Section";
import { Reveal } from "../ui/Reveal";
import { fmtRelative } from "../../lib/format";

function PackLine({ line }) {
  if (!line.trim()) return <div className="pk-blank" />;
  if (line.startsWith("# ")) return <div className="pk-h1">{line.slice(2)}</div>;
  if (line.startsWith("## ")) return <div className="pk-h2">{line.slice(3)}</div>;
  if (line.startsWith("Freshness:")) return <div className="pk-meta">{line}</div>;
  if (line.trimStart().startsWith("cited:")) return <div className="pk-cite">{line.trim()}</div>;

  if (line.startsWith("- ")) {
    const body = line.slice(2);
    const corro = /\[corroborated\]/.test(body);
    const clean = body.replace("[corroborated]", "").trim();
    return (
      <div className="pk-li">
        <span className="pk-bullet" />
        <span>
          {clean}
          {corro && <span className="pk-badge pk-badge-ok">corroborated</span>}
        </span>
      </div>
    );
  }
  return <div className="pk-text">{line}</div>;
}

function Stat({ value, label, tone }) {
  return (
    <div className={`pk-stat tone-${tone}`}>
      <span className="pk-stat-val">{value}</span>
      <span className="pk-stat-label">{label}</span>
    </div>
  );
}

export function ContextPack({ pack, loading }) {
  const counts = pack?.counts;
  const fresh = pack?.freshness;
  const lines = (pack?.hydration_prompt || "").split("\n");

  return (
    <Section id="pack" theme="light">
      <SectionHead
        eyebrow="The deliverable"
        title='The <span class="grad-text">context pack</span>, served on demand'
        lead="This is the exact artifact a new coding agent receives from a single MCP call — curated, cross-referenced, and provenance-stamped. Not a fuzzy vector blob: every line is dated and cited."
      />

      <div className="pack-grid">
        <Reveal className="pack-doc">
          <div className="pack-doc-head">
            <div className="cpp-dots"><span /><span /><span /></div>
            <span className="mono pack-doc-name">context-pack.md</span>
            <span className="pill pill-live pack-doc-badge"><span className="dot" />load_context</span>
          </div>
          <div className="pack-doc-body scrollbar-thin">
            {loading && !pack ? (
              <div className="pk-text">Building context pack…</div>
            ) : lines.length ? (
              lines.map((l, i) => <PackLine key={i} line={l} />)
            ) : (
              <div className="pk-text">No context yet — capture a session via the MCP server.</div>
            )}
          </div>
        </Reveal>

        <div className="pack-side">
          <Reveal className="pack-stats">
            <Stat value={counts?.decisions ?? "—"} label="Decisions" tone="amber" />
            <Stat value={counts?.corroborated ?? "—"} label="Corroborated" tone="teal" />
            <Stat value={counts?.rejected ?? "—"} label="Rejected" tone="rose" />
            <Stat value={counts?.gotchas ?? "—"} label="Gotchas" tone="violet" />
          </Reveal>

          <Reveal className="pack-fresh card">
            <h4>Provenance &amp; freshness</h4>
            <div className="pack-fresh-row">
              <span className="pf-dot tone-sky" />
              <div>
                <strong>Session memory</strong>
                <span>{fresh?.session_last_event ? fmtRelative(fresh.session_last_event) : "—"}</span>
              </div>
            </div>
            <div className="pack-fresh-row">
              <span className="pf-dot tone-amber" />
              <div>
                <strong>Sheet mirror via Fivetran</strong>
                <span>
                  {fresh?.sheet_last_synced
                    ? `synced ${fmtRelative(fresh.sheet_last_synced)} · ${fresh?.sheet_row_count ?? 0} rows`
                    : "—"}
                </span>
              </div>
            </div>
            <div className="pack-fresh-row">
              <span className="pf-dot tone-teal" />
              <div>
                <strong>GitHub via Fivetran</strong>
                <span>{fresh?.github_last_synced ? `synced ${fmtRelative(fresh.github_last_synced)}` : "—"}</span>
              </div>
            </div>
            <div className="pack-fresh-src mono">
              source: {fresh?.github_source || "demo"} · conn {fresh?.fivetran_connection?.slice(0, 14) || "fivetran"}…
            </div>
          </Reveal>

          <Reveal className="pack-note">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M12 2L3 7v6c0 5 3.5 8 9 9 5.5-1 9-4 9-9V7l-9-5z" stroke="var(--amber-deep)" strokeWidth="1.5" fill="rgba(245,166,35,0.1)" /><path d="M9 12l2 2 4-4" stroke="var(--amber-deep)" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" /></svg>
            <p>Governed retrieval: precise SQL for cited facts, optional Vertex AI RAG for conceptual grounding. The agent trusts it because it can <strong>verify every source</strong>.</p>
          </Reveal>
        </div>
      </div>
    </Section>
  );
}
