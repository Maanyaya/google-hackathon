import { Reveal } from "./Reveal";

/**
 * Theme-aware section wrapper.
 * theme: "dark" | "light". `aurora` adds the animated mesh (dark only).
 */
export function Section({ id, theme = "light", aurora = false, className = "", children }) {
  return (
    <section id={id} className={`section theme-${theme} section-pad ${className}`}>
      {aurora && (
        <div className="aurora" aria-hidden>
          <span className="a1" />
          <span className="a2" />
          <span className="a3" />
        </div>
      )}
      <div className="container">{children}</div>
    </section>
  );
}

/** Standard section header: eyebrow + title + lead. */
export function SectionHead({ eyebrow, title, lead, align = "left" }) {
  return (
    <Reveal className={`section-head ${align === "center" ? "section-head-center" : ""}`}>
      {eyebrow && <div className="eyebrow">{eyebrow}</div>}
      <h2 className="section-title" dangerouslySetInnerHTML={{ __html: title }} />
      {lead && <p className="section-lead">{lead}</p>}
    </Reveal>
  );
}
