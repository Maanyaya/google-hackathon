"""End-to-end proof: Agent A conversation -> Sheet/BQ -> Agent B hydration.

In-process (fast). Simulates a real Cursor conversation by writing genuine
event rows, then runs the deterministic handoff and shows the exact system
context a second agent would receive.
"""

from __future__ import annotations

import os
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "gen-lang-client-0795401430")
from dotenv import load_dotenv

load_dotenv(ROOT.parent / ".env")
load_dotenv(ROOT / ".env")

from modex_mcp.memory_store import append_codebase_log, load_latest_compressed_context, save_compressed_context

REPO = "github.com/Maanyaya/google-hackathon"
SID = f"e2e-{uuid.uuid4().hex[:10]}"
DEV = "gagantak00@gmail.com"


def log(event_type, summary, **extra):
    payload = extra.pop("payload", {})
    append_codebase_log(
        developer_id=DEV,
        agent_tool="cursor",
        project_repo=REPO,
        event_type=event_type,
        summary=summary,
        session_id=SID,
        payload=payload,
        **extra,
    )


def main() -> int:
    print(f"=== AGENT A: simulating a real Cursor session {SID} ===")
    log("session_start", "Cursor session started (agent)")
    log("user_prompt", "The MoDeX logging isn't capturing context. Make the pipeline rigid.",
        payload={"full_text": "The MoDeX logging isn't capturing context. Make the pipeline rigid so a second agent gets the same context."})
    log("decision", "Invoke hooks via python.exe directly instead of .cmd wrappers (Windows drops stdin through cmd chains)")
    log("decision", "Use Cursor conversation_id as the MoDeX session_id so events group per chat")
    log("file_edit", "Edited hook_runner.py (1 change(s))", file_path="modex_mcp/hook_runner.py", payload={"edit_count": 1})
    log("file_edit", "Edited hooks.json (1 change(s))", file_path=".cursor/hooks.json", payload={"edit_count": 1})
    log("tool_call", "Shell: python -m pytest tests/unit", payload={"tool_name": "Shell", "tool_input": {"command": "python -m pytest tests/unit"}})
    log("agent_response", "Rewrote hook_runner + pointed hooks.json at python.exe; verified sheet write to A361:N361.",
        payload={"full_text": "Rewrote hook_runner.py and pointed hooks.json directly at python.exe. Verified the Google Sheet mirror works (row A361:N361). Added a system-context briefing for the next agent."})
    log("user_prompt", "Now make sure a second agent can load the exact same context.",
        payload={"full_text": "Now make sure a second agent can load the exact same context from the spreadsheet."})
    log("agent_response", "Built handoff CLI: snapshot stores a rich handoff row; hydrate returns briefing+transcript for the next agent.",
        payload={"full_text": "Built the handoff CLI. snapshot compresses + stores the handoff; hydrate returns the briefing and full transcript that the next agent injects as system context."})
    log("session_end", "Session ended (completed)")

    print("Waiting 6s for BigQuery streaming buffer...")
    time.sleep(6)

    print("\n=== HANDOFF: compressing + storing to BigQuery + Google Sheet ===")
    res = save_compressed_context(developer_id=DEV, agent_tool="cursor", project_repo=REPO, session_id=SID)
    print("status:", res.get("status"))
    print("summary:", res.get("summary"))
    mirror = res.get("fivetran_mirror") or {}
    print("sheet row:", mirror.get("sheet_updated_range") or mirror.get("sheet_error") or "(none)")

    print("\n=== AGENT B (different tool/OS): loading the SAME context from memory ===")
    time.sleep(4)
    packed = load_latest_compressed_context(REPO)
    blob = packed.get("context_json") or {}
    from modex_mcp.context_compress import render_hydration_from_context

    hydration = render_hydration_from_context(blob)
    print(f"\n--- SYSTEM CONTEXT delivered to Agent B ({len(hydration)} chars) ---\n")
    print(hydration[:2600])
    print("\n--- (truncated for display) ---")

    turns = len(blob.get("transcript") or [])
    decisions = len(blob.get("decisions") or [])
    ok = turns >= 6 and decisions >= 2 and "system context" in hydration.lower()
    print(f"\nturns={turns} decisions={decisions}")
    print("RESULT:", "PASS - Agent B received the real, structured handoff" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
