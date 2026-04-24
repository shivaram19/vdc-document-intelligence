"""
baseline_tracker.py — Behavioral Baseline Manager

SINGLE RESPONSIBILITY: Maintain and update per-user behavioral baselines
using exponential moving average. No anomaly scoring, no session logic.

Research basis: Fathima & Saravanan (2024) — trust score computation via
EMA of behavioral attributes over N sessions.
"""

import json
from pathlib import Path

AUTH_DIR = Path(__file__).parent.parent.parent / "shared" / "project" / "vdc" / "auth"


class BaselineTracker:
    def __init__(self):
        self.path = AUTH_DIR / "registry.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> dict:
        if self.path.exists():
            return json.loads(self.path.read_text())
        return {"baselines": {}}

    def _save(self, data: dict):
        self.path.write_text(json.dumps(data, indent=2, default=str))

    def get(self, behavioral_hash: str) -> dict:
        return self._load().get("baselines", {}).get(behavioral_hash, {})

    def update(self, behavioral_hash: str, profile: dict, alpha: float = 0.3):
        data = self._load()
        baselines = data.setdefault("baselines", {})
        old = baselines.get(behavioral_hash, {})
        new = {}
        for key in set(old.keys()) | set(profile.keys()):
            if key in old and key in profile:
                try:
                    new[key] = round(old[key] * (1 - alpha) + profile[key] * alpha, 3)
                except (TypeError, ValueError):
                    new[key] = profile[key]
            elif key in profile:
                new[key] = profile[key]
            else:
                new[key] = old[key]
        baselines[behavioral_hash] = new
        self._save(data)

    def delete(self, behavioral_hash: str):
        data = self._load()
        data.get("baselines", {}).pop(behavioral_hash, None)
        self._save(data)
