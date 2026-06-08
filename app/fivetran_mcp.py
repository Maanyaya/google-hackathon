"""Thin Fivetran MCP client — auto-injects required schema_file paths."""

from __future__ import annotations

import json
import os
from typing import Any

from app import config

# Every Fivetran MCP tool requires schema_file (OpenAPI guardrail).
SCHEMA_FILES: dict[str, str] = {
    "get_account_info": "open-api-definitions/account/get_account_info.json",
    "list_groups": "open-api-definitions/groups/list_all_groups.json",
    "list_destinations": "open-api-definitions/destinations/list_destinations.json",
    "list_connections": "open-api-definitions/connections/list_connections.json",
    "get_connection_details": "open-api-definitions/connections/connection_details.json",
    "sync_connection": "open-api-definitions/connections/sync_connection.json",
    "list_transformations": "open-api-definitions/transformations/transformations_list.json",
    "get_transformation_details": "open-api-definitions/transformations/transformation_details.json",
    "run_transformation": "open-api-definitions/transformations/run_transformation.json",
    "list_transformation_projects": "open-api-definitions/transformation-projects/list_all_transformation_projects.json",
    "get_transformation_project_details": "open-api-definitions/transformation-projects/transformation_project_details.json",
}


def _extract_text(call_result: Any) -> str:
    chunks: list[str] = []
    for item in getattr(call_result, "content", []) or []:
        text = getattr(item, "text", None)
        if text:
            chunks.append(text)
    return "\n".join(chunks).strip()


async def call_fivetran_tool(
    tool_name: str,
    extra_args: dict[str, Any] | None = None,
    *,
    allow_writes: bool = False,
) -> dict[str, Any]:
    """Call a Fivetran MCP tool (async — safe inside ADK event loop)."""
    if not config.FIVETRAN_API_KEY or not config.FIVETRAN_API_SECRET:
        return {
            "status": "error",
            "message": "Fivetran credentials missing. Set FIVETRAN_API_KEY and FIVETRAN_API_SECRET.",
        }

    schema_file = SCHEMA_FILES.get(tool_name)
    if not schema_file:
        return {"status": "error", "message": f"Unknown Fivetran tool: {tool_name}"}

    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError:
        return {"status": "error", "message": "mcp package not installed."}

    args = [a for a in config.FIVETRAN_MCP_ARGS.split(",") if a]
    server_env = {
        **os.environ,
        "FIVETRAN_API_KEY": config.FIVETRAN_API_KEY,
        "FIVETRAN_API_SECRET": config.FIVETRAN_API_SECRET,
        "FIVETRAN_ALLOW_WRITES": "true" if allow_writes else "false",
    }
    server_params = StdioServerParameters(
        command=config.FIVETRAN_MCP_COMMAND,
        args=args,
        env=server_env,
    )
    payload = {"schema_file": schema_file, **(extra_args or {})}

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, payload)
            text = _extract_text(result)
            is_error = bool(getattr(result, "isError", False))
            if is_error:
                return {"status": "error", "message": text or "Fivetran MCP tool error"}
            try:
                parsed = json.loads(text) if text else {}
            except json.JSONDecodeError:
                parsed = {"raw": text}
            return {"status": "success", "data": parsed}
