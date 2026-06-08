/** Derive dashboard views from one context-pack response (avoids 3x BQ on load). */

export function deriveDecisions(pack) {
  if (!pack || pack.status !== "success") return pack;
  return {
    status: "success",
    project_repo: pack.project_repo,
    github_repo: pack.github_repo,
    freshness: pack.freshness,
    counts: pack.counts,
    decisions: pack.decisions,
    rejected: pack.rejected,
    open_questions: pack.open_questions,
  };
}

export function deriveImpact(pack) {
  if (!pack || pack.status !== "success") return pack;
  const c = pack.counts;
  const minutesSaved =
    c.decisions * 8 + c.rejected * 25 + c.gotchas * 15;
  const contextItems =
    c.decisions + c.rejected + c.open_questions + c.gotchas;
  return {
    status: "success",
    project_repo: pack.project_repo,
    freshness: pack.freshness,
    cold_start: {
      context_items: 0,
      decisions_known: 0,
      rejected_known: 0,
      note: "A fresh agent session knows nothing — it rediscovers from scratch.",
    },
    warm_start: {
      context_items: contextItems,
      decisions_known: c.decisions,
      corroborated: c.corroborated,
      rejected_known: c.rejected,
      gotchas_known: c.gotchas,
      hydration_seconds: 2,
      note: "MoDeX hydrates the agent via load_context in ~2s, each item cited.",
    },
    estimated_minutes_saved_per_session: minutesSaved,
    estimated_hours_saved_per_week_15_devs: Math.round(minutesSaved * 15 * 5 / 60 * 10) / 10,
  };
}
