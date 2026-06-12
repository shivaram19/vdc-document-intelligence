#!/usr/bin/env python3
"""
Seed Medha's marketing pipeline into Plane.

Idempotent: safe to re-run. Creates the Marketing project if missing, ensures
Cycles are enabled, creates default states if absent, and creates the standard
marketing tasks and weekly cycles only when they do not already exist.

Environment:
  PLANE_API_BASE  - Plane base URL (default: http://127.0.0.1:8091)
  PLANE_API_TOKEN - Plane API v1 token (X-Api-Key)
  PLANE_WORKSPACE - Workspace slug (default: medha)
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

# Allow importing the plane-mcp client without installing it as a package.
MCP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mcp-servers", "plane-mcp")
sys.path.insert(0, MCP_DIR)

from client import PlaneClient  # noqa: E402


PLANE_WORKSPACE = os.environ.get("PLANE_WORKSPACE", "medha")
PROJECT_NAME = "Marketing"
PROJECT_IDENTIFIER = "MKT"
PROJECT_DESCRIPTION = "Marketing pipeline, content calendar, and go-to-market execution for Medha."

# Default Plane state names we expect. The script maps these to task statuses.
DEFAULT_STATES = ["Backlog", "Todo", "In Progress", "Done", "Cancelled"]

TASKS: List[tuple[str, str, Optional[str]]] = [
    # (name, state_name, optional_description)
    ("[Content & Authority] Write founder-led LinkedIn post: outcome-first construction problem", "Todo", None),
    ("[Content & Authority] Write Twitter/X thread: soft problem-first \"We See It Too\"", "Todo", None),
    ("[Content & Authority] Publish landing page case study from pilot feedback", "Todo", None),
    ("[Content & Authority] Update website FAQ based on common pilot objections", "Todo", None),
    ("[Customer Discovery] Build target list: 50 VDC/GC prospects in Dubai/GCC", "Todo", None),
    ("[Customer Discovery] Run 5 discovery calls with VDC coordinators or BIM managers", "Todo", None),
    ("[Customer Discovery] Synthesize call notes into 1-page ICP update", "Todo", None),
    ("[Customer Discovery] Validate pilot pricing with 3 prospects", "Todo", None),
    ("[Pilot & Sales] Set up customized pilot for first qualified prospect", "Todo", None),
    ("[Pilot & Sales] Deliver pilot report: contradictions found and time saved", "Todo", None),
    ("[Pilot & Sales] Follow up on pilot: close or iterate", "Todo", None),
    ("[Product & Engineering] Deploy Sunday production release checklist", "Todo", None),
    ("[Product & Engineering] Fix dependency vulnerabilities: chromadb, gunicorn, requests", "Todo", None),
    ("[Product & Engineering] Rotate exposed OpenAI and XAI keys", "Todo", None),
    ("[Operations] Weekly backup verification", "Todo", None),
    ("[Operations] SSL expiry check and renewal dry-run", "Todo", None),
    ("[Operations] Uptime report for plane.trayini.ai and medha.trayini.ai", "Todo", None),
]


def this_monday(reference: datetime | None = None) -> datetime:
    ref = reference or datetime.utcnow()
    return ref - timedelta(days=ref.weekday())


def week_bounds(anchor: datetime, weeks_ahead: int) -> tuple[str, str]:
    start = anchor + timedelta(weeks=weeks_ahead)
    end = start + timedelta(days=6)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


async def get_or_create_project(client: PlaneClient) -> Dict[str, Any]:
    projects = await client.list_projects(PLANE_WORKSPACE)
    for project in projects:
        if project.get("name") == PROJECT_NAME:
            print(f"Using existing project '{PROJECT_NAME}' ({project['id']}).")
            if not project.get("cycle_view"):
                print("Enabling cycle view on existing project...")
                project = await client.update_project(
                    PLANE_WORKSPACE, project["id"], cycle_view=True
                )
            return project

    print(f"Creating project '{PROJECT_NAME}'...")
    project = await client.create_project(
        workspace_slug=PLANE_WORKSPACE,
        name=PROJECT_NAME,
        identifier=PROJECT_IDENTIFIER,
        description=PROJECT_DESCRIPTION,
        cycle_view=True,
    )
    print(f"Created project '{PROJECT_NAME}' ({project['id']}).")
    return project


async def map_states(client: PlaneClient, project_id: str) -> Dict[str, str]:
    states = await client.list_states(PLANE_WORKSPACE, project_id)
    state_map = {s["name"]: s["id"] for s in states}
    missing = [name for name in DEFAULT_STATES if name not in state_map]
    if missing:
        print(f"Warning: project is missing expected states: {missing}")
    return state_map


async def seed_tasks(client: PlaneClient, project_id: str, state_map: Dict[str, str]) -> None:
    existing = {issue["name"]: issue["id"] for issue in await client.list_issues(PLANE_WORKSPACE, project_id)}
    created = 0
    skipped = 0
    for name, state_name, description in TASKS:
        if name in existing:
            skipped += 1
            continue
        state_id = state_map.get(state_name)
        if state_name and not state_id:
            print(f"Warning: state '{state_name}' not found for task '{name}', creating in default state.")
        await client.create_issue(
            workspace_slug=PLANE_WORKSPACE,
            project_id=project_id,
            name=name,
            description=description or "",
            state_id=state_id,
        )
        created += 1
    print(f"Tasks: {created} created, {skipped} already present.")


def _parse_cycle_date(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        # Plane returns ISO-8601 timestamps; truncate to the date portion.
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    raise ValueError(f"Cannot parse cycle date: {value!r}")


def _cycles_overlap(start: datetime, end: datetime, existing: List[Dict[str, Any]]) -> bool:
    for cycle in existing:
        try:
            c_start = _parse_cycle_date(cycle["start_date"])
            c_end = _parse_cycle_date(cycle["end_date"])
        except (KeyError, ValueError):
            continue
        if start <= c_end and c_start <= end:
            return True
    return False


async def seed_cycles(client: PlaneClient, project_id: str) -> None:
    existing = await client.list_cycles(PLANE_WORKSPACE, project_id)
    created = 0
    skipped = 0
    failed = 0
    anchor = this_monday()
    for i in range(3):
        start_str, end_str = week_bounds(anchor, i)
        start = datetime.strptime(start_str, "%Y-%m-%d")
        end = datetime.strptime(end_str, "%Y-%m-%d")
        name = f"{start.strftime('%b %d')} — {end.strftime('%b %d')}"
        if any(cycle.get("name") == name for cycle in existing):
            skipped += 1
            continue
        if _cycles_overlap(start, end, existing):
            print(f"Skipping cycle '{name}' because it overlaps an existing cycle.")
            skipped += 1
            continue
        try:
            await client.create_cycle(
                workspace_slug=PLANE_WORKSPACE,
                project_id=project_id,
                name=name,
                start_date=start_str,
                end_date=end_str,
            )
            created += 1
            existing.append({"name": name, "start_date": start_str, "end_date": end_str})
        except Exception as exc:
            print(f"Failed to create cycle '{name}': {exc}")
            failed += 1
    print(f"Cycles: {created} created, {skipped} skipped, {failed} failed.")


async def main() -> int:
    client = PlaneClient()
    try:
        user = await client.get_current_user()
        print(f"Authenticated as {user.get('email', user.get('id'))}.")

        project = await get_or_create_project(client)
        project_id = project["id"]

        state_map = await map_states(client, project_id)
        await seed_tasks(client, project_id, state_map)
        await seed_cycles(client, project_id)

        print("\nSeed complete. Marketing project:")
        print(f"  URL: /{PLANE_WORKSPACE}/projects/{project.get('identifier', PROJECT_IDENTIFIER)}/")
        print(f"  ID: {project_id}")
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    finally:
        await client.close()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
