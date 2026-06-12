"""
Plane API v1 client for the Medha MCP server.

Uses Plane's API v1 endpoints, which support X-Api-Key authentication.
"""

import os
from typing import Any, Dict, List, Optional

import httpx


class PlaneClient:
    """Thin async client for Plane self-hosted API v1."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_token: Optional[str] = None,
    ):
        self.base_url = (base_url or os.environ.get("PLANE_API_BASE", "")).rstrip("/")
        self.api_token = api_token or os.environ.get("PLANE_API_TOKEN", "")
        if not self.base_url:
            raise ValueError("PLANE_API_BASE is required")
        if not self.api_token:
            raise ValueError("PLANE_API_TOKEN is required")

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"X-Api-Key": self.api_token, "Content-Type": "application/json"},
            timeout=30.0,
        )

    async def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        response = await self.client.get(path, params=params)
        response.raise_for_status()
        return response.json()

    async def post(self, path: str, json: Optional[Dict[str, Any]] = None) -> Any:
        response = await self.client.post(path, json=json)
        response.raise_for_status()
        return response.json()

    async def patch(self, path: str, json: Optional[Dict[str, Any]] = None) -> Any:
        response = await self.client.patch(path, json=json)
        response.raise_for_status()
        return response.json()

    async def delete(self, path: str) -> Any:
        response = await self.client.delete(path)
        response.raise_for_status()
        if response.status_code == 204:
            return {}
        return response.json()

    # ------------------------------------------------------------------
    # Workspaces
    # ------------------------------------------------------------------
    async def get_current_user(self) -> Dict[str, Any]:
        """Get the currently authenticated user."""
        return await self.get("/api/v1/users/me/")

    # ------------------------------------------------------------------
    # Projects
    # ------------------------------------------------------------------
    async def list_projects(self, workspace_slug: str) -> List[Dict[str, Any]]:
        data = await self.get(f"/api/v1/workspaces/{workspace_slug}/projects/")
        return data.get("results", [])

    async def create_project(
        self,
        workspace_slug: str,
        name: str,
        identifier: str,
        description: str = "",
        cycle_view: bool = True,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "name": name,
            "identifier": identifier,
            "cycle_view": cycle_view,
        }
        if description:
            payload["description"] = description
        return await self.post(
            f"/api/v1/workspaces/{workspace_slug}/projects/", json=payload
        )

    async def update_project(
        self,
        workspace_slug: str,
        project_id: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        return await self.patch(
            f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/",
            json=kwargs,
        )

    # ------------------------------------------------------------------
    # Issues (work-items)
    # ------------------------------------------------------------------
    async def list_issues(
        self,
        workspace_slug: str,
        project_id: str,
        state_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {}
        if state_id:
            params["state"] = state_id
        data = await self.get(
            f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/work-items/",
            params=params,
        )
        return data.get("results", [])

    async def create_issue(
        self,
        workspace_slug: str,
        project_id: str,
        name: str,
        description: str = "",
        state_id: Optional[str] = None,
        priority: Optional[str] = None,
        assignees: Optional[List[str]] = None,
        labels: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        target_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"name": name}
        if description:
            payload["description"] = {"content": [{"content": [{"text": description, "type": "text"}], "type": "paragraph"}], "type": "doc"}
        if state_id:
            payload["state_id"] = state_id
        if priority:
            payload["priority"] = priority
        if assignees:
            payload["assignees"] = assignees
        if labels:
            payload["labels"] = labels
        if start_date:
            payload["start_date"] = start_date
        if target_date:
            payload["target_date"] = target_date

        return await self.post(
            f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/work-items/",
            json=payload,
        )

    async def update_issue(
        self,
        workspace_slug: str,
        project_id: str,
        issue_id: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        return await self.patch(
            f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/work-items/{issue_id}/",
            json=kwargs,
        )

    # ------------------------------------------------------------------
    # States
    # ------------------------------------------------------------------
    async def list_states(self, workspace_slug: str, project_id: str) -> List[Dict[str, Any]]:
        data = await self.get(
            f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/states/"
        )
        return data.get("results", [])

    # ------------------------------------------------------------------
    # Cycles
    # ------------------------------------------------------------------
    async def list_cycles(self, workspace_slug: str, project_id: str) -> List[Dict[str, Any]]:
        data = await self.get(
            f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/cycles/"
        )
        return data.get("results", [])

    async def create_cycle(
        self,
        workspace_slug: str,
        project_id: str,
        name: str,
        start_date: str,
        end_date: str,
        description: str = "",
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "name": name,
            "start_date": start_date,
            "end_date": end_date,
            "project_id": project_id,
        }
        if description:
            payload["description"] = description
        return await self.post(
            f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/cycles/",
            json=payload,
        )

    # ------------------------------------------------------------------
    # Members
    # ------------------------------------------------------------------
    async def list_members(self, workspace_slug: str, project_id: str) -> List[Dict[str, Any]]:
        data = await self.get(
            f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/members/"
        )
        return data.get("results", [])

    async def close(self) -> None:
        await self.client.aclose()
