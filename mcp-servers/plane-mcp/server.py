#!/usr/bin/env python3
"""
Plane MCP Server

Exposes Medha's self-hosted Plane instance as a set of MCP tools.
Agents can read projects, issues, cycles, and states, and create or update issues.

Environment variables:
  PLANE_API_BASE  - e.g. https://plane.trayini.ai
  PLANE_API_TOKEN - Plane API v1 token (X-Api-Key)
"""

import json
import os
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from client import PlaneClient


server = Server("plane-mcp")


def _client() -> PlaneClient:
    return PlaneClient()


@server.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="plane_get_current_user",
            description="Get the currently authenticated Plane user.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="plane_list_projects",
            description="List projects in a Plane workspace.",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_slug": {
                        "type": "string",
                        "description": "Workspace slug (e.g. 'medha')",
                    }
                },
                "required": ["workspace_slug"],
            },
        ),
        Tool(
            name="plane_create_project",
            description="Create a new project in a Plane workspace.",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_slug": {"type": "string"},
                    "name": {"type": "string"},
                    "identifier": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["workspace_slug", "name", "identifier"],
            },
        ),
        Tool(
            name="plane_list_states",
            description="List states (statuses) in a Plane project.",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_slug": {"type": "string"},
                    "project_id": {"type": "string"},
                },
                "required": ["workspace_slug", "project_id"],
            },
        ),
        Tool(
            name="plane_list_issues",
            description="List work items (issues) in a Plane project.",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_slug": {"type": "string"},
                    "project_id": {"type": "string"},
                    "state_id": {"type": "string"},
                },
                "required": ["workspace_slug", "project_id"],
            },
        ),
        Tool(
            name="plane_create_issue",
            description="Create a work item in a Plane project.",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_slug": {"type": "string"},
                    "project_id": {"type": "string"},
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "state_id": {"type": "string"},
                    "priority": {"type": "string", "enum": ["urgent", "high", "medium", "low"]},
                    "assignees": {"type": "array", "items": {"type": "string"}},
                    "labels": {"type": "array", "items": {"type": "string"}},
                    "start_date": {"type": "string"},
                    "target_date": {"type": "string"},
                },
                "required": ["workspace_slug", "project_id", "name"],
            },
        ),
        Tool(
            name="plane_update_issue",
            description="Update a work item in a Plane project.",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_slug": {"type": "string"},
                    "project_id": {"type": "string"},
                    "issue_id": {"type": "string"},
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "state_id": {"type": "string"},
                    "priority": {"type": "string"},
                },
                "required": ["workspace_slug", "project_id", "issue_id"],
            },
        ),
        Tool(
            name="plane_list_cycles",
            description="List cycles (sprints) in a Plane project.",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_slug": {"type": "string"},
                    "project_id": {"type": "string"},
                },
                "required": ["workspace_slug", "project_id"],
            },
        ),
        Tool(
            name="plane_create_cycle",
            description="Create a cycle in a Plane project.",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_slug": {"type": "string"},
                    "project_id": {"type": "string"},
                    "name": {"type": "string"},
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["workspace_slug", "project_id", "name", "start_date", "end_date"],
            },
        ),
        Tool(
            name="plane_list_members",
            description="List members of a Plane project.",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_slug": {"type": "string"},
                    "project_id": {"type": "string"},
                },
                "required": ["workspace_slug", "project_id"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    client = _client()
    try:
        if name == "plane_get_current_user":
            result = await client.get_current_user()

        elif name == "plane_list_projects":
            result = await client.list_projects(arguments["workspace_slug"])

        elif name == "plane_create_project":
            result = await client.create_project(
                workspace_slug=arguments["workspace_slug"],
                name=arguments["name"],
                identifier=arguments["identifier"],
                description=arguments.get("description", ""),
            )

        elif name == "plane_list_states":
            result = await client.list_states(
                arguments["workspace_slug"], arguments["project_id"]
            )

        elif name == "plane_list_issues":
            result = await client.list_issues(
                workspace_slug=arguments["workspace_slug"],
                project_id=arguments["project_id"],
                state_id=arguments.get("state_id"),
            )

        elif name == "plane_create_issue":
            result = await client.create_issue(
                workspace_slug=arguments["workspace_slug"],
                project_id=arguments["project_id"],
                name=arguments["name"],
                description=arguments.get("description", ""),
                state_id=arguments.get("state_id"),
                priority=arguments.get("priority"),
                assignees=arguments.get("assignees"),
                labels=arguments.get("labels"),
                start_date=arguments.get("start_date"),
                target_date=arguments.get("target_date"),
            )

        elif name == "plane_update_issue":
            kwargs = {k: v for k, v in arguments.items() if k not in ("workspace_slug", "project_id", "issue_id")}
            result = await client.update_issue(
                workspace_slug=arguments["workspace_slug"],
                project_id=arguments["project_id"],
                issue_id=arguments["issue_id"],
                **kwargs,
            )

        elif name == "plane_list_cycles":
            result = await client.list_cycles(
                arguments["workspace_slug"], arguments["project_id"]
            )

        elif name == "plane_create_cycle":
            result = await client.create_cycle(
                workspace_slug=arguments["workspace_slug"],
                project_id=arguments["project_id"],
                name=arguments["name"],
                start_date=arguments["start_date"],
                end_date=arguments["end_date"],
                description=arguments.get("description", ""),
            )

        elif name == "plane_list_members":
            result = await client.list_members(
                arguments["workspace_slug"], arguments["project_id"]
            )

        else:
            raise ValueError(f"Unknown tool: {name}")

        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]

    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}, indent=2))]
    finally:
        await client.close()


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
