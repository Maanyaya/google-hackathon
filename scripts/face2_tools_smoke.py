"""Smoke-test Face 2 specialist tools (no LLM — direct tool calls)."""

from __future__ import annotations

import json
import sys

from app.tools import (
    get_agent_memory_catalog,
    get_agent_memory_for_project,
    get_codebase_log_timeline,
    get_modex_fivetran_logs,
    get_data_catalog,
)

DEMO_REPO = "github.com/demo/api-service"


def _print(title: str, payload: dict) -> None:
    print(f"\n=== {title} ===")
    print(json.dumps(payload, indent=2, default=str)[:2000])


def main() -> int:
    checks = [
        ("memory_catalog", get_agent_memory_catalog()),
        (
            "session_handoff",
            get_agent_memory_for_project(DEMO_REPO, limit=10),
        ),
        (
            "timeline_decisions",
            get_codebase_log_timeline(DEMO_REPO, event_types="decision,error", limit=10),
        ),
        ("fivetran_modex_logs", get_modex_fivetran_logs(DEMO_REPO, limit=10)),
        ("data_catalog", get_data_catalog()),
    ]
    failed = 0
    for name, result in checks:
        _print(name, result)
        if result.get("status") == "error":
            failed += 1
            print(f"FAIL: {name}")
    print("\n" + ("ALL FACE 2 TOOL CHECKS PASSED" if not failed else f"{failed} CHECK(S) FAILED"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
