"""Create MoDeX memory tables and seed realistic codebase log timeline."""

from __future__ import annotations

import json
import sys
import uuid

from modex_mcp.memory_store import append_codebase_log, ensure_all_tables, save_memory

DEMO_REPO = "github.com/demo/api-service"
DEMO_DEV = "gagan@demo.dev"
DEMO_SESSION = str(uuid.uuid4())


def seed_antigravity_session() -> list[dict]:
    """Simulate a full Antigravity session as append-only events."""
    sid = DEMO_SESSION
    events = [
        ("session_start", "Opened api-service on branch feature/jwt-auth", {}),
        (
            "user_prompt",
            "Implement JWT auth — should we use MongoDB or PostgreSQL?",
            {"prompt": "Implement JWT auth..."},
        ),
        (
            "tool_call",
            "grep 'database' across src/",
            {"tool": "grep", "pattern": "database"},
        ),
        (
            "decision",
            "Use PostgreSQL for auth — need transactional consistency",
            {"rejected": ["MongoDB"]},
        ),
        (
            "file_edit",
            "Created src/auth.py with JWT middleware",
            {"file": "src/auth.py", "lines_added": 87},
        ),
        (
            "file_edit",
            "Updated docs/adr-001-database.md",
            {"file": "docs/adr-001-database.md"},
        ),
        (
            "tool_call",
            "Run pytest tests/test_auth.py",
            {"tool": "pytest", "command": "pytest tests/test_auth.py"},
        ),
        (
            "error",
            "test_auth_token_expired failed — missing clock skew handling",
            {"test": "test_auth_token_expired", "line": 42},
        ),
    ]
    results = []
    parent_id = None
    for event_type, summary, payload in events:
        fp = payload.get("file") if isinstance(payload, dict) else None
        r = append_codebase_log(
            developer_id=DEMO_DEV,
            agent_tool="antigravity",
            project_repo=DEMO_REPO,
            event_type=event_type,
            summary=summary,
            session_id=sid,
            file_path=fp,
            payload=payload if isinstance(payload, dict) else {},
            parent_event_id=parent_id,
        )
        parent_id = r.get("event_id")
        results.append(r)
    return results


def main() -> int:
    print("Creating MoDeX memory tables...")
    print(json.dumps(ensure_all_tables(), indent=2))

    print("\nSeeding Antigravity session log timeline...")
    seed_antigravity_session()

    print("\nSeeding session_end + Antigravity handoff continuation...")
    save_result = save_memory(
        developer_id=DEMO_DEV,
        agent_tool="antigravity",
        project_repo=DEMO_REPO,
        summary="JWT auth in progress. PostgreSQL chosen. Fix clock skew in test_auth.",
        decisions=["PostgreSQL over MongoDB", "JWT over session cookies"],
        files_touched=["src/auth.py", "docs/adr-001-database.md"],
        rejected_approaches=["MongoDB for auth"],
        session_id=DEMO_SESSION,
    )
    print(json.dumps(save_result, indent=2, default=str))

    handoff = append_codebase_log(
        developer_id="teammate@demo.dev",
        agent_tool="antigravity",
        project_repo=DEMO_REPO,
        event_type="session_start",
        summary="New Antigravity session — loading team context from prior handoff",
        payload={"prior_session": DEMO_SESSION, "prior_tool": "antigravity"},
    )
    print(json.dumps(handoff, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
