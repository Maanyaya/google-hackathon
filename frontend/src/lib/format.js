export function fmtTime(iso) {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return String(iso);
  }
}

export function fmtRelative(iso) {
  if (!iso) return "—";
  try {
    const diff = Date.now() - new Date(iso).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return "just now";
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    return fmtTime(iso);
  } catch {
    return "—";
  }
}

export function initials(email = "") {
  const part = email.split("@")[0] || "?";
  return part.slice(0, 2).toUpperCase();
}
