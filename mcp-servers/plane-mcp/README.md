# plane-mcp

MCP server for Medha's self-hosted Plane instance.

## What it does

Exposes Plane projects, issues, cycles, states, and members as MCP tools so agents can:

- Read the current project state
- Create and update work items
- Plan cycles (sprints)
- Look up available states and members

## Setup

1. Create a Plane API token (already done via Django shell for the admin user).
2. Set environment variables:

```bash
export PLANE_API_BASE="https://plane.trayini.ai"
export PLANE_API_TOKEN="your-token"
```

3. Install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

4. Run the server:

```bash
python server.py
```

## Tools

| Tool | Purpose |
|---|---|
| `plane_get_current_user` | Verify authentication |
| `plane_list_projects` | List projects in the workspace |
| `plane_create_project` | Create a new project |
| `plane_list_states` | List project states (backlog, in progress, done, etc.) |
| `plane_list_issues` | List work items in a project |
| `plane_create_issue` | Create a work item |
| `plane_update_issue` | Update a work item |
| `plane_list_cycles` | List cycles |
| `plane_create_cycle` | Create a cycle |
| `plane_list_members` | List project members |

## Claude Desktop config

```json
{
  "mcpServers": {
    "plane": {
      "command": "/path/to/.venv/bin/python",
      "args": ["/path/to/mcp-servers/plane-mcp/server.py"],
      "env": {
        "PLANE_API_BASE": "https://plane.trayini.ai",
        "PLANE_API_TOKEN": "your-token"
      }
    }
  }
}
```

## Notes

- Uses Plane API v1 (`/api/v1/`) which supports `X-Api-Key` token authentication.
- The self-hosted `/api/` app endpoints use session auth and are not used here.
