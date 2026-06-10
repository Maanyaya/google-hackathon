"""Smoke test MoDeX codebase log round-trip."""

from __future__ import annotations

import json

from modex_mcp.memory_store import (
    append_codebase_log,
    ensure_all_tables,
    load_context_from_logs,
)

DEMO_REPO = "github.com/demo/api-service"


def main() -> None:
    ensure_all_tables()

    append_codebase_log(
        developer_id="test-dev",
        agent_tool="antigravity",
        project_repo=DEMO_REPO,
        event_type="file_edit",
        summary="Patched auth token refresh logic",
        file_path="src/auth.py",
        payload={"lines_changed": 12},
    )

    load = load_context_from_logs(DEMO_REPO, limit=20)
    print("LOAD:", json.dumps(load, indent=2, default=str))
    print("\n--- HYDRATION PROMPT FOR NEW AGENT ---")
    print(load.get("hydration_prompt", ""))


if __name__ == "__main__":
    main()
