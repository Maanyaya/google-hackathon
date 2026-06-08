/** MoDeX icon set — lib copy for component architecture */

export function MoDeXLogo({ size = 40, className = "" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 48 48" fill="none" className={className}>
      <defs>
        <linearGradient id="mx-logo-grad" x1="8" y1="4" x2="40" y2="44">
          <stop stopColor="#E8A317" />
          <stop offset="0.55" stopColor="#9D8DF1" />
          <stop offset="1" stopColor="#0DDBBE" />
        </linearGradient>
        <filter id="mx-glow">
          <feGaussianBlur stdDeviation="2" result="b" />
          <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
      </defs>
      <path d="M24 4L42 14V34L24 44L6 34V14L24 4Z" stroke="url(#mx-logo-grad)" strokeWidth="2" fill="rgba(232,163,23,0.06)" filter="url(#mx-glow)" />
      <path d="M24 11V37M15 17L33 31M33 17L15 31" stroke="url(#mx-logo-grad)" strokeWidth="1.25" strokeLinecap="round" opacity="0.55" />
      <circle cx="24" cy="24" r="3.5" fill="#E8A317" />
    </svg>
  );
}

export function EventIcon({ type, size = 16 }) {
  const s = size;
  const map = {
    decision: <path d="M8 1l2 4h4l-3 3 1 4-4-2-4 2 1-4-3-3h4z" fill="#E8A317" />,
    file: <><path d="M3 2h7l3 3v9H3V2z" stroke="#3BCEFF" fill="rgba(59,206,255,0.12)" strokeWidth="1" /><path d="M10 2v3h3" stroke="#3BCEFF" strokeWidth="1" /></>,
    error: <><circle cx="8" cy="8" r="7" stroke="#FF6B6B" fill="rgba(255,107,107,0.1)" strokeWidth="1" /><path d="M8 5v4M8 11h.01" stroke="#FF6B6B" strokeWidth="1.5" strokeLinecap="round" /></>,
    session: <><circle cx="8" cy="8" r="6" stroke="#9D8DF1" fill="rgba(157,141,241,0.1)" strokeWidth="1" /><circle cx="8" cy="8" r="2" fill="#9D8DF1" /></>,
    tool: <path d="M4 10l2-6 6-2-2 6-6 2z" stroke="#7C8AFF" fill="rgba(124,138,255,0.12)" strokeWidth="1" />,
    default: <circle cx="8" cy="8" r="3" fill="#8892A8" />,
  };
  const key = ["file_edit"].includes(type) ? "file" : ["session_start", "session_end"].includes(type) ? "session" : ["tool_call"].includes(type) ? "tool" : type;
  return <svg width={s} height={s} viewBox="0 0 16 16">{map[key] || map.default}</svg>;
}

export function MissionIcon({ id, size = 18 }) {
  const c = "#E8A317";
  const icons = {
    handoff: <path d="M4 8h8M12 8l-3-3M12 8l-3 3M20 16h-8M8 16l3-3M8 16l3 3" stroke={c} strokeWidth="1.5" strokeLinecap="round" />,
    pipeline: <><rect x="3" y="7" width="18" height="10" rx="2" stroke="#0DDBBE" strokeWidth="1.5" fill="rgba(13,219,190,0.08)" /><path d="M8 12h8" stroke="#0DDBBE" strokeWidth="1.5" /></>,
    freshness: <><circle cx="12" cy="12" r="8" stroke={c} strokeWidth="1.5" fill="none" /><path d="M12 8v4l3 2" stroke={c} strokeWidth="1.5" strokeLinecap="round" /></>,
    decision: <path d="M12 3l2.5 5h5.5l-4.5 3.5 1.5 5.5L12 14l-5 3 1.5-5.5L4 8h5.5z" fill={c} opacity="0.85" />,
    lineage: <><circle cx="6" cy="12" r="3" stroke="#3BCEFF" strokeWidth="1.5" fill="none" /><circle cx="18" cy="12" r="3" stroke="#0DDBBE" strokeWidth="1.5" fill="none" /><path d="M9 12h6" stroke="#8892A8" strokeWidth="1.5" strokeDasharray="2 2" /></>,
    export: <><path d="M12 4v10M8 10l4 4 4-4" stroke={c} strokeWidth="1.5" strokeLinecap="round" /><path d="M4 18h16" stroke={c} strokeWidth="1.5" strokeLinecap="round" /></>,
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none">{icons[id] || icons.decision}</svg>;
}

export function SyncRing({ pct = 85, size = 44, color = "#0DDBBE" }) {
  const r = (size - 6) / 2;
  const c = 2 * Math.PI * r;
  const off = c - (pct / 100) * c;
  return (
    <svg width={size} height={size} className="ui-sync-ring">
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="3" />
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={color} strokeWidth="3" strokeDasharray={c} strokeDashoffset={off} strokeLinecap="round" transform={`rotate(-90 ${size / 2} ${size / 2})`} />
    </svg>
  );
}
