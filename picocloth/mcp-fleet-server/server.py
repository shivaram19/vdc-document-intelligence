#!/usr/bin/env python3
"""
MCP Fleet Server — Authenticated Model Context Protocol for VDC Fleet

Research basis:
  - AIP (2026): Agent Identity Protocol — every MCP call must carry identity
  - Errico et al. (2025): 100% of 2,000 scanned MCP servers lacked auth
  - Red Hat (2026): Delegated token exchange — each hop gets scoped token

Design:
  - Stdio transport (zero-dependency, runs as subprocess)
  - Every tool call requires machine_token in arguments
  - Token verified against fleet_identity module
  - Operations logged to enterprise audit trail
  - VDC tools exposed: query, rfi, scan, ingest, list_projects
"""

import asyncio
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "agents"))
from fleet_identity import verify_machine_token, FLEET_REGISTRY, read_json
from enterprise_audit import AuditEvent, log_audit
from orchestrator import run_workflow
from vdc_core import read_state

NODE_ID = "mcp-fleet-server"
SHARED_DIR = Path(__file__).parent.parent / "shared"


def ensure_shared_dirs():
    for sub in ["doctrine", "project", "state", "run"]:
        (SHARED_DIR / sub).mkdir(parents=True, exist_ok=True)


def register_node(node_id: str, meta: dict):
    registry = SHARED_DIR / "state" / "fleet-registry.json"
    data = read_json(registry) if registry.exists() else {"nodes": {}}
    data.setdefault("nodes", {})[node_id] = {
        **meta,
        "last_seen": datetime.now(timezone.utc).isoformat(),
    }
    with open(registry, "w") as f:
        json.dump(data, f, indent=2)


def get_fleet_state() -> dict:
    registry = SHARED_DIR / "state" / "fleet-registry.json"
    if registry.exists():
        return read_json(registry)
    return {"nodes": {}}


def _audit(node_id: str, action: str, resource: str, outcome: str, details: dict = None):
    try:
        event = AuditEvent(
            actor=node_id, action=action, resource=resource,
            outcome=outcome, details=details or {}, node_id=node_id,
        )
        log_audit(event)
    except Exception as e:
        print(f"[mcp] Audit failed: {e}", file=sys.stderr)


def _auth_guard(arguments: dict) -> dict:
    """Verify machine token from tool arguments. Returns {ok, node_id, caps, error}."""
    token = arguments.get("machine_token", "").strip()
    if not token:
        return {"ok": False, "error": "Missing machine_token"}
    result = verify_machine_token(token)
    if not result["valid"]:
        return {"ok": False, "error": "Invalid or expired machine_token"}
    return {"ok": True, "node_id": result["node_id"], "caps": result["capabilities"]}


# ── VDC Tool Implementations ─────────────────────────────────────────────────
def vdc_query(arguments: dict) -> dict:
    auth = _auth_guard(arguments)
    if not auth["ok"]:
        _audit("unknown", "vdc_query", "*", "auth_denied", {"reason": auth["error"]})
        return {"error": auth["error"]}
    if "can_query" not in auth["caps"]:
        _audit(auth["node_id"], "vdc_query", "*", "cap_denied")
        return {"error": "Missing capability: can_query"}

    project = arguments.get("project", "default")
    query = arguments.get("query", "").strip()
    if not query:
        return {"error": "Empty query"}

    result = run_workflow("query", {"project": project, "query": query, "top_k": arguments.get("top_k", 5)})
    _audit(auth["node_id"], "vdc_query", project, "success", {"query_preview": query[:80]})
    return result


def vdc_rfi(arguments: dict) -> dict:
    auth = _auth_guard(arguments)
    if not auth["ok"]:
        _audit("unknown", "vdc_rfi", "*", "auth_denied", {"reason": auth["error"]})
        return {"error": auth["error"]}
    if "can_draft_rfi" not in auth["caps"]:
        _audit(auth["node_id"], "vdc_rfi", "*", "cap_denied")
        return {"error": "Missing capability: can_draft_rfi"}

    project = arguments.get("project", "default")
    question = arguments.get("question", "").strip()
    if not question:
        return {"error": "Empty question"}

    result = run_workflow("rfi", {
        "project": project,
        "question": question,
        "number": arguments.get("number", "RFI-MCP-" + str(int(time.time()))),
    })
    _audit(auth["node_id"], "vdc_rfi", project, "success", {"question_preview": question[:80]})
    return result


def vdc_scan(arguments: dict) -> dict:
    auth = _auth_guard(arguments)
    if not auth["ok"]:
        _audit("unknown", "vdc_scan", "*", "auth_denied", {"reason": auth["error"]})
        return {"error": auth["error"]}
    if "can_scan_contradictions" not in auth["caps"]:
        _audit(auth["node_id"], "vdc_scan", "*", "cap_denied")
        return {"error": "Missing capability: can_scan_contradictions"}

    project = arguments.get("project", "default")
    result = run_workflow("scan", {"project": project, "query": arguments.get("query", "")})
    _audit(auth["node_id"], "vdc_scan", project, "success")
    return result


def vdc_ingest(arguments: dict) -> dict:
    auth = _auth_guard(arguments)
    if not auth["ok"]:
        _audit("unknown", "vdc_ingest", "*", "auth_denied", {"reason": auth["error"]})
        return {"error": auth["error"]}
    if "can_upload" not in auth["caps"]:
        _audit(auth["node_id"], "vdc_ingest", "*", "cap_denied")
        return {"error": "Missing capability: can_upload"}

    fpath = arguments.get("file", "")
    if not fpath or not Path(fpath).exists():
        return {"error": "File not found"}

    result = run_workflow("ingest", {
        "project": arguments.get("project", "default"),
        "file": fpath,
        "doc_type": arguments.get("doc_type", "drawing"),
        "use_docling": arguments.get("use_docling", False),
    })
    _audit(auth["node_id"], "vdc_ingest", arguments.get("project", "default"), "success", {"file": fpath})
    return result


def vdc_list_projects(arguments: dict) -> dict:
    auth = _auth_guard(arguments)
    if not auth["ok"]:
        _audit("unknown", "vdc_list_projects", "*", "auth_denied", {"reason": auth["error"]})
        return {"error": auth["error"]}
    if "can_query" not in auth["caps"]:
        _audit(auth["node_id"], "vdc_list_projects", "*", "cap_denied")
        return {"error": "Missing capability: can_query"}

    projects = read_state().get("projects", [])
    _audit(auth["node_id"], "vdc_list_projects", "*", "success", {"count": len(projects)})
    return {"projects": projects, "count": len(projects)}


# ── Fleet Management Tools ───────────────────────────────────────────────────
def fleet_query_state(arguments: dict) -> dict:
    auth = _auth_guard(arguments)
    if not auth["ok"]:
        return {"error": auth["error"]}
    state = get_fleet_state()
    _audit(auth["node_id"], "fleet_query_state", "*", "success")
    return {"nodes": state.get("nodes", {}), "count": len(state.get("nodes", {}))}


def fleet_spawn_task(arguments: dict) -> dict:
    auth = _auth_guard(arguments)
    if not auth["ok"]:
        return {"error": auth["error"]}
    target = arguments.get("target_node", "")
    task = arguments.get("task", "")
    priority = arguments.get("priority", "normal")
    task_id = f"task-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{hash(task) % 10000}"

    task_file = SHARED_DIR / "state" / "task-queue.json"
    queue = []
    if task_file.exists():
        with open(task_file, "r") as f:
            queue = json.load(f)
    queue.append({
        "id": task_id, "target_node": target, "task": task,
        "priority": priority, "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(), "result": None,
    })
    with open(task_file, "w") as f:
        json.dump(queue, f, indent=2)

    _audit(auth["node_id"], "fleet_spawn_task", target, "success", {"task_id": task_id})
    return {"task_id": task_id, "status": "queued", "target": target}


# ── MCP Tool Definitions ─────────────────────────────────────────────────────
TOOLS = {
    "vdc_query": {
        "description": "Query the VDC document intelligence system using RAG",
        "parameters": {
            "type": "object",
            "properties": {
                "machine_token": {"type": "string", "description": "Fleet machine identity token"},
                "project": {"type": "string", "default": "default"},
                "query": {"type": "string", "description": "Natural language query"},
                "top_k": {"type": "integer", "default": 5},
            },
            "required": ["machine_token", "query"]
        }
    },
    "vdc_rfi": {
        "description": "Draft an RFI (Request for Information) from the VDC system",
        "parameters": {
            "type": "object",
            "properties": {
                "machine_token": {"type": "string"},
                "project": {"type": "string", "default": "default"},
                "question": {"type": "string"},
                "number": {"type": "string"},
            },
            "required": ["machine_token", "question"]
        }
    },
    "vdc_scan": {
        "description": "Scan for contradictions in project documents",
        "parameters": {
            "type": "object",
            "properties": {
                "machine_token": {"type": "string"},
                "project": {"type": "string", "default": "default"},
                "query": {"type": "string", "description": "Optional focus query"},
            },
            "required": ["machine_token"]
        }
    },
    "vdc_ingest": {
        "description": "Ingest a document into the VDC system",
        "parameters": {
            "type": "object",
            "properties": {
                "machine_token": {"type": "string"},
                "project": {"type": "string", "default": "default"},
                "file": {"type": "string", "description": "Absolute path to file"},
                "doc_type": {"type": "string", "default": "drawing"},
                "use_docling": {"type": "boolean", "default": False},
            },
            "required": ["machine_token", "file"]
        }
    },
    "vdc_list_projects": {
        "description": "List available VDC projects",
        "parameters": {
            "type": "object",
            "properties": {
                "machine_token": {"type": "string"},
            },
            "required": ["machine_token"]
        }
    },
    "fleet_query_state": {
        "description": "Get current fleet node status",
        "parameters": {
            "type": "object",
            "properties": {
                "machine_token": {"type": "string"},
            },
            "required": ["machine_token"]
        }
    },
    "fleet_spawn_task": {
        "description": "Delegate a task to a specific fleet node",
        "parameters": {
            "type": "object",
            "properties": {
                "machine_token": {"type": "string"},
                "target_node": {"type": "string"},
                "task": {"type": "string"},
                "priority": {"type": "string", "enum": ["low", "normal", "high", "critical"], "default": "normal"},
            },
            "required": ["machine_token", "target_node", "task"]
        }
    },
}


def handle_tool_call(name: str, arguments: dict) -> dict:
    try:
        if name == "vdc_query":
            return vdc_query(arguments)
        elif name == "vdc_rfi":
            return vdc_rfi(arguments)
        elif name == "vdc_scan":
            return vdc_scan(arguments)
        elif name == "vdc_ingest":
            return vdc_ingest(arguments)
        elif name == "vdc_list_projects":
            return vdc_list_projects(arguments)
        elif name == "fleet_query_state":
            return fleet_query_state(arguments)
        elif name == "fleet_spawn_task":
            return fleet_spawn_task(arguments)
        else:
            return {"error": f"Unknown tool: {name}"}
    except Exception as e:
        return {"error": str(e)}


def send(message: dict) -> None:
    print(json.dumps(message, ensure_ascii=False), flush=True)


async def main() -> None:
    ensure_shared_dirs()
    register_node(NODE_ID, {"role": "mcp-fleet-server", "tools": list(TOOLS.keys())})

    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
        except KeyboardInterrupt:
            break
        if not line:
            break

        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            continue

        req_id = request.get("id")
        method = request.get("method", "")

        if method == "initialize":
            send({
                "jsonrpc": "2.0", "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "picocloth-mcp-fleet-server", "version": "2.0.0-auth"},
                }
            })
        elif method == "tools/list":
            send({
                "jsonrpc": "2.0", "id": req_id,
                "result": {
                    "tools": [
                        {"name": k, "description": v["description"], "inputSchema": v["parameters"]}
                        for k, v in TOOLS.items()
                    ]
                }
            })
        elif method == "tools/call":
            params = request.get("params", {})
            result = handle_tool_call(params.get("name"), params.get("arguments", {}))
            send({
                "jsonrpc": "2.0", "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}],
                    "isError": "error" in result,
                }
            })
        elif method == "prompts/list":
            send({"jsonrpc": "2.0", "id": req_id, "result": {"prompts": []}})
        elif method == "resources/list":
            send({"jsonrpc": "2.0", "id": req_id, "result": {"resources": []}})


if __name__ == "__main__":
    asyncio.run(main())
