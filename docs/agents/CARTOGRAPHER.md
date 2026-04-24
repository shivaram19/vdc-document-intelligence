# Cartographer (node-h)
## Problem: "If I change the HVAC spec, what drawings are affected?"

### JTBD
When a design change is proposed, the architect wants to know every document, RFI, and spec clause that references the same system — not just the one they searched for.

### What Cartographer Does
1. Extracts entity relationships from documents (HVAC → ductwork → drawing A-201 → spec M-301)
2. Builds a knowledge graph linking specs, drawings, RFIs, and submittals
3. Enables "what else is affected?" queries
4. Visualizes document dependencies for impact analysis

### Research Basis
- [CITE: MorandiniPhD] Construction knowledge graphs enable impact analysis across document types.
- [CITE: Li2024] Agent specialization — Cartographer focuses exclusively on relationship mapping, not retrieval.

### Capability
```
can_graph
```

### Success Metric
- Relationship extraction accuracy: > 85%
- Graph query latency: < 2s
- Coverage: All ingested documents linked

### Future Enhancement
- Export to Neo4j for complex graph analytics
- Visual graph explorer in dashboard
