import { useEffect, useState } from "react";
import { MoDeXLogo } from "../lib/icons";
import { NAV } from "../lib/theme";

export function Nav({ onNav, githubSource, onSync, syncing }) {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <nav className={`nav ${scrolled ? "scrolled" : ""}`}>
      <div className="nav-inner">
        <button className="brand" onClick={() => onNav("top")} aria-label="MoDeX home">
          <MoDeXLogo size={34} />
          <span>
            <span className="brand-name">MoDeX</span>
            <span className="brand-sub" style={{ display: "block" }}>Memory of Codex</span>
          </span>
        </button>
        <div className="nav-links">
          {NAV.map((n) => (
            <button key={n.id} className="nav-link" onClick={() => onNav(n.id)}>
              {n.label}
            </button>
          ))}
        </div>
        <div className="nav-actions">
          {onSync && (
            <button
              className={`nav-sync ${syncing ? "is-syncing" : ""}`}
              onClick={onSync}
              disabled={syncing}
              title="Resync session memory (Sheet → Fivetran → BigQuery) and refresh the dashboard"
            >
              <svg width="15" height="15" viewBox="0 0 16 16" fill="none" className="nav-sync-icon">
                <path d="M13.5 8a5.5 5.5 0 1 1-1.6-3.9M13.5 2.5V5H11" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              {syncing ? "Syncing…" : "Sync data"}
            </button>
          )}
          <button className="nav-cta" onClick={() => onNav("ask")}>
            Ask Face 2
          </button>
        </div>
      </div>
    </nav>
  );
}
