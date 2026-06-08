import { useRef, useState, useCallback } from "react";
import { Section } from "../ui/Section";
import { Reveal, useInViewOnce } from "../ui/Reveal";

function CountUp({ to = 0, suffix = "" }) {
  const [val, setVal] = useState(0);
  const ref = useRef(null);
  const start = useCallback(() => {
    const t0 = performance.now();
    const duration = 900;
    const tick = (t) => {
      const p = Math.min(1, (t - t0) / duration);
      const eased = 1 - Math.pow(1 - p, 3);
      setVal(to * eased);
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }, [to]);

  useInViewOnce(ref, start);
  const display = to % 1 === 0 ? Math.round(val) : val.toFixed(1);
  return <span ref={ref}>{display}{suffix}</span>;
}

function ColdRow({ label }) {
  return (
    <li className="cold-row">
      <span className="cold-x">✕</span>
      {label}
    </li>
  );
}
function WarmRow({ label, value }) {
  return (
    <li className="warm-row">
      <span className="warm-check">✓</span>
      <span>{label}</span>
      <span className="warm-val">{value}</span>
    </li>
  );
}

export function Impact({ impact }) {
  const warm = impact?.warm_start;
  const hours = impact?.estimated_hours_saved_per_week_15_devs ?? 0;
  const mins = impact?.estimated_minutes_saved_per_session ?? 0;

  return (
    <Section id="impact" theme="dark" aurora>
      <div className="impact-head">
        <Reveal>
          <div className="eyebrow">Cold start → warm start</div>
          <h2 className="section-title">
            Every session starts with <span className="grad-text">everything the team knows</span>
          </h2>
        </Reveal>
      </div>

      <div className="impact-compare">
        <Reveal className="impact-panel cold-panel">
          <div className="impact-panel-head">
            <span className="impact-tag tag-cold">Without MoDeX</span>
            <h3>Cold start</h3>
          </div>
          <ul className="impact-list">
            <ColdRow label="Knows nothing about prior decisions" />
            <ColdRow label="Re-proposes already-rejected approaches" />
            <ColdRow label="Rediscovers gotchas the hard way" />
            <ColdRow label="Burns time re-deriving settled context" />
          </ul>
          <div className="impact-panel-foot cold-foot">
            <span className="big-zero">0</span>
            <span>context items · rediscovers from scratch</span>
          </div>
        </Reveal>

        <Reveal className="impact-arrow" delay={80}>
          <span className="impact-arrow-label mono">load_context</span>
          <svg width="60" height="24" viewBox="0 0 60 24" fill="none"><path d="M2 12h50M46 5l9 7-9 7" stroke="var(--amber)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
          <span className="impact-arrow-time">~{warm?.hydration_seconds ?? 2}s</span>
        </Reveal>

        <Reveal className="impact-panel warm-panel" delay={120}>
          <div className="impact-panel-head">
            <span className="impact-tag tag-warm">With MoDeX</span>
            <h3>Warm start</h3>
          </div>
          <ul className="impact-list">
            <WarmRow label="Decisions known" value={warm?.decisions_known ?? "—"} />
            <WarmRow label="Corroborated by PRs" value={warm?.corroborated ?? "—"} />
            <WarmRow label="Rejected approaches flagged" value={warm?.rejected_known ?? "—"} />
            <WarmRow label="Gotchas surfaced" value={warm?.gotchas_known ?? "—"} />
          </ul>
          <div className="impact-panel-foot warm-foot">
            <span className="big-num"><CountUp to={warm?.context_items ?? 0} /></span>
            <span>cited context items · hydrated in seconds</span>
          </div>
        </Reveal>
      </div>

      <Reveal className="impact-bottom">
        <div className="impact-metric">
          <span className="impact-metric-val"><CountUp to={hours} suffix="h" /></span>
          <span className="impact-metric-label">saved per week<br />across 15 developers</span>
        </div>
        <div className="impact-divider" />
        <div className="impact-metric">
          <span className="impact-metric-val"><CountUp to={mins} suffix="m" /></span>
          <span className="impact-metric-label">rediscovery avoided<br />per agent session</span>
        </div>
        <div className="impact-divider" />
        <div className="impact-metric impact-metric-text">
          <p>Time that used to vanish into re-deriving context now compounds into shipped work. <strong>That&apos;s the ROI of shared reasoning memory.</strong></p>
        </div>
      </Reveal>
    </Section>
  );
}
