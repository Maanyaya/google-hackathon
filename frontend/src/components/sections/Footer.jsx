import { MoDeXLogo } from "../../lib/icons";
import { NAV } from "../../lib/theme";

const LINKS = {
  devpost: "https://rapid-agent.devpost.com/",
  dashboard: "https://agentic-data-platform-979112189932.asia-south1.run.app/dashboard/",
  github: "https://github.com/Maanyaya/google-hackathon",
  judges: "https://github.com/Maanyaya/google-hackathon/blob/main/JUDGES.md",
  demo: "https://youtu.be/_-O5sinN4qY",
};

const STACK = ["Gemini 2.5 Flash", "Google ADK", "Fivetran MCP", "BigQuery", "Cloud Run", "Secret Manager"];

export function Footer({ overview, onNav }) {
  return (
    <footer className="section theme-dark footer">
      <div className="aurora"><span className="a2" /></div>
      <div className="container footer-inner">
        <div className="footer-brand">
          <div className="brand">
            <MoDeXLogo size={40} />
            <span>
              <span className="brand-name">MoDeX</span>
              <span className="brand-sub" style={{ display: "block" }}>Memory of Codex</span>
            </span>
          </div>
          <p className="footer-tagline">
            <strong>Google Cloud Rapid Agent Hackathon</strong> · Fivetran Track submission.
            Shared memory for AI coding agents — Gemini ADK + Fivetran MCP on Cloud Run.
          </p>
          <div className="footer-stack">
            {STACK.map((s) => <span key={s} className="footer-badge">{s}</span>)}
          </div>
        </div>

        <div className="footer-links">
          <h5>Submission</h5>
          <a href={LINKS.dashboard} target="_blank" rel="noreferrer">Live dashboard</a>
          <a href={LINKS.demo} target="_blank" rel="noreferrer">Demo video (3 min)</a>
          <a href={LINKS.github} target="_blank" rel="noreferrer">GitHub repo</a>
          <a href={LINKS.judges} target="_blank" rel="noreferrer">Judge guide</a>
          <a href={LINKS.devpost} target="_blank" rel="noreferrer">DevPost</a>
        </div>

        <div className="footer-links">
          <h5>Explore</h5>
          {NAV.map((n) => (
            <button key={n.id} onClick={() => onNav(n.id)}>{n.label}</button>
          ))}
        </div>

        <div className="footer-meta">
          <h5>Deployment</h5>
          <p className="mono">{overview?.project || "agentic-data-platform"}</p>
          <p className="mono">{overview?.region || "asia-south1"}</p>
          {overview?.cloud_run_url && (
            <a className="footer-cta" href={overview.cloud_run_url} target="_blank" rel="noreferrer">
              Open live service ↗
            </a>
          )}
        </div>
      </div>

      <div className="container footer-bottom">
        <span>Submitted to Google Cloud Rapid Agent Hackathon · Fivetran Track · Apache 2.0</span>
        <span className="mono">Team MoDeX</span>
      </div>
    </footer>
  );
}
