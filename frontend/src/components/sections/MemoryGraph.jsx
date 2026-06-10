import { useMemo, useState } from "react";
import { Section, SectionHead } from "../ui/Section";
import { Reveal } from "../ui/Reveal";

const FALLBACK = [
  { decision: "PostgreSQL over MongoDB for relational integrity", session: { tool: "antigravity", who: "alex" }, pr: { number: 142, who: "priya", review: "priya (APPROVED): relational guarantees win here" } },
  { decision: "JWT (stateless) — drop server-side sessions", session: { tool: "antigravity", who: "sam" }, pr: { number: 137, who: "lee", review: "lee (APPROVED): scales horizontally" } },
  { decision: "Idempotent webhook handlers with dedupe keys", session: { tool: "antigravity", who: "mia" }, pr: { number: 151, who: "alex", review: "alex (APPROVED): prevents double-processing" } },
];

function buildLanes(decisions) {
  const list = (decisions?.decisions || [])
    .map((d) => {
      const session = d.sources?.find((s) => s.type === "session");
      const pr = d.sources?.find((s) => s.type === "github_pr");
      if (!pr) return null;
      return { decision: d.decision, status: d.status, session, pr };
    })
    .filter(Boolean)
    .slice(0, 4);
  return list.length ? list : FALLBACK;
}

const H = 130;

export function MemoryGraph({ decisions }) {
  const lanes = useMemo(() => buildLanes(decisions), [decisions]);
  const [active, setActive] = useState(0);
  const n = lanes.length;
  const height = n * H + 40;
  const hubY = height / 2;
  const hubX = 500;
  const laneY = (i) => 60 + i * H + H / 2 - 20;

  return (
    <Section id="graph" theme="dark" aurora>
      <SectionHead
        eyebrow="The living memory graph"
        title='Where a decision meets <span class="grad-text">its proof</span>'
        lead="MoDeX cross-references each coding-agent session decision with the GitHub PR and reviewer reasoning that backs it — synced through Fivetran. Hover a lane to inspect the link."
      />

      <div className="graph-wrap">
        <svg className="graph-svg graph-fade-in" viewBox={`0 0 1000 ${height}`}>
          <defs>
            <linearGradient id="g-edge" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0" stopColor="#4cc9ff" />
              <stop offset="0.5" stopColor="#f5a623" />
              <stop offset="1" stopColor="#9b8cff" />
            </linearGradient>
            <radialGradient id="g-hub">
              <stop offset="0" stopColor="#f5a623" />
              <stop offset="1" stopColor="#e8920a" />
            </radialGradient>
          </defs>

          <text x="120" y="28" className="graph-col">CODING-AGENT SESSIONS</text>
          <text x="500" y="28" className="graph-col" textAnchor="middle">MoDeX</text>
          <text x="880" y="28" className="graph-col" textAnchor="end">GITHUB PRs · FIVETRAN</text>

          {lanes.map((lane, i) => {
            const y = laneY(i);
            const lx = 120;
            const rx = 880;
            const pathL = `M ${lx} ${y} C ${(lx + hubX) / 2} ${y}, ${(lx + hubX) / 2} ${hubY}, ${hubX} ${hubY}`;
            const pathR = `M ${hubX} ${hubY} C ${(hubX + rx) / 2} ${hubY}, ${(hubX + rx) / 2} ${y}, ${rx} ${y}`;
            const on = active === i;
            return (
              <g key={i} onMouseEnter={() => setActive(i)} className="graph-lane">
                <path d={pathL} className={`graph-edge ${on ? "on" : ""}`} />
                <path d={pathR} className={`graph-edge ${on ? "on" : ""}`} />
                <g transform={`translate(${lx}, ${y})`} className="graph-node">
                  <circle r="11" className={`gn-session ${on ? "on" : ""}`} />
                  <text x="-22" y="4" textAnchor="end" className="gn-label">{lane.session?.tool || "session"}</text>
                </g>
                <g transform={`translate(${rx}, ${y})`} className="graph-node">
                  <circle r="11" className={`gn-pr ${on ? "on" : ""}`} />
                  <text x="22" y="4" className="gn-label">PR #{lane.pr?.number}</text>
                </g>
              </g>
            );
          })}

          <g transform={`translate(${hubX}, ${hubY})`}>
            <circle r="44" className="gn-hub-ring" />
            <circle r="30" fill="url(#g-hub)" />
            <text y="5" textAnchor="middle" className="gn-hub-text">MoDeX</text>
          </g>
        </svg>

        <Reveal className="graph-detail card">
          <div className="graph-detail-head">
            <span className="pill" style={{ borderColor: "rgba(56,211,159,0.4)", color: "var(--green)" }}>
              <span className="dot" style={{ background: "var(--green)" }} />
              corroborated
            </span>
            <span className="mono graph-detail-lane">lane {active + 1} / {n}</span>
          </div>
          <h3 className="graph-detail-title">{lanes[active]?.decision}</h3>
          <div className="graph-detail-row">
            <span className="gdr-key">Session</span>
            <span className="gdr-val">{lanes[active]?.session?.tool || "—"} · {lanes[active]?.session?.who || "agent"}</span>
          </div>
          <div className="graph-detail-row">
            <span className="gdr-key">GitHub</span>
            <span className="gdr-val">PR #{lanes[active]?.pr?.number} · {lanes[active]?.pr?.who}</span>
          </div>
          {lanes[active]?.pr?.review && (
            <p className="graph-detail-review">&ldquo;{lanes[active].pr.review}&rdquo;</p>
          )}
        </Reveal>
      </div>
    </Section>
  );
}
