#!/usr/bin/env python3
"""
rate_limiter.py — Token Bucket Rate Limiting for Fleet Nodes & Clients

Research basis: Shahidinejad et al. (2021) "Short-TTL capability tokens"
— rate limiting is essential companion to short-lived tokens. Exabeam 2026
Zero Trust guide: "Require token-based authentication, implement call rate
limits, and log all inter-service communications."

Design:
  - Token bucket per identity (node_id or session_id)
  - Separate buckets per capability
  - Burst allowance for interactive use
  - Automatic cleanup of stale buckets
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from threading import Lock
from typing import Dict, Optional


@dataclass
class Bucket:
    """Token bucket state."""
    tokens: float
    last_update: float
    capacity: int
    rate: float  # tokens per second


class RateLimiter:
    """
    Token bucket rate limiter with per-identity, per-capability granularity.

    Default limits (enterprise-grade):
      - Sustained: 100 req/min = 1.67 req/sec
      - Burst: 20 requests
    """

    def __init__(self, default_rate: float = 1.67, default_burst: int = 20):
        self.default_rate = default_rate
        self.default_burst = default_burst
        self.buckets: Dict[str, Bucket] = {}
        self.lock = Lock()
        self.last_cleanup = time.time()

    def _key(self, identity: str, capability: Optional[str] = None) -> str:
        return f"{identity}:{capability or 'global'}"

    def _get_or_create(self, key: str, rate: Optional[float] = None,
                       burst: Optional[int] = None) -> Bucket:
        now = time.time()
        if key not in self.buckets:
            cap = burst if burst is not None else self.default_burst
            r = rate if rate is not None else self.default_rate
            self.buckets[key] = Bucket(tokens=float(cap), last_update=now, capacity=cap, rate=r)
        return self.buckets[key]

    def _refill(self, bucket: Bucket) -> None:
        now = time.time()
        elapsed = now - bucket.last_update
        bucket.tokens = min(bucket.capacity, bucket.tokens + elapsed * bucket.rate)
        bucket.last_update = now

    def check(self, identity: str, capability: Optional[str] = None,
              rate: Optional[float] = None, burst: Optional[int] = None) -> dict:
        """
        Check if request is allowed. Returns dict with allowed=True/False and metadata.
        If allowed, consumes one token.
        """
        key = self._key(identity, capability)
        with self.lock:
            self._maybe_cleanup()
            bucket = self._get_or_create(key, rate, burst)
            self._refill(bucket)

            if bucket.tokens >= 1.0:
                bucket.tokens -= 1.0
                return {
                    "allowed": True,
                    "remaining": int(bucket.tokens),
                    "reset_after_sec": round((1.0 - bucket.tokens) / bucket.rate, 2) if bucket.rate > 0 else 0,
                }
            else:
                wait_time = (1.0 - bucket.tokens) / bucket.rate if bucket.rate > 0 else 60
                return {
                    "allowed": False,
                    "remaining": 0,
                    "retry_after_sec": round(wait_time, 2),
                    "reason": f"Rate limit exceeded. Retry after {round(wait_time, 1)}s",
                }

    def _maybe_cleanup(self):
        """Remove stale buckets every 5 minutes."""
        now = time.time()
        if now - self.last_cleanup > 300:
            stale_threshold = now - 3600  # 1 hour idle
            stale_keys = [k for k, b in self.buckets.items() if b.last_update < stale_threshold]
            for k in stale_keys:
                del self.buckets[k]
            self.last_cleanup = now

    def get_status(self, identity: str, capability: Optional[str] = None) -> dict:
        """Get current bucket status without consuming."""
        key = self._key(identity, capability)
        with self.lock:
            if key not in self.buckets:
                return {"tokens": self.default_burst, "capacity": self.default_burst}
            bucket = self.buckets[key]
            self._refill(bucket)
            return {
                "tokens": round(bucket.tokens, 2),
                "capacity": bucket.capacity,
                "rate_per_sec": round(bucket.rate, 2),
            }

    def reset(self, identity: str, capability: Optional[str] = None):
        """Reset bucket for an identity (e.g., after auth refresh)."""
        key = self._key(identity, capability)
        with self.lock:
            if key in self.buckets:
                del self.buckets[key]


# Singleton instance for the bridge
_limiter = RateLimiter()


def check_rate_limit(identity: str, capability: Optional[str] = None,
                     rate: Optional[float] = None, burst: Optional[int] = None) -> dict:
    """Module-level convenience function."""
    return _limiter.check(identity, capability, rate, burst)


def get_rate_status(identity: str, capability: Optional[str] = None) -> dict:
    """Module-level convenience function."""
    return _limiter.get_status(identity, capability)
