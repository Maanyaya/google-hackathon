"""MoDeX handoff CLI — the rigid backbone of code-memory transfer.

This is the deterministic, hook-independent path that guarantees one agent's
context reaches the next agent through the Google Sheet (Fivetran source) +
BigQuery. Hooks are the convenient automatic layer; this CLI is the contract
the demo relies on.

    # Agent A: capture the conversation so far into a single rich handoff row
    python -m modex_mcp.handoff snapshot --repo github.com/Maanyaya/google-hackathon

    # Agent B (any IDE / tool / OS): load the exact same context to resume
    python -m modex_mcp.handoff hydrate  --repo github.com/Maanyaya/google-hackathon

    # Inspect what memory currently exists for a repo
    python -m modex_mcp.handoff status   --repo github.com/Maanyaya/google-hackathon

``snapshot`` reads every event in agent_memory.codebase_logs for the repo,
deterministically compresses it (transcript + decisions + files + briefing),
writes ONE ``context_compressed`` row to BigQuery and mirrors it to the
``MoDex_Logs`` sheet (columns context_json + transcript_md), then reads it back
to prove the round-trip. ``hydrate`` returns the briefing + transcript that the
next agent injects as its system context.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_WORKSPACE = _ROOT.parent
sys.path.insert(0, str(_ROOT))

os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "gen-lang-client-0795401430")
if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
    for _cand in (
        _WORKSPACE / "gen-lang-client-0795401430-7e740cbd01ac.json",
        _ROOT / "gen-lang-client-0795401430-7e740cbd01ac.json",
    ):
        if _cand.is_file():
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(_cand)
            break

from dotenv import load_dotenv  # noqa: E402

load_dotenv(_ROOT / ".env")
load_dotenv(_WORKSPACE / ".env")

from modex_mcp.memory_store import (  # noqa: E402
    _fetch_log_events,
    load_latest_compressed_context,
    save_compressed_context,
)


def _developer_id(explicit: str | None) -> str:
    if explicit:
        return explicit
    import subprocess

    for cwd in (str(_ROOT), str(_WORKSPACE / "agentic-data-platform"), str(_WORKSPACE)):
        try:
            r = subprocess.run(
                ["git", "-C", cwd, "config", "user.email"],
                capture_output=True,
                text=True,
                timeout=3,
                check=False,
            )
            if r.stdout.strip():
                return r.stdout.strip()
        except Exception:  # noqa: BLE001
            continue
    return os.getenv("USERNAME") or os.getenv("USER") or "developer"


def cmd_snapshot(args: argparse.Namespace) -> int:
    print(f"[snapshot] compressing memory for {args.repo}"
          + (f" (session {args.session})" if args.session else ""))
    result = save_compressed_context(
        developer_id=_developer_id(args.developer),
        agent_tool=args.agent_tool,
        project_repo=args.repo,
        session_id=args.session,
    )
    if result.get("status") != "success":
        print(f"[snapshot] FAILED: {result.get('message')}")
        return 1

    blob = result.get("context_json") or {}
    print(f"[snapshot] {result.get('summary')}")
    print(f"[snapshot] BigQuery event_id: {result.get('event_id')}")
    mirror = result.get("fivetran_mirror") or {}
    if mirror.get("sheet_updated_range"):
        print(f"[snapshot] Sheet row written: {mirror['sheet_updated_range']}")
    elif mirror.get("sheet_error"):
        print(f"[snapshot] Sheet mirror error: {mirror['sheet_error']}")
    else:
        print("[snapshot] Sheet mirror: (no sheet configured)")

    # Round-trip proof: read back what another agent would load.
    packed = load_latest_compressed_context(args.repo)
    rb = packed.get("context_json") or {}
    turns = len(rb.get("transcript") or [])
    has_briefing = bool(rb.get("system_context"))
    print(f"[snapshot] Round-trip read-back: {turns} turns, briefing={'yes' if has_briefing else 'no'}")
    ok = turns > 0
    print("[snapshot] RESULT:", "PASS" if ok else "EMPTY (no events captured yet)")
    return 0 if ok else 2


def cmd_hydrate(args: argparse.Namespace) -> int:
    from modex_mcp.context_compress import render_hydration_from_context

    packed = load_latest_compressed_context(args.repo)
    if packed.get("status") != "success" or not packed.get("context_json"):
        print(f"# MoDeX: no shared memory found for {args.repo} yet.")
        return 2
    blob = packed["context_json"]
    text = render_hydration_from_context(blob)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"[hydrate] wrote system context for next agent -> {args.out}")
        print(f"[hydrate] {len(blob.get('transcript') or [])} turns, "
              f"{len(blob.get('decisions') or [])} decisions")
    else:
        print(text)
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    events = _fetch_log_events(args.repo, limit=500)
    counts: dict[str, int] = {}
    for e in events:
        counts[e["event_type"]] = counts.get(e["event_type"], 0) + 1
    print(f"[status] {args.repo}: {len(events)} recent events")
    for et, c in sorted(counts.items(), key=lambda kv: kv[1], reverse=True):
        print(f"  {et}: {c}")
    packed = load_latest_compressed_context(args.repo)
    blob = packed.get("context_json") or {}
    if blob:
        print(f"[status] latest handoff: {blob.get('compressed_at')} "
              f"({len(blob.get('transcript') or [])} turns, "
              f"{len(blob.get('decisions') or [])} decisions)")
    else:
        print("[status] no compressed handoff yet — run `snapshot`.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="modex.handoff", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    def _common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--repo", required=True, help="project_repo, e.g. github.com/org/name")
        p.add_argument("--agent-tool", default=os.getenv("MODEX_AGENT_TOOL", "cursor"))
        p.add_argument("--developer", default=os.getenv("MODEX_DEVELOPER_ID") or None)

    p_snap = sub.add_parser("snapshot", help="compress + store + verify the handoff")
    _common(p_snap)
    p_snap.add_argument("--session", default=None, help="limit to one session id")
    p_snap.set_defaults(func=cmd_snapshot)

    p_hyd = sub.add_parser("hydrate", help="load latest context for the next agent")
    _common(p_hyd)
    p_hyd.add_argument("--out", default=None, help="write to file instead of stdout")
    p_hyd.set_defaults(func=cmd_hydrate)

    p_stat = sub.add_parser("status", help="show memory counts + freshness")
    _common(p_stat)
    p_stat.set_defaults(func=cmd_status)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
