"""Pre-demo verification — run the 3 killer Face 2 missions against live Cloud Run.

Usage:
    uv run python scripts/demo_missions.py
    uv run python scripts/demo_missions.py --base https://your-service.run.app
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request

DEFAULT_BASE = "https://agentic-data-platform-979112189932.asia-south1.run.app"

DEMO_MISSIONS = [
    {
        "id": "hydrate",
        "label": "Hydrate me (cold -> warm start)",
        "prompt": (
            "I'm a new agent on github.com/demo/api-service. Use get_team_context to "
            "brief me: decisions, rejected approaches, gotchas. Cite PRs. One paragraph."
        ),
        "expect_tools": {"transfer_to_agent", "get_team_context"},
        "expect_keywords": ("PostgreSQL", "MongoDB", "JWT"),
    },
    {
        "id": "why_stack",
        "label": "Why this stack? (session + GitHub)",
        "prompt": (
            "Did the team pick PostgreSQL or MongoDB and why? Cross-reference session "
            "memory with GitHub PR #142 and rejected PR #88."
        ),
        "expect_tools": {"get_team_context"},
        "expect_keywords": ("PostgreSQL", "142", "88"),
    },
    {
        "id": "pipeline",
        "label": "Pipeline health (Fivetran MCP)",
        "prompt": (
            "List Fivetran connections in group solve_unhurt. Are GitHub and "
            "stowed_register healthy? Report sync state briefly."
        ),
        "expect_tools": {"fivetran_list_connections"},
        "expect_keywords": ("connection", "sync"),
    },
]


def _post_json(url: str, body: dict, timeout: int = 180) -> tuple[int, object]:
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode()[:500]


def run_mission(base: str, prompt: str) -> dict:
    user = "demo-check"
    sid = f"demo-{int(time.time())}"
    _post_json(f"{base}/apps/app/users/{user}/sessions/{sid}", {})
    status, events = _post_json(
        f"{base}/run",
        {
            "app_name": "app",
            "user_id": user,
            "session_id": sid,
            "new_message": {"role": "user", "parts": [{"text": prompt}]},
        },
    )
    if status != 200:
        return {"ok": False, "error": f"HTTP {status}: {events}"}

    tools: set[str] = set()
    texts: list[str] = []
    for ev in events if isinstance(events, list) else []:
        for part in (ev.get("content") or {}).get("parts") or []:
            if fc := part.get("functionCall"):
                tools.add(fc.get("name", ""))
            if txt := part.get("text"):
                if (ev.get("content") or {}).get("role") == "model":
                    texts.append(txt)

    answer = texts[-1] if texts else ""
    return {"ok": True, "tools": tools, "answer": answer, "event_count": len(events)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify MoDeX demo missions on live Cloud Run")
    parser.add_argument("--base", default=DEFAULT_BASE, help="Cloud Run base URL")
    args = parser.parse_args()
    base = args.base.rstrip("/")

    print(f"MoDeX demo mission check -> {base}\n")
    failed = 0

    for m in DEMO_MISSIONS:
        print(f"> {m['label']}")
        t0 = time.time()
        result = run_mission(base, m["prompt"])
        elapsed = time.time() - t0

        if not result.get("ok"):
            print(f"  FAIL ({elapsed:.1f}s): {result.get('error')}\n")
            failed += 1
            continue

        tools = result["tools"]
        answer = result.get("answer", "")
        missing_tools = m["expect_tools"] - tools
        missing_kw = [k for k in m["expect_keywords"] if k.lower() not in answer.lower()]

        ok = not missing_tools and not missing_kw
        status = "PASS" if ok else "WARN"
        if not ok:
            failed += 1

        print(f"  {status} ({elapsed:.1f}s) tools={sorted(tools)} events={result['event_count']}")
        if missing_tools:
            print(f"    missing tools: {missing_tools}")
        if missing_kw:
            print(f"    missing keywords in answer: {missing_kw}")
        print(f"    preview: {answer[:220].replace(chr(10), ' ')}...\n")

    if failed:
        print(f"{failed} mission(s) need attention before demo.")
        return 1
    print("All demo missions ready for presentation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
