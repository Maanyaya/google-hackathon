import { useState, useEffect, useCallback } from "react";

const BASE = window.location.origin;

async function apiFetch(path) {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

export function useDashboardData(path, interval = 0) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const refresh = useCallback(() => {
    setLoading(true);
    apiFetch(path)
      .then((d) => { setData(d); setError(null); })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [path]);

  useEffect(() => {
    refresh();
    if (interval > 0) {
      const id = setInterval(refresh, interval);
      return () => clearInterval(id);
    }
  }, [refresh, interval]);

  return { data, loading, error, refresh };
}

export async function runMission(prompt) {
  const userId = "dashboard-user";
  const sessionId = `dash-${Date.now()}`;

  await fetch(`${BASE}/apps/app/users/${userId}/sessions/${sessionId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: "{}",
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
  });

  if (!res.ok) throw new Error(`Run failed: ${res.status}`);
  const events = await res.json();

  const texts = [];
  const toolCalls = [];
  for (const ev of events) {
    for (const part of (ev.content?.parts || [])) {
      if (part.text) texts.push(part.text);
      if (part.functionCall) toolCalls.push(part.functionCall.name);
    }
  }
  return { texts, toolCalls, raw: events };
}
