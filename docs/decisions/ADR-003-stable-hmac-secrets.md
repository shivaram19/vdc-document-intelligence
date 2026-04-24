# ADR-003: Stable HMAC Secret Derivation

## Status
Accepted — implemented 2026-04-24

## Context
The HMAC secret for capability tokens was derived from `hashlib.sha256(state.json).hexdigest()`. Every write to `state.json` (e.g., creating a project, ingesting a document) changed the secret and invalidated all active sessions/tokens.

## Decision
Derive the HMAC secret from:
1. `AGENT_AUTH_SECRET` environment variable (required — fails startup if missing)
2. A stable per-machine secret stored in `shared/.machine-secret` (created once, chmod 600)

`state.json` is completely removed from the secret derivation chain.

## Consequences
- **Positive**: Tokens survive state mutations. Users stay logged in across project creation.
- **Positive**: Explicit failure on missing env var prevents accidental default-secret deployment.
- **Negative**: Machine secret file must be backed up; losing it invalidates all tokens (same as losing any HSM key).

## Research Basis
- [RFC2104] HMAC: Keyed-Hashing for Message Authentication — keys must be stable for the lifetime of the token.
- [NIST800-132] Recommendation for Password-Based Key Derivation — derivation inputs must be entropy sources, not mutable state.
- [Shahidinejad2021] Short-TTL capability tokens reduce attack surface, but token invalidation should be explicit (revocation), not implicit (state change).
- [GitGuardian2026] "HMAC Secrets Explained", https://blog.gitguardian.com/hmac-secrets-explained-authentication/ — Generate strong keys (min 32 bytes) with CSPRNG. Never commit secrets. Include timestamp in signed payload. Use constant-time comparison.
- [WhoisArjen2026] "HMAC Timestamp Tokens: Zero-Trust Communication", https://whoisarjen.com/blog/hmac-timestamp-tokens-zero-trust-service-communication — "Rotation is an environment variable change, not a migration. No database updates, no token invalidation, no coordination beyond deploying the new secret."
- [S4E2025] "The Fragile Trust Behind JWTs", https://resources.s4e.io/blog/the-fragile-trust-behind-jwts-understanding-exploits-and-defenses/ — Keep signing secrets out of code and config files. Use secrets manager. Rotate on schedule. Support multiple active keys during transitions.

## Alternatives Considered
1. **Keep state-derived, accept token churn** — rejected: destroys UX; every project creation logs everyone out.
2. **Use JWT with asymmetric keys** — rejected: adds cryptography complexity; symmetric HMAC is sufficient for single-tenant deployments.
3. **Store secret in systemd creds / Docker secrets** — accepted as future enhancement; env var + file is the minimal viable approach.

## Code Location
- `picocloth/agents/auth/crypto_utils.py:_get_agent_secret()`
- `picocloth/agents/auth/crypto_utils.py:_ensure_machine_secret()`
