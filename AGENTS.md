# Agent Operating Guidelines — Medha VDC Document Intelligence

## Mandatory: Research-Backed Code

Every line of code must have a cited reason. Every architectural decision must have an ADR in `docs/decisions/`.

### Citation Format (inline)
```python
# [CITE: AuthorYear] One-sentence reason from the source
# [CITE: RFCXXXX] Standard requirement
# [CITE: NIST-SP-800-XXX] Security control
```

### When No Paper Exists
Document the trade-off in an ADR with:
- Context (what problem)
- Decision (what chosen)
- Consequences (positive + negative)
- Alternatives rejected (with why)

### Research Sources (hierarchy)
1. Peer-reviewed paper (IEEE, ACM, arXiv with citations)
2. Industry standard (ISO, NIST, RFC, OWASP)
3. Primary source (official docs, source code, man pages)
4. Documented decision (ADR with clear reasoning)

## File System Rules
- Single responsibility per file (max ~5KB for docs, max ~200 lines for Python)
- `docs/research/` — all citations, search logs, paper summaries
- `docs/decisions/` — ADRs numbered sequentially
- `docs/citations/` — BibTeX or Markdown bibliographies
- Code comments must cite; ADRs must reference URLs or DOIs

## Current Research Corpus
- [Fathima2024] BIM adoption barriers in developing economies
- [Papaioannou2023] LLM hallucination in construction documents
- [Mondal2015] Keystroke dynamics for behavioral biometrics
- [Ejiofor2025] Construction rework costs from document errors
- [Li2024] RAG pipeline optimization for technical documents
- [YangSmith2026] Agent consensus protocols for secure systems
- [AIP2026] Agent Identity Protocol — delegated token exchange
- [RedHat2026] Zero Trust for agentic AI
- [Errico2025] Securing MCP servers with per-user auth
- [Shahidinejad2021] Short-TTL capability tokens
- [NIST800-132] Password-Based Key Derivation
- [RFC2104] HMAC: Keyed-Hashing for Message Authentication
