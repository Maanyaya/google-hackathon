import { MoDeXLogo } from "../../lib/icons";
import { NAV } from "../../lib/theme";

const STACK = ["Gemini", "Google ADK", "Fivetran MCP", "BigQuery", "Vertex AI RAG", "Cloud Run"];

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
            Shared reasoning memory for AI coding teams. Capture the <em>why</em>, cross-reference
            it with GitHub via Fivetran, and serve it to any agent — cited and governed.
          </p>
          <div className="footer-stack">
            {STACK.map((s) => <span key={s} className="footer-badge">{s}</span>)}
          </div>
        </div>

        <div className="footer-links">
          <h5>Explore</h5>
          {NAV.map((n) => (
            <button key={n.id} onClick={() => onNav(n.id)}>{n.label}</button>
          ))}
        </div>

        <div className="footer-meta">
          <h5>Deployment</h5>
          <p className="mono">{overview?.project || "agentic-platform"}</p>
          <p className="mono">{overview?.region || "asia-south1"}</p>
          {overview?.cloud_run_url && (
            <a className="footer-cta" href={overview.cloud_run_url} target="_blank" rel="noreferrer">
              Open live service ↗
            </a>
          )}
        </div>
      </div>

      <div className="container footer-bottom">
        <span>Built for the Google Cloud × Fivetran Rapid Agent Hackathon</span>
        <span className="mono">{overview?.face1_mcp || "modex_mcp · load_context"}</span>
      </div>
    </footer>
  );
}
