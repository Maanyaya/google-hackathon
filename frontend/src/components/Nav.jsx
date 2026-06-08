import { useEffect, useState } from "react";
import { MoDeXLogo } from "../lib/icons";
import { NAV } from "../lib/theme";

export function Nav({ onNav, githubSource }) {
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
        <button className="nav-cta" onClick={() => onNav("mission")}>
          Run a mission
        </button>
      </div>
    </nav>
  );
}
