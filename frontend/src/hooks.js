import { useState, useEffect, useCallback, useMemo } from "react";
import { deriveDecisions, deriveImpact } from "./lib/deriveDashboard";

const BASE = window.location.origin;
const cache = new Map();
const inflight = new Map();

async function apiFetch(path) {
  if (cache.has(path)) return cache.get(path);
  if (inflight.has(path)) return inflight.get(path);

  const p = fetch(`${BASE}${path}`).then(async (res) => {
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    const data = await res.json();
    cache.set(path, data);
    inflight.delete(path);
    return data;
  }).catch((err) => {
    inflight.delete(path);
    throw err;
  });

  inflight.set(path, p);
  return p;
}

function invalidateCache(prefix = "") {
  for (const key of cache.keys()) {
    if (!prefix || key.startsWith(prefix)) cache.delete(key);
  }
}

/** Single bundled loader — one heavy BQ call instead of three. */
export function useDashboardBundle() {
  const [overview, setOverview] = useState(null);
  const [topology, setTopology] = useState(null);
  const [pack, setPack] = useState(null);
  const [pipelines, setPipelines] = useState(null);
  const [freshness, setFreshness] = useState(null);
  const [setup, setSetup] = useState(null);
  const [loading, setLoading] = useState(true);
  const [packLoading, setPackLoading] = useState(true);
  const [error, setError] = useState(null);

  const refreshLight = useCallback(async (silent = false) => {
    try {
      const [ov, topo, pipe, fresh, setupData] = await Promise.all([
        apiFetch("/api/dashboard/overview"),
        apiFetch("/api/dashboard/topology"),
        apiFetch("/api/dashboard/pipelines"),
        apiFetch("/api/dashboard/freshness"),
        apiFetch("/api/dashboard/setup"),
      ]);
      setOverview(ov);
      setTopology(topo);
      setPipelines(pipe);
      setFreshness(fresh);
      setSetup(setupData);
      if (!silent) setLoading(false);
    } catch (e) {
      if (!silent) setError(e.message);
    }
  }, []);

  const refreshPack = useCallback(async (silent = false) => {
    try {
      invalidateCache("/api/dashboard/context-pack");
      const data = await apiFetch("/api/dashboard/context-pack");
      setPack(data);
      if (!silent) setPackLoading(false);
    } catch (e) {
      if (!silent) setError(e.message);
      if (!silent) setPackLoading(false);
    }
  }, []);

  const refresh = useCallback(async () => {
    invalidateCache("/api/dashboard");
    await Promise.all([refreshLight(true), refreshPack(true)]);
  }, [refreshLight, refreshPack]);

  useEffect(() => {
    let cancelled = false;

    (async () => {
      try {
        const [ov, topo] = await Promise.all([
          apiFetch("/api/dashboard/overview"),
          apiFetch("/api/dashboard/topology"),
        ]);
        if (cancelled) return;
        setOverview(ov);
        setTopology(topo);
        setLoading(false);

        // Defer heavy pack + ops data so hero paints first.
        const defer = window.requestIdleCallback || ((fn) => setTimeout(fn, 80));
        defer(() => {
          if (cancelled) return;
          refreshPack(false);
          refreshLight(false);
        });
      } catch (e) {
        if (!cancelled) {
          setError(e.message);
          setLoading(false);
        }
      }
    })();

    const poll = setInterval(() => {
      invalidateCache("/api/dashboard");
      refreshPack(true);
      refreshLight(true);
    }, 120_000);

    return () => {
      cancelled = true;
      clearInterval(poll);
    };
  }, [refreshLight, refreshPack]);

  const decisions = useMemo(() => deriveDecisions(pack), [pack]);
  const impact = useMemo(() => deriveImpact(pack), [pack]);

  return {
    overview,
    topology,
    pack,
    decisions,
    impact,
    pipelines,
    freshness,
    setup,
    loading,
    packLoading,
    topoLoading: loading,
    decisionsLoading: packLoading,
    error,
    refresh,
  };
}

/** Trigger a Fivetran resync (Sheet -> BigQuery) from the dashboard. */
export async function syncData() {
  const res = await fetch(`${BASE}/api/dashboard/sync`, { method: "POST" });
  if (!res.ok) throw new Error(`Sync failed: ${res.status}`);
  return res.json();
}

import { parseMissionEvents } from "./lib/parseMission";

const MISSION_TIMEOUT_MS = 180_000;

export async function runMission(prompt) {
  const userId = "dashboard-user";
  const sessionId = `dash-${Date.now()}`;
  const started = Date.now();
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), MISSION_TIMEOUT_MS);

  try {
    await fetch(`${BASE}/apps/app/users/${userId}/sessions/${sessionId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: "{}",
      signal: controller.signal,
    });

    const res = await fetch(`${BASE}/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        app_name: "app",
        user_id: userId,
        session_id: sessionId,
        new_message: { role: "user", parts: [{ text: prompt }] },
      }),
      signal: controller.signal,
    });

    if (!res.ok) {
      const detail = await res.text().catch(() => "");
      throw new Error(`Run failed (${res.status})${detail ? `: ${detail.slice(0, 120)}` : ""}`);
    }

    const events = await res.json();
    const parsed = parseMissionEvents(events);
    return {
      ...parsed,
      texts: parsed.answer ? [parsed.answer] : [],
      toolCalls: parsed.toolNames,
      elapsedMs: Date.now() - started,
      raw: events,
    };
  } catch (err) {
    if (err.name === "AbortError") {
      throw new Error(
        "Mission timed out after 3 minutes. Multi-agent missions can take 30–90s — try again or use a shorter prompt.",
      );
    }
    throw err;
  } finally {
    clearTimeout(timer);
  }
}
