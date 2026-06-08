import { MoDeXLogo } from "../../lib/icons";
import { NAV } from "../../lib/theme";

export function TopBar({ overview, onNav }) {
  return (
    <header className="ui-topbar">
      <div className="ui-topbar-inner">
        <div className="ui-brand">
          <div className="ui-brand-mark">
            <MoDeXLogo size={36} />
          </div>
          <div>
            <h1 className="ui-brand-title">MoDeX</h1>
            <p className="ui-brand-tag">Memory of Codex</p>
          </div>
        </div>

        <nav className="ui-nav" aria-label="Sections">
          {NAV.map((n) => (
            <button key={n.id} type="button" className="ui-nav-item" onClick={() => onNav?.(n.id)}>
              {n.label}
            </button>
          ))}
        </nav>

        <div className="ui-topbar-status">
          <span className="ui-live-pill">
            <span className="ui-live-dot" />
            {overview?.agent_count ?? 7} agents live
          </span>
          <span className="ui-region-pill">{overview?.region ?? "asia-south1"}</span>
        </div>
      </div>
    </header>
  );
}

export function Shell({ children }) {
  return (
    <div className="ui-app">
      <div className="ui-aurora ui-aurora-a" />
      <div className="ui-aurora ui-aurora-b" />
      <div className="ui-noise" />
      <div className="ui-app-content">{children}</div>
    </div>
  );
}
