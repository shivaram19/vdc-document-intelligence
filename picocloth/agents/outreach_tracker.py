#!/usr/bin/env python3
"""
outreach_tracker.py — Outreach Pipeline State Tracker

SRP: ONLY tracks pipeline state. No drafting, no sending.
DIP: Reads/writes to shared memory — any agent can observe.

RESEARCH BASIS:
- [CITE: SaaSFactor2025] SaaSFactor (2025). TTFV under 10 min correlates with 29% churn drop. https://www.saasfactor.co/blogs/saas-customer-onboarding
  → We track identified→contacted→demo→pilot→customer conversion.
- [CITE: Reforge2025] Companies that run weekly onboarding experiments
  improve activation 5-10% per quarter.
  → Weekly pipeline review = continuous optimization.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent))
from vdc_core import read_state, write_state, SHARED_DIR

OUTREACH_STATE_FILE = SHARED_DIR / "project" / "vdc" / "outreach_state.json"


def load_state() -> dict:
    if OUTREACH_STATE_FILE.exists():
        try:
            with open(OUTREACH_STATE_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {"targets": {}, "history": [], "last_updated": None}


def save_state(state: dict):
    state["last_updated"] = datetime.now(timezone.utc).isoformat()
    OUTREACH_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTREACH_STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def update_target(target_name: str, stage: str, notes: str = ""):
    """Update a target's pipeline stage."""
    state = load_state()
    old_stage = state["targets"].get(target_name, {}).get("stage", "unknown")
    state["targets"][target_name] = {
        "stage": stage,
        "notes": notes,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    state["history"].append({
        "target": target_name,
        "from_stage": old_stage,
        "to_stage": stage,
        "notes": notes,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    save_state(state)
    return state


def get_pipeline_metrics() -> dict:
    """Compute funnel metrics."""
    state = load_state()
    stages = ["identified", "contacted", "demo", "pilot", "customer"]
    counts = {s: 0 for s in stages}
    for t in state["targets"].values():
        s = t.get("stage", "identified")
        if s in counts:
            counts[s] += 1

    # Conversion rates
    conversions = {}
    for i, s in enumerate(stages[:-1]):
        next_s = stages[i + 1]
        conversions[f"{s}_to_{next_s}"] = round(counts[next_s] / max(counts[s], 1), 2)

    return {
        "total_tracked": len(state["targets"]),
        "stage_counts": counts,
        "conversions": conversions,
        "history_last_7d": [
            h for h in state.get("history", [])
            if (datetime.now(timezone.utc) - datetime.fromisoformat(h["timestamp"].replace("Z", "+00:00"))).days <= 7
        ],
    }


def get_target_history(target_name: str) -> list:
    state = load_state()
    return [h for h in state.get("history", []) if h["target"] == target_name]


if __name__ == "__main__":
    # Demo: update Turner to "contacted"
    update_target("Turner Construction", "contacted", "LinkedIn connection sent to Gary Chapman")
    print(json.dumps(get_pipeline_metrics(), indent=2))
