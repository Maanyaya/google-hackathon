/**
 * Submission — hackathon entry card for judges & DevPost visitors.
 */
import { Section } from "../ui/Section";
import { Reveal } from "../ui/Reveal";

const LINKS = {
  devpost: "https://rapid-agent.devpost.com/",
  dashboard: "https://agentic-data-platform-979112189932.asia-south1.run.app/dashboard/",
  github: "https://github.com/Maanyaya/google-hackathon",
  judges: "https://github.com/Maanyaya/google-hackathon/blob/main/JUDGES.md",
  demoVideo: "https://youtu.be/_-O5sinN4qY",
  sheet: "https://docs.google.com/spreadsheets/d/1NKxRyKBBgBzETtaaPO_gPC8vdM1i4vtt5yxrq6iCRck",
  license: "https://github.com/Maanyaya/google-hackathon/blob/main/LICENSE",
};

const BUILT_WITH = [
  "Gemini 2.5 Flash",
  "Google ADK",
  "Cloud Run",
  "BigQuery",
  "Secret Manager",
  "Fivetran MCP",
];

const JUDGE_STEPS = [
  {
    n: "1",
    title: "Try Face 2 (no install)",
    desc: "Open the dashboard → Ask Face 2 → click Hydrate me or Pipeline trust.",
  },
  {
    n: "2",
    title: "Test Face 1 MCP (5 min)",
    desc: "Copy judge keys from JUDGES.md → paste into ~/.gemini/antigravity/mcp_config.json → restart Antigravity.",
  },
  {
    n: "3",
    title: "Watch the demo video",
    desc: "3-minute walkthrough: IDE handoff, Fivetran connectors, Face 2 live trace.",
  },
];

function LinkCard({ href, label, sub, external = true, primary }) {
  return (
    <a
      className={`sub-link-card${primary ? " sub-link-primary" : ""}`}
      href={href}
      target={external ? "_blank" : undefined}
      rel={external ? "noreferrer" : undefined}
    >
      <span className="sub-link-label">{label}</span>
      {sub && <span className="sub-link-sub">{sub}</span>}
      <svg className="sub-link-arrow" width="14" height="14" viewBox="0 0 16 16" fill="none" aria-hidden>
        <path d="M4 12L12 4M12 4H6M12 4v6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </a>
  );
}

export function Submission() {
  return (
    <Section id="submission" theme="light" className="section-submission">
      <Reveal className="sub-banner">
        <div className="sub-banner-top">
          <div className="sub-badges">
            <span className="sub-badge sub-badge-hackathon">Google Cloud Rapid Agent Hackathon</span>
            <span className="sub-badge sub-badge-track">Fivetran Track</span>
            <span className="sub-badge sub-badge-live">
              <span className="dot" />
              Live submission
            </span>
          </div>
          <h2 className="sub-title">MoDeX — Memory of Codex</h2>
          <p className="sub-lead">
            Shared persistent memory for AI coding agents.{" "}
            <strong>Face 1 MCP</strong> captures decisions in the IDE.{" "}
            <strong>Fivetran</strong> syncs the memory bus to BigQuery.{" "}
            <strong>Face 2</strong> (Gemini ADK on Cloud Run) answers and operates pipelines live.
          </p>
        </div>

        <div className="sub-links-grid">
          <LinkCard
            href={LINKS.dashboard}
            label="Hosted project"
            sub="Try the live dashboard — no login required"
            primary
          />
          <LinkCard href={LINKS.demoVideo} label="Demo video (3 min)" sub="YouTube · full walkthrough" primary />
          <LinkCard href={LINKS.github} label="GitHub repo" sub="Apache 2.0 · public source" />
          <LinkCard href={LINKS.judges} label="Judge guide" sub="MCP keys + test prompts" />
          <LinkCard href={LINKS.sheet} label="Memory bus (Sheet)" sub="Human-readable session logs" />
          <LinkCard href={LINKS.devpost} label="DevPost" sub="Hackathon submission page" />
        </div>

        <div className="sub-built">
          <span className="sub-built-label">Built with</span>
          <div className="sub-built-tags">
            {BUILT_WITH.map((t) => (
              <span key={t} className="sub-built-tag">{t}</span>
            ))}
          </div>
        </div>
      </Reveal>

      <Reveal className="sub-judge-card card">
        <h3 className="sub-judge-head">How judges can evaluate MoDeX</h3>
        <div className="sub-judge-steps">
          {JUDGE_STEPS.map((s) => (
            <div key={s.n} className="sub-judge-step">
              <span className="sub-judge-n">{s.n}</span>
              <div>
                <strong>{s.title}</strong>
                <p>{s.desc}</p>
              </div>
            </div>
          ))}
        </div>
        <p className="sub-judge-note">
          Pre-provisioned on our Google Cloud + Fivetran accounts — judges use public API keys from{" "}
          <a href={LINKS.judges} target="_blank" rel="noreferrer">JUDGES.md</a>
          . No GCP or Fivetran signup required to test.
        </p>
      </Reveal>
    </Section>
  );
}
