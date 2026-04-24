#!/usr/bin/env python3
"""
fleet_bootstrap.py — CLI for Registering Fleet Nodes

Usage:
    python fleet_bootstrap.py register node-a    # Register a single node
    python fleet_bootstrap.py register-all       # Register all 10 nodes
    python fleet_bootstrap.py status             # Show registration status
    python fleet_bootstrap.py secrets            # Show all secrets (admin only)

Security: Secrets are shown ONCE at registration. Store them securely.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fleet_identity import register_fleet_node, FLEET_REGISTRY, read_json


def cmd_register(node_id: str, role: str = ""):
    result = register_fleet_node(node_id, role=role)
    print(f"✅ Registered: {result['node_id']}")
    print(f"   Role: {role or node_id}")
    print(f"   Capabilities: {', '.join(result['capabilities'])}")
    print(f"   Node Key: {result['node_key']}")
    print(f"   ⚠️  NODE SECRET (store securely): {result['node_secret']}")
    print(f"   🔒 This secret will NOT be shown again.")
    return result


def cmd_register_all():
    roles = {
        "node-a": "curiosity-brain",
        "node-b": "executor-builder",
        "node-c": "memory-guardian",
        "node-d": "safety-auditor",
        "node-e": "document-parser",
        "node-f": "contradiction-detector",
        "node-g": "rfi-drafter",
        "node-h": "knowledge-graph",
        "node-i": "fleet-router",
        "node-j": "metrics-collector",
    }
    secrets = {}
    for node_id, role in roles.items():
        result = cmd_register(node_id, role)
        secrets[node_id] = result["node_secret"]
        print()
    
    # Save secrets to a file for distribution (in production, use a vault)
    secrets_file = Path(__file__).parent.parent / "shared" / "state" / ".fleet-secrets.json"
    secrets_file.parent.mkdir(parents=True, exist_ok=True)
    with open(secrets_file, "w") as f:
        json.dump(secrets, f, indent=2)
    print(f"🔐 Secrets saved to: {secrets_file}")
    print("   ⚠️  Restrict access to this file: chmod 600")


def cmd_status():
    registry = read_json(FLEET_REGISTRY) if FLEET_REGISTRY.exists() else {"nodes": {}}
    print("Fleet Registration Status")
    print("=" * 50)
    for node_id, info in sorted(registry.get("nodes", {}).items()):
        print(f"  {node_id}: {info.get('status', 'unknown')} "
              f"(role={info.get('role', '?')}, "
              f"caps={len(info.get('capabilities', []))})")
    print(f"\nTotal registered: {len(registry.get('nodes', {}))}")


def cmd_secrets():
    secrets_file = Path(__file__).parent.parent / "shared" / "state" / ".fleet-secrets.json"
    if not secrets_file.exists():
        print("No secrets file found. Run 'register-all' first.")
        return
    with open(secrets_file) as f:
        secrets = json.load(f)
    print("Fleet Node Secrets (ADMIN ONLY)")
    print("=" * 50)
    for node_id, secret in sorted(secrets.items()):
        print(f"  {node_id}: {secret}")


def main():
    parser = argparse.ArgumentParser(description="Fleet Node Bootstrap")
    sub = parser.add_subparsers(dest="command")
    
    reg = sub.add_parser("register", help="Register a single node")
    reg.add_argument("node_id", help="Node ID (e.g., node-a)")
    reg.add_argument("--role", default="", help="Node role")
    
    sub.add_parser("register-all", help="Register all 10 fleet nodes")
    sub.add_parser("status", help="Show registration status")
    sub.add_parser("secrets", help="Show secrets (admin)")
    
    args = parser.parse_args()
    
    if args.command == "register":
        cmd_register(args.node_id, args.role)
    elif args.command == "register-all":
        cmd_register_all()
    elif args.command == "status":
        cmd_status()
    elif args.command == "secrets":
        cmd_secrets()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
