"""MoDeX Face 1 MCP server — developer-edge memory for Cursor / Antigravity / Windsurf."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from modex_mcp.memory_store import (
    append_codebase_log,
    get_memory_catalog,
    load_context_from_logs,
    load_session_history,
    load_team_context,
    log_decision,
    save_memory,
)

server = Server("modex-memory")


def _text(payload: dict[str, Any]) -> list[TextContent]:
    return [TextContent(type="text", text=json.dumps(payload, indent=2, default=str))]


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="append_codebase_log",
            description=(
                "PRIMARY: Append one immutable codebase/agent event to MoDeX shared memory. "
                "Use for session_start, tool_call, file_edit, decision, error, session_end. "
                "Logs are the source of truth for session handoff."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "developer_id": {"type": "string"},
                    "agent_tool": {"type": "string"},
                    "project_repo": {"type": "string"},
                    "event_type": {
                        "type": "string",
                        "enum": [
                            "session_start",
                            "user_prompt",
                            "tool_call",
                            "file_edit",
                            "decision",
                            "error",
                            "session_end",
                        ],
                    },
                    "summary": {"type": "string"},
                    "session_id": {"type": "string"},
                    "file_path": {"type": "string"},
                    "commit_sha": {"type": "string"},
                    "payload": {"type": "object"},
                    "parent_event_id": {"type": "string"},
                },
                "required": [
                    "developer_id",
                    "agent_tool",
                    "project_repo",
                    "event_type",
                    "summary",
                ],
            },
        ),
        Tool(
            name="load_context",
            description=(
                "PRIMARY: Hydrate a NEW coding-agent session with the team's shared "
                "decision memory. Returns a curated, provenance-stamped CONTEXT PACK that "
                "fuses coding-agent session decisions with GitHub PRs + reviews synced via "
                "Fivetran, cross-referenced and dated: adopted decisions, REJECTED approaches "
                "(don't redo), open questions, and known gotchas. Call at session start and "
                "build on `hydration_prompt` instead of starting cold."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_repo": {"type": "string"},
                    "limit": {"type": "integer", "default": 40},
                    "include_rag": {
                        "type": "boolean",
                        "default": False,
                        "description": "Also attach a conceptual note from Vertex AI RAG.",
                    },
                },
                "required": ["project_repo"],
            },
        ),
        Tool(
            name="load_context_from_logs",
            description=(
                "Replay recent raw codebase log events for a repo (lower-level than "
                "load_context). Returns chronological events + a basic hydration_prompt."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_repo": {"type": "string"},
                    "limit": {"type": "integer", "default": 50},
                    "event_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter: decision, file_edit, tool_call, etc.",
                    },
                    "session_id": {"type": "string"},
                },
                "required": ["project_repo"],
            },
        ),
        Tool(
            name="log_decision",
            description="Log one engineering decision as an append-only codebase event.",
            inputSchema={
                "type": "object",
                "properties": {
                    "developer_id": {"type": "string"},
                    "agent_tool": {"type": "string"},
                    "project_repo": {"type": "string"},
                    "decision": {"type": "string"},
                    "context": {"type": "string"},
                    "session_id": {"type": "string"},
                    "file_path": {"type": "string"},
                },
                "required": ["developer_id", "agent_tool", "project_repo", "decision"],
            },
        ),
        Tool(
            name="save_session_memory",
            description=(
                "End-of-session wrapper — writes session_end + decision events to codebase_logs."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "developer_id": {"type": "string"},
                    "agent_tool": {"type": "string"},
                    "project_repo": {"type": "string"},
                    "summary": {"type": "string"},
                    "decisions": {"type": "array", "items": {"type": "string"}},
                    "files_touched": {"type": "array", "items": {"type": "string"}},
                    "rejected_approaches": {"type": "array", "items": {"type": "string"}},
                    "session_id": {"type": "string"},
                },
                "required": ["developer_id", "agent_tool", "project_repo", "summary"],
            },
        ),
        Tool(
            name="load_team_context",
            description="Alias for load_context_from_logs (backward compatible).",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_repo": {"type": "string"},
                    "limit": {"type": "integer", "default": 50},
                },
                "required": ["project_repo"],
            },
        ),
        Tool(
            name="load_session_history",
            description="Recent log events for one developer (tool switch handoff).",
            inputSchema={
                "type": "object",
                "properties": {
                    "developer_id": {"type": "string"},
                    "project_repo": {"type": "string"},
                    "limit": {"type": "integer", "default": 50},
                },
                "required": ["developer_id"],
            },
        ),
        Tool(
            name="get_memory_catalog",
            description="List repos with codebase log activity.",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    args = arguments or {}
    if name == "load_context":
        try:
            from app.memory_graph import build_context_pack

            result = build_context_pack(
                project_repo=args["project_repo"],
                limit=int(args.get("limit", 40)),
                include_rag=bool(args.get("include_rag", False)),
            )
        except Exception as exc:  # noqa: BLE001
            result = {
                "status": "error",
                "message": f"context pack failed, falling back to raw logs: {exc}",
                "fallback": load_context_from_logs(
                    project_repo=args["project_repo"],
                    limit=int(args.get("limit", 40)),
                ),
            }
    elif name == "append_codebase_log":
        result = append_codebase_log(
            developer_id=args["developer_id"],
            agent_tool=args["agent_tool"],
            project_repo=args["project_repo"],
            event_type=args["event_type"],
            summary=args["summary"],
            session_id=args.get("session_id"),
            file_path=args.get("file_path"),
            commit_sha=args.get("commit_sha"),
            payload=args.get("payload"),
            parent_event_id=args.get("parent_event_id"),
        )
    elif name == "load_context_from_logs":
        result = load_context_from_logs(
            project_repo=args["project_repo"],
            limit=int(args.get("limit", 50)),
            event_types=args.get("event_types"),
            session_id=args.get("session_id"),
        )
    elif name == "save_session_memory":
        result = save_memory(
            developer_id=args["developer_id"],
            agent_tool=args["agent_tool"],
            project_repo=args["project_repo"],
            summary=args["summary"],
            decisions=args.get("decisions"),
            files_touched=args.get("files_touched"),
            rejected_approaches=args.get("rejected_approaches"),
            session_id=args.get("session_id"),
        )
    elif name == "log_decision":
        result = log_decision(
            developer_id=args["developer_id"],
            agent_tool=args["agent_tool"],
            project_repo=args["project_repo"],
            decision=args["decision"],
            context=args.get("context", ""),
            session_id=args.get("session_id"),
            file_path=args.get("file_path"),
        )
    elif name == "load_team_context":
        result = load_team_context(
            project_repo=args["project_repo"],
            limit=int(args.get("limit", 50)),
        )
    elif name == "load_session_history":
        result = load_session_history(
            developer_id=args["developer_id"],
            project_repo=args.get("project_repo"),
            limit=int(args.get("limit", 50)),
        )
    elif name == "get_memory_catalog":
        result = get_memory_catalog()
    else:
        result = {"status": "error", "message": f"Unknown tool: {name}"}
    return _text(result)


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def cli() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    cli()
