import { fmtRelative } from "../../lib/format";

function HeroStat({ value, label }) {
  return (
    <div className="hero-stat">
      <span className="hero-stat-val">{value}</span>
      <span className="hero-stat-label">{label}</span>
    </div>
  );
}

export function Hero({ overview, decisions, impact, onNav }) {
  const counts = decisions?.counts;
  const fresh = decisions?.freshness;
  const sample = (decisions?.decisions || []).slice(0, 3);

  return (
    <header id="top" className="section theme-dark hero">
      <div className="aurora" aria-hidden>
        <span className="a1" />
        <span className="a2" />
        <span className="a3" />
      </div>

      <div className="container hero-grid">
        <div className="hero-copy hero-animate">
          <div className="pill pill-live">
            <span className="dot" />
            Live on Cloud Run · {overview?.region || "asia-south1"}
          </div>

          <h1 className="hero-title">
            Git remembers <span className="hero-strike">what</span> changed.
            <br />
            MoDeX remembers <span className="grad-text">why</span>.
          </h1>

          <p className="hero-lead">
            The shared reasoning memory for AI coding teams. Every decision, every
            <strong> rejected approach</strong>, every gotcha — captured from coding-agent
            sessions, cross-referenced with GitHub PRs synced by <strong>Fivetran</strong>,
            and served to any new agent in seconds. No more relitigating settled decisions.
          </p>

          <div className="hero-cta">
            <button className="btn btn-primary" onClick={() => onNav("mission")}>
              Ask the memory guide
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3 8h9M9 4l4 4-4 4" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" /></svg>
            </button>
            <button className="btn btn-ghost" onClick={() => onNav("pack")}>
              See the context pack
            </button>
          </div>

          <div className="hero-stats">
            <HeroStat value={overview?.agent_count ?? 4} label="ADK agents" />
            <HeroStat value={counts ? counts.decisions : "—"} label="Decisions remembered" />
            <HeroStat value={counts ? counts.corroborated : "—"} label="Corroborated by PRs" />
            <HeroStat
              value={impact ? `${impact.estimated_hours_saved_per_week_15_devs}h` : "—"}
              label="Saved / week (15 devs)"
            />
          </div>
        </div>

        <div className="hero-visual hero-visual-in">
          <ContextPackPreview sample={sample} fresh={fresh} counts={counts} />
        </div>
      </div>

      <div className="hero-fade" />
    </header>
  );
}

function ContextPackPreview({ sample, fresh, counts }) {
  return (
    <div className="cpp">
      <div className="cpp-glow" aria-hidden />
      <div className="cpp-card">
        <div className="cpp-head">
          <div className="cpp-dots"><span /><span /><span /></div>
          <span className="mono cpp-title">load_context() → context pack</span>
          <span className="pill pill-live cpp-badge"><span className="dot" />MCP</span>
        </div>

        <div className="cpp-body scrollbar-thin">
          <div className="cpp-line cpp-comment"># Shared context · cross-referenced & cited</div>
          {(sample.length ? sample : FALLBACK).map((d, i) => (
            <DecisionLine key={i} d={d} />
          ))}
          <div className="cpp-line cpp-warn">
            <span className="cpp-tag tag-rejected">REJECTED</span>
            <span>Don&apos;t reintroduce sticky sessions — see PR review</span>
          </div>
        </div>

        <div className="cpp-foot">
          <SourceFloat label="Cursor session" tone="sky" />
          <span className="cpp-link" />
          <SourceFloat label="GitHub PR" tone="violet" />
          <span className="cpp-link" />
          <SourceFloat label="Fivetran" tone="teal" />
        </div>
      </div>

      <div className="hero-float tone-teal chip-1 float-up">
        <span className="hero-float-dot" />
        Fivetran synced {fresh?.github_last_synced ? fmtRelative(fresh.github_last_synced) : "live"}
      </div>
      <div className="hero-float tone-violet chip-2 float-down">
        <span className="hero-float-dot" />
        {counts ? `${counts.corroborated} corroborated` : "corroborated"}
      </div>
    </div>
  );
}

const FALLBACK = [
  { decision: "PostgreSQL over MongoDB for relational integrity", confidence: "corroborated" },
  { decision: "JWT auth, stateless — no server sessions", confidence: "corroborated" },
  { decision: "Idempotent webhook handlers with dedupe keys", confidence: "session-only" },
];

function DecisionLine({ d }) {
  const ok = d.confidence === "corroborated";
  return (
    <div className="cpp-line">
      <span className={`cpp-tag ${ok ? "tag-ok" : "tag-soft"}`}>{ok ? "CITED" : "SESSION"}</span>
      <span>{d.decision}</span>
    </div>
  );
}

function SourceFloat({ label, tone }) {
  return <span className={`cpp-src tone-${tone}`}>{label}</span>;
}
