# Scribe (node-d)
## Problem: "The auditor asked for proof we checked everything. We have nothing."

### JTBD
When a project faces a claims dispute or compliance audit, the PM needs a tamper-evident record of every document review, query, and contradiction check.

### What Scribe Does
1. Receives every auth event, query, ingest, and scan from the fleet
2. Appends to a SHA-256 chained JSONL audit log
3. Each entry includes: timestamp, identity, action, result, previous hash
4. Verifies chain integrity on `/health` endpoint
5. Makes undetected deletion/modification cryptographically impossible

### Research Basis
- [CITE: NIST800-207] Zero Trust Architecture requires continuous audit and verification.
- [CITE: RedHat2026] Zero Trust for agentic AI — tamper-evident audit trails are non-negotiable.
- [CITE: PaloAltoAuditor] "Poor document management prevents defending against claims."

### Capability
```
can_audit
```

### Success Metric
- Chain verification: < 50ms
- Events logged: 100% of auth + query + scan + ingest
- Tamper detection: Cryptographically guaranteed

### Audit Chain Example
```json
{
  "ts": "2026-04-24T21:30:00Z",
  "identity": "human_sess_a1b2",
  "action": "query",
  "project": "default",
  "result": "success",
  "prev_hash": "a3f7...",
  "hash": "c8d2..."
}
```
