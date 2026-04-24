#!/usr/bin/env python3
"""
fleet_identity.py — Machine-to-Machine Authentication for PicoCloth Fleet Nodes

Enterprise Principle: Fleet nodes are first-class identities, not anonymous
processes. Each node must prove its identity before accessing VDC resources.

Research basis: Shahidinejad et al. (2021) "Light-edge" — machine identities
use short-lived certificates/tokens instead of passwords. NIST SP 800-207
(Zero Trust) requires every device to authenticate, regardless of network
location.
"""

import hashlib
import hmac
import json
import os
import secrets
import time
from datetime import datetime, timedelta
from pathlib import Path

from vdc_core import write_json, read_json

FLEET_IDENTITIES = Path(__file__).parent.parent / "shared" / "state" / "fleet-identities.json"
FLEET_REGISTRY = Path(__file__).parent.parent / "shared" / "state" / "fleet-registry.json"

# Node roles and their default capabilities
NODE_CAPABILITIES = {
    "node-a": ["can_query", "can_upload", "can_draft_rfi", "can_scan_contradictions"],
    "node-b": ["can_query", "can_upload"],
    "node-c": ["can_query"],
    "node-d": ["can_query", "can_scan_contradictions"],
    "node-e": ["can_query", "can_upload"],
    "node-f": ["can_query", "can_scan_contradictions"],
    "node-g": ["can_query", "can_draft_rfi"],
    "node-h": ["can_query"],
    "node-i": ["can_query", "can_upload", "can_draft_rfi", "can_scan_contradictions", "can_manage_projects"],
    "node-j": ["can_query"],
}


_MASTER_SECRET: str | None = None


def _get_master_secret() -> str:
    """Derive deterministic fleet master secret from deployment state.

    In production: read FLEET_MASTER_SECRET from environment or secure vault.
    Falls back to a stable secret derived from the vdc state file + deployment path.
    """
    global _MASTER_SECRET
    if _MASTER_SECRET is not None:
        return _MASTER_SECRET

    env_secret = os.environ.get("FLEET_MASTER_SECRET", "").strip()
    if not env_secret:
        # Deterministic fallback: hash of deployment path + state file
        deploy_path = Path(__file__).parent.parent.resolve()
        state_path = deploy_path / "shared" / "project" / "vdc" / "state.json"
        base = hashlib.sha256(str(deploy_path).encode()).hexdigest()[:32]
        if state_path.exists():
            base += hashlib.sha256(state_path.read_bytes()).hexdigest()[:32]
        env_secret = base

    _MASTER_SECRET = hashlib.sha256(env_secret.encode()).hexdigest()
    return _MASTER_SECRET


def register_fleet_node(node_id: str, role: str = "") -> dict:
    """Register a fleet node and issue it a machine identity token."""
    registry = read_json(FLEET_REGISTRY) if FLEET_REGISTRY.exists() else {"nodes": {}}

    node_secret = secrets.token_hex(32)
    node_key = hashlib.sha256(f"{_get_master_secret()}:{node_id}".encode()).hexdigest()[:32]

    registry["nodes"][node_id] = {
        "role": role or node_id,
        "registered_at": datetime.utcnow().isoformat() + "Z",
        "secret_hash": hashlib.sha256(node_secret.encode()).hexdigest()[:16],
        "status": "active",
        "capabilities": NODE_CAPABILITIES.get(node_id, ["can_query"]),
    }
    write_json(FLEET_REGISTRY, registry)

    return {
        "node_id": node_id,
        "node_secret": node_secret,
        "node_key": node_key,
        "capabilities": registry["nodes"][node_id]["capabilities"],
    }


def issue_machine_token(node_id: str, node_secret: str, ttl_sec: int = 3600) -> dict:
    """Issue a short-lived machine token for a fleet node."""
    registry = read_json(FLEET_REGISTRY) if FLEET_REGISTRY.exists() else {"nodes": {}}
    node_info = registry.get("nodes", {}).get(node_id)

    if not node_info:
        return {"error": "Node not registered"}

    expected_hash = node_info.get("secret_hash")
    provided_hash = hashlib.sha256(node_secret.encode()).hexdigest()[:16]
    if not secrets.compare_digest(expected_hash, provided_hash):
        return {"error": "Invalid node secret"}

    expiry = int(time.time()) + ttl_sec
    payload = f"{node_id}:{','.join(node_info['capabilities'])}:{expiry}"
    sig = hmac.new(_get_master_secret().encode(), payload.encode(), hashlib.sha256).hexdigest()[:32]
    token = f"{payload}:{sig}"

    return {
        "token": token,
        "expires": datetime.utcfromtimestamp(expiry).isoformat() + "Z",
        "capabilities": node_info["capabilities"],
    }


def verify_machine_token(token: str) -> dict:
    """Verify a fleet machine token."""
    result = {"valid": False, "node_id": "", "capabilities": []}
    try:
        parts = token.split(":")
        if len(parts) != 4:
            return result
        node_id, caps_str, expiry_str, provided_sig = parts
        payload = f"{node_id}:{caps_str}:{expiry_str}"
        expected_sig = hmac.new(_get_master_secret().encode(), payload.encode(), hashlib.sha256).hexdigest()[:32]
        if not secrets.compare_digest(provided_sig, expected_sig):
            return result
        if time.time() > int(expiry_str):
            return result
        result.update({
            "valid": True,
            "node_id": node_id,
            "capabilities": [c for c in caps_str.split(",") if c],
        })
    except Exception:
        pass
    return result
