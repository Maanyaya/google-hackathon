import { Section, SectionHead } from "../ui/Section";
import { Reveal, RevealGroup } from "../ui/Reveal";
import { fmtRelative } from "../../lib/format";

const CONF = {
  corroborated: { label: "corroborated", cls: "ok" },
  "session-only": { label: "session only", cls: "soft" },
  "github-only": { label: "github only", cls: "violet" },
};

function SourceChip({ s }) {
  if (s.type === "github_pr") {
    return (
      <span className="src-chip src-pr" title={s.review || s.title}>
        <span className="src-ico">PR</span>#{s.number} · {s.who}
      </span>
    );
  }
  return (
    <span className="src-chip src-session">
      <span className="src-ico">SES</span>{s.tool || "session"} · {s.who || "agent"}
    </span>
  );
}

function DecisionCard({ d }) {
  const conf = CONF[d.confidence] || CONF["session-only"];
  const review = d.sources?.find((s) => s.review)?.review;
  return (
    <Reveal className="dec-card card card-hover">
      <div className="dec-card-top">
        <span className={`dec-status dec-${d.status}`}>{d.status}</span>
        <span className={`dec-conf dec-conf-${conf.cls}`}>{conf.label}</span>
      </div>
      <h3 className="dec-title">{d.decision}</h3>
      {review && <p className="dec-review">&ldquo;{review.replace(/^[^:]+:\s*/, "")}&rdquo;</p>}
      <div className="dec-sources">
        {(d.sources || []).slice(0, 3).map((s, i) => <SourceChip key={i} s={s} />)}
      </div>
    </Reveal>
  );
}

export function Decisions({ decisions, loading }) {
  const adopted = (decisions?.decisions || []).filter((d) => d.status !== "rejected");
  const rejected = decisions?.rejected || [];
  const counts = decisions?.counts;

  return (
    <Section id="decisions" theme="light" className="section-alt">
      <SectionHead
        eyebrow="Cross-referenced decision memory"
        title='What the team decided — and <span class="grad-text">what it rejected</span>'
        lead="Each decision fuses the coding-agent session that made it with the GitHub PR and reviewer reasoning that confirms it. Rejected approaches are first-class — so no agent ever redoes a dead-end."
      />

      <RevealGroup className="dec-grid">
        {loading && !decisions ? (
          <div className="dec-empty">Loading decision memory…</div>
        ) : adopted.length ? (
          adopted.slice(0, 6).map((d, i) => <DecisionCard key={i} d={d} />)
        ) : (
          <div className="dec-empty">No decisions captured yet.</div>
        )}
      </RevealGroup>

      {rejected.length > 0 && (
        <Reveal className="rejected-block">
          <div className="rejected-head">
            <span className="rejected-icon">✕</span>
            <h3>Dead-ends the team already explored</h3>
            <span className="rejected-count">{rejected.length} rejected</span>
          </div>
          <div className="rejected-grid">
            {rejected.slice(0, 4).map((r, i) => (
              <div key={i} className="rejected-card">
                <h4>{r.decision}</h4>
                <p>{r.review ? r.review.replace(/^[^:]+:\s*/, "") : r.why}</p>
                <span className="rejected-cite mono">
                  PR #{r.pr} · {r.author} · synced {r.synced ? fmtRelative(r.synced) : "—"}
                </span>
              </div>
            ))}
          </div>
        </Reveal>
      )}

      {counts && (
        <Reveal className="dec-summary mono">
          {counts.decisions} decisions · {counts.corroborated} corroborated by PRs ·
          {" "}{counts.rejected} rejected · {counts.open_questions} open
        </Reveal>
      )}
    </Section>
  );
}
