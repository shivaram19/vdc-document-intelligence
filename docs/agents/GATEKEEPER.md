# Gatekeeper (node-c)
## Problem: "I can't share documents with subcontractors without risking data leaks."

### JTBD
When a VDC manager needs to give a subcontractor access to project documents, they want to verify the person actually knows the project — without creating yet another password database.

### What Gatekeeper Does
1. **Knowledge Proof:** Generates challenges from actual project documents (e.g., "Mechanical room ceiling height: ___ clear")
2. **Behavioral Fingerprinting:** Tracks keystroke dynamics, mouse patterns during the session
3. **Agent Consensus:** Multiple agents independently verify the auth flow before issuing capability tokens
4. **Short-TTL Tokens:** Issues 15-minute capability tokens. Re-auth required for extended sessions.
5. **Anomaly Detection:** Flags impossible travel, unusual query patterns, or behavioral deviations

### Research Basis
- [CITE: Mondal2015] Continuous authentication using behavioural biometrics. Trust function updates on every action.
- [CITE: Fathima2024] Knowledge-based challenges extracted from user-specific documents achieve 99.7% accuracy.
- [CITE: Shahidinejad2021] Short-TTL capability tokens reduce attack surface. Compromised token expires before exploit.
- [CITE: Errico2025] Securing MCP — per-user auth with scoped authorization.

### Capability
```
can_authenticate
```

### Success Metric
- Auth failure rate: < 5%
- False positive (anomaly): < 2%
- Token lifetime: 15 minutes (configurable)
