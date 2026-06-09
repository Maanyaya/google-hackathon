"""Unit tests for deterministic MoDeX context compression + transcript."""

from modex_mcp.context_compress import (
    SCHEMA_VERSION,
    compress_events,
    compression_summary_line,
    render_transcript_md,
)


def _sample_events():
    return [
        {
            "event_type": "session_start",
            "summary": "Cursor session started",
            "session_id": "s1",
            "developer_id": "dev1",
            "agent_tool": "cursor",
            "created_at": "2026-06-01T10:00:00Z",
            "payload_json": {},
        },
        {
            "event_type": "user_prompt",
            "summary": "Should we use PostgreSQL or MongoDB for auth?",
            "session_id": "s1",
            "developer_id": "dev1",
            "agent_tool": "cursor",
            "created_at": "2026-06-01T10:01:00Z",
            "payload_json": {"full_text": "Should we use PostgreSQL or MongoDB for auth?"},
        },
        {
            "event_type": "agent_response",
            "summary": "PostgreSQL is better for transactional auth.",
            "session_id": "s1",
            "developer_id": "dev1",
            "agent_tool": "cursor",
            "created_at": "2026-06-01T10:02:00Z",
            "payload_json": {"full_text": "PostgreSQL is better for transactional auth because ACID."},
        },
        {
            "event_type": "decision",
            "summary": "Use PostgreSQL not MongoDB",
            "session_id": "s1",
            "developer_id": "dev1",
            "agent_tool": "cursor",
            "created_at": "2026-06-01T10:05:00Z",
            "payload_json": {"decision": "Use PostgreSQL not MongoDB", "context": "PR review"},
        },
        {
            "event_type": "tool_call",
            "summary": "Shell: pytest tests/",
            "session_id": "s1",
            "developer_id": "dev1",
            "agent_tool": "cursor",
            "created_at": "2026-06-01T10:09:00Z",
            "payload_json": {"tool_name": "Shell", "tool_input": {"command": "pytest tests/"}},
        },
        {
            "event_type": "session_end",
            "summary": "Session ended",
            "session_id": "s1",
            "developer_id": "dev1",
            "agent_tool": "cursor",
            "created_at": "2026-06-01T10:15:00Z",
            "payload_json": {"rejected_approaches": ["MongoDB for auth store"]},
        },
    ]


def test_compress_builds_full_transcript():
    blob = compress_events(_sample_events(), project_repo="github.com/demo/api-service", session_id="s1")
    assert blob["schema"] == SCHEMA_VERSION
    transcript = blob["transcript"]
    roles = [t["role"] for t in transcript]
    assert "user" in roles
    assert "assistant" in roles
    assert "tool" in roles
    assert blob.get("transcript_md")
    assert "PostgreSQL is better" in blob["transcript_md"]
    assert "Should we use PostgreSQL" in blob["transcript_md"]


def test_compression_summary_line_includes_turns():
    blob = compress_events(_sample_events(), project_repo="github.com/demo/api-service")
    line = compression_summary_line(blob)
    assert "turns" in line
    assert SCHEMA_VERSION in line


def test_render_transcript_md_is_markdown():
    blob = compress_events(_sample_events(), project_repo="github.com/demo/api-service")
    md = render_transcript_md(blob)
    assert "# MoDeX session transcript" in md
    assert "Not a summary" in md
    assert "### [" in md
