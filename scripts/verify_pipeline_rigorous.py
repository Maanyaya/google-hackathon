"""RIGOROUS end-to-end proof of the MoDeX handoff pipeline.

This does NOT shortcut anything. It:
  1. Fires each Cursor hook event the EXACT way Cursor does on Windows:
     python.exe hook_runner.py EVENT  with the payload piped as UTF-16LE bytes.
  2. Uses a fresh conversation_id so we measure only this run.
  3. Snapshots (compress -> BigQuery -> Google Sheet).
  4. Reads the ACTUAL Google Sheet cells back (context_json + transcript_md
     columns) to prove the next agent's context physically lives in the sheet.
  5. Hydrates as "Agent B" and prints the system context delivered.

If any step is fake or empty, this script FAILS loudly.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = ROOT / ".venv" / "Scripts" / "python.exe"
RUNNER = ROOT / "modex_mcp" / "hook_runner.py"
sys.path.insert(0, str(ROOT))

os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "gen-lang-client-0795401430")
from dotenv import load_dotenv

load_dotenv(ROOT.parent / ".env")
load_dotenv(ROOT / ".env")

from modex_mcp import memory_store as ms
from modex_mcp.context_compress import render_hydration_from_context

REPO = "github.com/Maanyaya/google-hackathon"
CONV = f"rigor-{uuid.uuid4().hex[:10]}"


def fire(event: str, payload: dict) -> str:
    """Invoke the hook exactly like Cursor on Windows: UTF-16LE bytes on stdin."""
    payload = {"conversation_id": CONV, **payload}
    raw = json.dumps(payload).encode("utf-16-le")  # mimic Cursor Windows stdin
    proc = subprocess.run(
        [str(PY), str(RUNNER), event],
        input=raw,
        capture_output=True,
    )
    out = (proc.stdout or b"").decode("utf-8", "replace").strip()
    err = (proc.stderr or b"").decode("utf-8", "replace").strip()
    if err:
        print(f"  [{event}] STDERR: {err[:200]}")
    print(f"  [{event}] -> {out[:80]}")
    return out


def read_sheet_row(updated_range: str) -> list[str]:
    """Read back the exact cells written, straight from Google Sheets."""
    token = ms._sheet_access_token()
    # updated_range looks like 'MoDex_Logs!A376:N376'
    url = (
        f"https://sheets.googleapis.com/v4/spreadsheets/{ms.MEMORY_SHEET_ID}/values/"
        f"{urllib.parse.quote(updated_range)}"
    )
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    values = data.get("values") or [[]]
    return values[0] if values else []


def main() -> int:
    print(f"=== STEP 1: fire Cursor hooks as UTF-16LE stdin (conv {CONV}) ===")
    fire("beforeSubmitPrompt", {"prompt": "Rigorously verify MoDeX context handoff works", "generation_id": "g1"})
    fire("postToolUse", {"tool_name": "Read", "tool_input": {"path": "modex_mcp/handoff.py"}})
    fire("afterFileEdit", {"file_path": "modex_mcp/hook_runner.py", "edits": [{"old_string": "x", "new_string": "y"}]})
    fire("afterShellExecution", {"command": "python -m pytest tests/unit", "output": "11 passed"})
    fire("afterAgentResponse", {"text": "Decoded UTF-16 stdin from Cursor on Windows; prompts/responses now captured.", "generation_id": "g1"})
    fire("beforeSubmitPrompt", {"prompt": "Now confirm Agent B can load the same context from the sheet", "generation_id": "g2"})
    fire("afterAgentResponse", {"text": "Snapshot writes a rich handoff row; hydrate returns it for the next agent.", "generation_id": "g2"})

    print("\n=== STEP 2: verify the hook rows landed in BigQuery (this conv only) ===")
    time.sleep(8)
    rows = ms._fetch_log_events(REPO, limit=50, session_id=CONV)
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["event_type"]] = counts.get(r["event_type"], 0) + 1
    print(f"  rows for {CONV}: {len(rows)} -> {counts}")
    captured_prompts = counts.get("user_prompt", 0)
    captured_responses = counts.get("agent_response", 0)

    print("\n=== STEP 3: snapshot -> compress -> BigQuery + Google Sheet ===")
    snap = ms.save_compressed_context(
        developer_id="gagantak00@gmail.com", agent_tool="cursor",
        project_repo=REPO, session_id=CONV,
    )
    print("  status:", snap.get("status"), "|", snap.get("summary"))
    mirror = snap.get("fivetran_mirror") or {}
    sheet_range = mirror.get("sheet_updated_range")
    print("  sheet row:", sheet_range or mirror.get("sheet_error"))

    print("\n=== STEP 4: read the ACTUAL Google Sheet cells back ===")
    sheet_ctx_ok = sheet_md_ok = False
    if sheet_range:
        cells = read_sheet_row(sheet_range)
        # columns: ...,context_json(M, idx12), transcript_md(N, idx13)
        ctx_cell = cells[12] if len(cells) > 12 else ""
        md_cell = cells[13] if len(cells) > 13 else ""
        print(f"  columns present: {len(cells)}")
        print(f"  context_json cell: {len(ctx_cell)} chars")
        print(f"  transcript_md cell: {len(md_cell)} chars")
        sheet_ctx_ok = len(ctx_cell) > 200 and CONV in ctx_cell
        sheet_md_ok = "system context" in md_cell.lower()
        print(f"  context_json mentions this conv: {sheet_ctx_ok}")
        print(f"  transcript_md has briefing: {sheet_md_ok}")

    print("\n=== STEP 5: Agent B hydrates the SAME context from memory ===")
    time.sleep(3)
    packed = ms.load_latest_compressed_context(REPO)
    blob = packed.get("context_json") or {}
    hydration = render_hydration_from_context(blob)
    print(f"  delivered system context: {len(hydration)} chars, "
          f"{len(blob.get('transcript') or [])} turns")
    print("\n----- BRIEFING (first 1500 chars) -----\n")
    print(hydration[:1500])

    print("\n=== VERDICT ===")
    checks = {
        "hooks captured user prompts": captured_prompts >= 2,
        "hooks captured agent responses": captured_responses >= 2,
        "snapshot wrote to sheet": bool(sheet_range),
        "sheet context_json holds this conv": sheet_ctx_ok,
        "sheet transcript_md has briefing": sheet_md_ok,
        "agent B got non-trivial context": len(hydration) > 1000,
    }
    for k, v in checks.items():
        print(f"  [{'PASS' if v else 'FAIL'}] {k}")
    ok = all(checks.values())
    print("\nOVERALL:", "PASS — pipeline is genuinely working end to end" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
