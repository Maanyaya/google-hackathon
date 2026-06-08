export function Panel({ title, subtitle, action, children, className = "", id, glow }) {
  return (
    <section id={id} className={`ui-panel ${glow ? "ui-panel-glow" : ""} ${className}`}>
      {(title || action) && (
        <header className="ui-panel-head">
          <div>
            {title && <h2 className="ui-panel-title">{title}</h2>}
            {subtitle && <p className="ui-panel-sub">{subtitle}</p>}
          </div>
          {action}
        </header>
      )}
      {children}
    </section>
  );
}

export function Skeleton({ className = "", style }) {
  return <div className={`ui-skeleton ${className}`} style={style} aria-hidden />;
}

export function Badge({ children, tone = "neutral", dot }) {
  return (
    <span className={`ui-badge ui-badge-${tone}`}>
      {dot && <span className={`ui-badge-dot ui-badge-dot-${tone}`} />}
      {children}
    </span>
  );
}

export function MetricCard({ label, value, hint, accent = "memory", loading }) {
  return (
    <div className={`ui-metric ui-metric-${accent}`}>
      {loading ? (
        <>
          <Skeleton className="h-8 w-16 mb-2" />
          <Skeleton className="h-3 w-24" />
        </>
      ) : (
        <>
          <div className="ui-metric-value">{value ?? "—"}</div>
          <div className="ui-metric-label">{label}</div>
          {hint && <div className="ui-metric-hint">{hint}</div>}
        </>
      )}
    </div>
  );
}
