"""Add one demo row to MoDex_Logs sheet so Fivetran has data to sync."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from modex_mcp.memory_store import CODEBASE_LOG_COLUMNS, _append_sheet_row, _parse_sheet_id
import modex_mcp.memory_store as ms

SHEET_ID = _parse_sheet_id(ms.MEMORY_SHEET_ID or "1NKxRyKBBgBzETtaaPO_gPC8vdM1i4vtt5yxrq6iCRck")


def main() -> int:
    if not SHEET_ID:
        print("ERROR: Set MODEX_MEMORY_SHEET_ID in ../.env")
        return 1

    row = {
        "event_id": str(uuid.uuid4()),
        "session_id": str(uuid.uuid4()),
        "developer_id": "gagantak00@gmail.com",
        "agent_tool": "antigravity",
        "project_repo": "github.com/demo/api-service",
        "event_type": "decision",
        "file_path": "src/auth.py",
        "commit_sha": "",
        "summary": "Seed row for Fivetran stowed_register sync test",
        "payload_json": json.dumps({"source": "seed_modex_sheet_row"}),
        "parent_event_id": "",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    print(f"Sheet: {SHEET_ID}")
    print(f"Range: {ms.LOG_SHEET_RANGE}")
    result = _append_sheet_row(row, CODEBASE_LOG_COLUMNS, ms.LOG_SHEET_RANGE)
    if result and "sheet_error" in result:
        print("FAILED:", result["sheet_error"])
        print("\nFix: run")
        print("  gcloud auth application-default login --scopes=https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/spreadsheets")
        print("And share the sheet with your Google account as Editor.")
        return 1
    print("SUCCESS:", result)
    print("\nNext: Fivetran -> stowed_register -> Sync now")
    print("Then: uv run python scripts/check_modex_fivetran_table.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
