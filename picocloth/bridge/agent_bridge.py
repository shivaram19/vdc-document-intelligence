#!/usr/bin/env python3
"""
VDC Agent Bridge — Enterprise Fleet↔Auth Gateway

WebSocket + HTTP Inbox + Agentic Auth Mesh + Fleet Machine Identity

SOLID compliance:
  S: Bridge ONLY routes messages. Auth → AuthFacade. Commands → handlers.
  O: New commands added via COMMAND_HANDLERS dict, no bridge modification.
  D: Bridge depends on AuthFacade abstraction, not concrete auth agents.

Enterprise additions:
  - Machine-to-Machine auth for fleet nodes (fleet_identity)
  - Rate limiting per identity (rate_limiter)
  - Input sanitization (input_sanitizer)
  - Tamper-evident audit trails (enterprise_audit)
  - Token exchange: machine_token → VDC capability_token

Research basis:
  - AIP (2026): Agent Identity Protocol — delegated token exchange across MCP
  - Red Hat (2026): Zero Trust for agentic AI — continuous verification + audit
  - Errico et al. (2025): Securing MCP — per-user auth, scoped authorization
  - Shahidinejad et al. (2021): Short-TTL capability tokens reduce attack surface
"""

import asyncio
import json
import os
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

import aiohttp
from aiohttp import web

sys.path.insert(0, str(Path(__file__).parent.parent / "agents"))
from orchestrator import run_workflow
from vdc_core import read_state, SHARED_DIR, INBOX_DIR, append_event, preload_model, is_model_ready
from auth import AuthFacade
from fleet_identity import (
    register_fleet_node,
    issue_machine_token,
    verify_machine_token,
    NODE_CAPABILITIES,
)
from rate_limiter import check_rate_limit, get_rate_status
from input_sanitizer import (
    sanitize_command,
    sanitize_inbox_upload,
    sanitize_project_id,
    sanitize_text_field,
    ValidationError,
)
from enterprise_audit import AuditEvent, log_audit

# ── Configuration ────────────────────────────────────────────────────────────
BRIDGE_HOST = os.environ.get("BRIDGE_HOST", "0.0.0.0")
BRIDGE_PORT = int(os.environ.get("BRIDGE_PORT", "8765"))
FLEET_AUTH_ENABLED = os.environ.get("FLEET_AUTH_ENABLED", "true").lower() == "true"

# Capabilities required for each action
CAPABILITY_MAP = {
    "query": "can_query",
    "rfi": "can_draft_rfi",
    "scan": "can_scan_contradictions",
    "ingest": "can_upload",
    "list_projects": None,
    "create_project": "can_manage_projects",
    # Fleet actions
    "fleet_register": None,
    "fleet_auth": None,
    "fleet_exchange": None,
    "fleet_status": None,
}

# ── WebSocket State ──────────────────────────────────────────────────────────
CLIENTS = set()      # (websocket, session_id, identity)
UNAUTH = set()       # websockets awaiting auth
FLEET_WS = set()     # fleet-node websockets


async def _broadcast(msg: dict, to_unauth: bool = False, to_fleet: bool = False):
    payload = json.dumps(msg, default=str)
    targets = {ws for ws, _, _ in CLIENTS}
    if to_unauth:
        targets |= UNAUTH
    if to_fleet:
        targets |= FLEET_WS
    dead = set()
    for ws in targets:
        try:
            asyncio.create_task(ws.send_str(payload))
        except Exception:
            dead.add(ws)
    for ws in dead:
        CLIENTS.discard((ws, None, None))
        UNAUTH.discard(ws)
        FLEET_WS.discard(ws)


def _audit(actor: str, action: str, resource: str, outcome: str,
           details: dict = None, token: str = "", node_id: str = "",
           ip: str = ""):
    """Fire-and-forget audit logging."""
    try:
        event = AuditEvent(
            actor=actor, action=action, resource=resource,
            outcome=outcome, details=details or {},
            capability_token=token, ip_address=ip, node_id=node_id,
        )
        log_audit(event)
    except Exception as e:
        print(f"[bridge] Audit logging failed: {e}")


# ── Shared Memory Watcher ────────────────────────────────────────────────────
async def watch_shared_memory():
    last = {cat: 0 for cat in ["tasks", "queries", "rfis", "contradictions", "auth"]}
    while True:
        for cat in last:
            for fpath in sorted((SHARED_DIR / cat).glob("*.jsonl")):
                try:
                    lines = fpath.read_text().strip().split("\n")
                    for line in lines[last[cat]:]:
                        if line.strip():
                            ev = json.loads(line)
                            ev["_stream_type"] = cat
                            await _broadcast(ev)
                    last[cat] = len(lines)
                except Exception:
                    pass
        await _broadcast({"type": "state_snapshot", "state": read_state()})
        await asyncio.sleep(2)


# ── Rate Limit Wrapper ───────────────────────────────────────────────────────
def _check_rate(identity: str, capability: str, ip: str) -> dict:
    """Check rate limit and log if exceeded."""
    result = check_rate_limit(identity, capability)
    if not result["allowed"]:
        _audit(
            actor=identity, action="rate_limit_exceeded",
            resource=capability or "global", outcome="denied",
            details={"retry_after": result.get("retry_after_sec")},
            ip=ip,
        )
    return result


# ── Input Sanitization Wrapper ───────────────────────────────────────────────
def _sanitize(cmd: dict) -> dict:
    """Sanitize command, returning sanitized dict or raising ValidationError."""
    allowed = set(CAPABILITY_MAP.keys())
    return sanitize_command(cmd, allowed_actions=allowed)


# ── Async Workflow Runner (avoids blocking the event loop) ───────────────────
async def _run_workflow_async(workflow: str, params: dict) -> dict:
    """Run a synchronous workflow in a thread pool."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, run_workflow, workflow, params)


# ── Pluggable Command Handlers (Open/Closed Principle) ───────────────────────
async def _handle_query(ws, cmd, request_id, project, identity, ip):
    result = await _run_workflow_async("query", {"project": project, "query": cmd["query"], "top_k": cmd.get("top_k", 5)})
    result.update({"type": "query_result", "request_id": request_id})
    await ws.send_str(json.dumps(result, default=str))
    await _broadcast(result)
    _audit(identity, "query", project, "success", {"query_preview": cmd["query"][:80]}, ip=ip)
    return None


async def _handle_rfi(ws, cmd, request_id, project, identity, ip):
    result = await _run_workflow_async("rfi", {
        "project": project,
        "question": cmd["question"],
        "number": cmd.get("number", "RFI-XXX"),
    })
    result.update({"type": "rfi_result", "request_id": request_id})
    await ws.send_str(json.dumps(result, default=str))
    await _broadcast(result)
    _audit(identity, "rfi", project, "success", {"question_preview": cmd["question"][:80]}, ip=ip)
    return None


async def _handle_scan(ws, cmd, request_id, project, identity, ip):
    result = await _run_workflow_async("scan", {"project": project, "query": cmd.get("query", "")})
    result.update({"type": "scan_result", "request_id": request_id})
    await ws.send_str(json.dumps(result, default=str))
    await _broadcast(result)
    _audit(identity, "scan", project, "success", ip=ip)
    return None


async def _handle_ingest(ws, cmd, request_id, project, identity, ip):
    fpath = cmd.get("file", "")
    path_obj = Path(fpath)
    if not path_obj.exists():
        _audit(identity, "ingest", project, "failure", {"reason": "file_not_found", "path": fpath}, ip=ip)
        return {"type": "error", "request_id": request_id, "error": "File not found"}
    result = await _run_workflow_async("ingest", {
        "project": project,
        "file": fpath,
        "doc_type": cmd.get("doc_type", "drawing"),
        "use_docling": cmd.get("use_docling", False),
    })
    result.update({"type": "ingest_result", "request_id": request_id})
    await ws.send_str(json.dumps(result, default=str))
    await _broadcast(result)
    _audit(identity, "ingest", project, "success", {"file": fpath}, ip=ip)
    return None


async def _handle_list_projects(ws, cmd, request_id, project, identity, ip):
    await ws.send_str(json.dumps({
        "type": "projects_list", "request_id": request_id,
        "projects": read_state().get("projects", []),
    }))
    _audit(identity, "list_projects", "*", "success", ip=ip)
    return None


async def _handle_create_project(ws, cmd, request_id, project, identity, ip):
    state = read_state()
    pid = f"proj_{int(time.time())}"
    state.setdefault("projects", []).append({
        "id": pid,
        "name": cmd.get("name", "Untitled"),
        "client": cmd.get("client", ""),
        "created": datetime.now().isoformat(),
        "docs": [],
    })
    from vdc_core import write_state
    write_state(state)
    await _broadcast({
        "type": "project_created", "request_id": request_id,
        "project": {"id": pid, "name": cmd.get("name", "Untitled"),
                    "client": cmd.get("client", "")},
    })
    _audit(identity, "create_project", pid, "success", ip=ip)
    return None


# ── Fleet Command Handlers ───────────────────────────────────────────────────
async def _handle_fleet_register(ws, cmd, request_id, identity, ip):
    """Register a fleet node (admin-only or bootstrap)."""
    node_id = cmd.get("node_id", "").strip()
    if not node_id.startswith("node-"):
        return {"type": "error", "request_id": request_id,
                "error": "Invalid node_id format. Expected node-a through node-j."}
    result = register_fleet_node(node_id, role=cmd.get("role", ""))
    await ws.send_str(json.dumps({
        "type": "fleet_registered", "request_id": request_id,
        "node_id": node_id, "node_key": result.get("node_key", ""),
        "capabilities": result.get("capabilities", []),
        "warning": "Store node_secret securely. It will not be shown again.",
    }))
    _audit(identity, "fleet_register", node_id, "success",
           {"capabilities": result.get("capabilities", [])}, ip=ip)
    return None


async def _handle_fleet_auth(ws, cmd, request_id, identity, ip):
    """Fleet node authenticates with its secret to get a machine token."""
    node_id = cmd.get("node_id", "").strip()
    node_secret = cmd.get("node_secret", "").strip()
    ttl = min(cmd.get("ttl_sec", 3600), 86400)  # Max 24h

    result = issue_machine_token(node_id, node_secret, ttl_sec=ttl)
    if "error" in result:
        _audit(identity or node_id, "fleet_auth", node_id, "failure",
               {"reason": result["error"]}, ip=ip)
        return {"type": "auth_failed", "request_id": request_id,
                "reason": result["error"]}

    await ws.send_str(json.dumps({
        "type": "fleet_auth_success", "request_id": request_id,
        "machine_token": result["token"],
        "expires": result["expires"],
        "capabilities": result["capabilities"],
    }))
    _audit(identity or node_id, "fleet_auth", node_id, "success",
           {"expires": result["expires"]}, ip=ip)
    return None


async def _handle_fleet_exchange(ws, cmd, request_id, identity, ip):
    """
    Exchange a fleet machine_token for a VDC capability_token.
    This is the CRITICAL gateway: only node-i (fleet-router) should typically
    exchange tokens, but any authenticated fleet node can do so for its own
    capabilities.
    """
    machine_token = cmd.get("machine_token", "").strip()
    project_id = cmd.get("project", "default")

    # Verify machine token
    mtok = verify_machine_token(machine_token)
    if not mtok["valid"]:
        _audit(identity, "fleet_exchange", project_id, "failure",
               {"reason": "invalid_machine_token"}, ip=ip)
        return {"type": "auth_failed", "request_id": request_id,
                "reason": "Invalid or expired machine token."}

    node_id = mtok["node_id"]
    node_caps = mtok["capabilities"]

    # Issue VDC capability token via AuthFacade
    # Fleet nodes don't have behavioral profiles, so we pass empty
    session = AuthFacade.authenticate(project_id, behavioral_profile={}, capabilities=node_caps)

    await ws.send_str(json.dumps({
        "type": "fleet_exchange_success", "request_id": request_id,
        "node_id": node_id,
        "vdc_token": session["token"],
        "capabilities": session["capabilities"],
        "expires": session["expires"],
    }))
    _audit(node_id, "fleet_exchange", project_id, "success",
           {"vdc_session": session.get("session_id", "")}, ip=ip)
    return None


async def _handle_fleet_status(ws, cmd, request_id, identity, ip):
    """Get fleet registration status."""
    from fleet_identity import FLEET_REGISTRY
    from vdc_core import read_json
    registry = read_json(FLEET_REGISTRY) if FLEET_REGISTRY.exists() else {"nodes": {}}
    nodes = {}
    for nid, info in registry.get("nodes", {}).items():
        nodes[nid] = {
            "role": info.get("role", ""),
            "status": info.get("status", "unknown"),
            "registered_at": info.get("registered_at", ""),
            "capabilities": info.get("capabilities", []),
        }
    await ws.send_str(json.dumps({
        "type": "fleet_status", "request_id": request_id,
        "nodes": nodes, "fleet_auth_enabled": FLEET_AUTH_ENABLED,
    }))
    return None


COMMAND_HANDLERS = {
    "query": _handle_query,
    "rfi": _handle_rfi,
    "scan": _handle_scan,
    "ingest": _handle_ingest,
    "list_projects": _handle_list_projects,
    "create_project": _handle_create_project,
    "fleet_register": _handle_fleet_register,
    "fleet_auth": _handle_fleet_auth,
    "fleet_exchange": _handle_fleet_exchange,
    "fleet_status": _handle_fleet_status,
}


# ── Auth Flow (Human Users) ──────────────────────────────────────────────────
async def _handle_auth_challenge(ws, cmd, request_id, ip):
    challenge = AuthFacade.challenge(cmd.get("project", "default"), cmd.get("difficulty", "medium"))
    await ws.send_str(json.dumps({"type": "auth_challenge", "request_id": request_id, **challenge}))
    _audit("anonymous", "auth_challenge", cmd.get("project", "default"), "issued", ip=ip)


async def _handle_auth_answer(ws, cmd, request_id, ip):
    result = AuthFacade.answer(cmd.get("challenge_id", ""), cmd.get("answer", ""))
    if result.get("valid"):
        profile = cmd.get("behavioral_profile", {})
        session = AuthFacade.authenticate(result["project_id"], profile)
        UNAUTH.discard(ws)
        CLIENTS.add((ws, session["session_id"], "human"))
        await ws.send_str(json.dumps({
            "type": "auth_success", "request_id": request_id,
            "token": session["token"], "capabilities": session["capabilities"],
            "expires": session["expires"],
            "message": "Authenticated via knowledge proof. Welcome to the agent mesh.",
        }))
        _audit("human", "auth_answer", result["project_id"], "success",
               {"session_id": session["session_id"]}, token=session["token"], ip=ip)
    else:
        await ws.send_str(json.dumps({
            "type": "auth_failed", "request_id": request_id,
            "reason": result.get("reason", "Incorrect answer."),
        }))
        _audit("anonymous", "auth_answer", cmd.get("project", "default"), "failure",
               {"reason": result.get("reason", "")}, ip=ip)


# ── Command Router ───────────────────────────────────────────────────────────
async def handle_command(ws, cmd: dict, peer_ip: str = ""):
    action = cmd.get("action")
    request_id = cmd.get("request_id", "")
    project = cmd.get("project", "default")

    # Auth-phase commands (no token needed, but rate-limited)
    if action == "auth_challenge":
        rl = _check_rate(peer_ip, "auth_challenge", peer_ip)
        if not rl["allowed"]:
            await ws.send_str(json.dumps({"type": "rate_limited", "request_id": request_id, **rl}))
            return
        return await _handle_auth_challenge(ws, cmd, request_id, peer_ip)

    if action == "auth_answer":
        rl = _check_rate(peer_ip, "auth_answer", peer_ip)
        if not rl["allowed"]:
            await ws.send_str(json.dumps({"type": "rate_limited", "request_id": request_id, **rl}))
            return
        return await _handle_auth_answer(ws, cmd, request_id, peer_ip)

    # Fleet commands (machine identity)
    if action in ("fleet_register", "fleet_auth", "fleet_exchange", "fleet_status"):
        rl = _check_rate(peer_ip, action, peer_ip)
        if not rl["allowed"]:
            await ws.send_str(json.dumps({"type": "rate_limited", "request_id": request_id, **rl}))
            return
        handler = COMMAND_HANDLERS.get(action)
        if handler:
            error = await handler(ws, cmd, request_id, "fleet", peer_ip)
            if error:
                await ws.send_str(json.dumps(error))
        return

    # All other commands require authorization + sanitization + rate limiting
    token = cmd.get("token", "")
    profile = cmd.get("behavioral_profile", {})
    required_cap = CAPABILITY_MAP.get(action)

    # Step 1: Sanitize input
    try:
        cmd = _sanitize(cmd)
    except ValidationError as ve:
        await ws.send_str(json.dumps({
            "type": "validation_error", "request_id": request_id,
            "field": ve.field, "reason": ve.reason,
        }))
        _audit("unknown", action, project, "validation_error",
               {"field": ve.field, "reason": ve.reason}, ip=peer_ip)
        return

    # Step 2: Authorize
    if required_cap:
        auth = AuthFacade.authorize(token, required_cap, profile)
        if not auth["authorized"]:
            await ws.send_str(json.dumps({
                "type": "auth_required", "request_id": request_id,
                "reason": auth.get("reason", "Unauthorized."),
                "rechallenge": auth.get("rechallenge", False),
            }))
            _audit("unknown", action, project, "auth_denied",
                   {"reason": auth.get("reason", "")}, token=token, ip=peer_ip)
            return
        identity = auth.get("session_id", "unknown")
        capabilities = auth.get("capabilities", [])
    else:
        identity = "anonymous"
        capabilities = []

    # Step 3: Rate limit
    rl = _check_rate(identity, required_cap or action, peer_ip)
    if not rl["allowed"]:
        await ws.send_str(json.dumps({"type": "rate_limited", "request_id": request_id, **rl}))
        return

    # Step 4: Execute via pluggable handler (async handler, sync workflow in thread pool)
    handler = COMMAND_HANDLERS.get(action)
    if handler:
        try:
            error = await handler(ws, cmd, request_id, project, identity, peer_ip)
            if error:
                await ws.send_str(json.dumps(error))
                _audit(identity, action, project, "handler_error", {"error": error}, token=token, ip=peer_ip)
        except Exception as e:
            traceback.print_exc()
            await ws.send_str(json.dumps({
                "type": "error", "request_id": request_id,
                "error": f"Internal error: {str(e)}",
            }))
            _audit(identity, action, project, "exception",
                   {"error": str(e)}, token=token, ip=peer_ip)
    else:
        await ws.send_str(json.dumps({
            "type": "error", "request_id": request_id,
            "error": f"Unknown action: {action}",
        }))
        _audit(identity, action, project, "unknown_action", ip=peer_ip)


# ── WebSocket Handler ────────────────────────────────────────────────────────
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    peer_ip = request.remote or "unknown"
    UNAUTH.add(ws)
    print(f"[bridge] Client connected from {peer_ip}. Auth:{len(CLIENTS)} Unauth:{len(UNAUTH)}")

    await ws.send_str(json.dumps({
        "type": "auth_required",
        "message": "Medha Authentication Mesh: Prove project knowledge to access the fleet.",
        "instructions": "Send auth_challenge → receive question → auth_answer with response.",
        "fleet_auth": "Send fleet_auth with node_id + node_secret for machine identity.",
    }))

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            try:
                data = json.loads(msg.data)
                await handle_command(ws, data, peer_ip)
            except json.JSONDecodeError:
                await ws.send_str(json.dumps({"type": "error", "error": "Invalid JSON"}))
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print(f"[bridge] WS error from {peer_ip}: {ws.exception()}")

    UNAUTH.discard(ws)
    for entry in list(CLIENTS):
        if entry[0] == ws:
            CLIENTS.discard(entry)
            break
    print(f"[bridge] Client from {peer_ip} disconnected. Auth:{len(CLIENTS)} Unauth:{len(UNAUTH)}")
    return ws


# ── HTTP Handlers ────────────────────────────────────────────────────────────
async def inbox_upload(request):
    peer_ip = request.remote or "unknown"
    reader = await request.multipart()
    files_saved = []

    async for part in reader:
        if part.filename:
            try:
                sanitize_inbox_upload(part.filename, 0)
            except ValidationError as ve:
                _audit("anonymous", "inbox_upload", part.filename, "validation_error",
                       {"field": ve.field, "reason": ve.reason}, ip=peer_ip)
                return web.json_response({"error": ve.reason}, status=400)

            target = INBOX_DIR / part.filename
            if target.exists():
                target = INBOX_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{part.filename}"
            with open(target, 'wb') as f:
                while True:
                    chunk = await part.read_chunk()
                    if not chunk:
                        break
                    f.write(chunk)
            files_saved.append({"name": part.filename, "path": str(target)})
            append_event("tasks", {"type": "inbox_uploaded", "filename": part.filename,
                                    "size_bytes": target.stat().st_size})

    # NOTE: Ingestion is handled by inbox_watcher daemon.
    # The bridge only deposits files into inbox/ to ensure single-source-of-truth.
    # This prevents duplicate ingestion (previously: bridge + watcher both ingested).

    _audit("anonymous", "inbox_upload", "default", "success",
           {"files": [f["name"] for f in files_saved]}, ip=peer_ip)
    return web.json_response({"files": files_saved, "message": "Files uploaded. Agents will process them."})


async def health(request):
    peer_ip = request.remote or "unknown"
    # Verify audit integrity on health check (lightweight)
    from enterprise_audit import verify_audit_integrity
    audit_status = verify_audit_integrity()
    return web.json_response({
        "status": "ok",
        "mode": "agent-driven",
        "auth": "agentic-3factor-mesh",
        "fleet_auth": FLEET_AUTH_ENABLED,
        "apis": "none",
        "auth_clients": len(CLIENTS),
        "unauth_clients": len(UNAUTH),
        "audit_integrity": audit_status,
        "model_ready": is_model_ready(),
        "timestamp": datetime.now().isoformat(),
    })


async def audit_query(request):
    """Query audit trail (admin capability required)."""
    peer_ip = request.remote or "unknown"
    # Simple auth check via header token
    token = request.headers.get("X-VDC-Token", "")
    auth = AuthFacade.authorize(token, "can_manage_projects")
    if not auth["authorized"]:
        return web.json_response({"error": "Unauthorized"}, status=403)

    from enterprise_audit import query_audit
    params = request.query
    results = query_audit(
        actor=params.get("actor"),
        action=params.get("action"),
        resource=params.get("resource"),
        since=params.get("since"),
        limit=min(int(params.get("limit", 100)), 1000),
    )
    _audit(auth.get("session_id", "unknown"), "audit_query", "*", "success",
           {"count": len(results)}, token=token, ip=peer_ip)
    return web.json_response({"events": results, "count": len(results)})


# ── App Factory ──────────────────────────────────────────────────────────────
def create_app():
    app = web.Application(client_max_size=100 * 1024 * 1024)
    app.router.add_get('/ws', websocket_handler)
    app.router.add_post('/inbox', inbox_upload)
    app.router.add_get('/health', health)
    app.router.add_get('/audit', audit_query)
    return app


async def main():
    # Preload embedding model BEFORE accepting connections to avoid
    # query-time blocking that causes WebSocket timeouts.
    # This runs sync in the main thread; the model loads once and is
    # shared across all thread-pool workflow executions.
    preload_model()

    app = create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, BRIDGE_HOST, BRIDGE_PORT).start()
    print(f"[bridge] Medha Agent Bridge + Auth Mesh on http://{BRIDGE_HOST}:{BRIDGE_PORT}")
    print(f"[bridge] Auth: 3-Factor Agentic (Knowledge + Behavioral + Agent Attestation)")
    print(f"[bridge] Fleet Auth: {'ENABLED' if FLEET_AUTH_ENABLED else 'DISABLED'}")
    print(f"[bridge] Enterprise: RateLimit + InputSanitization + AuditTrail")
    asyncio.create_task(watch_shared_memory())
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
