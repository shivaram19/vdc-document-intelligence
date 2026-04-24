# Finder (node-a)
## Problem: "I waste 20 minutes searching for one spec clause."

### JTBD
When a superintendent is on site and needs to know the concrete strength, they want to ask in plain English and get an answer in 3 seconds — not hunt through 10,000 pages.

### What Finder Does
1. Receives natural language query from user
2. Embeds query vector using preloaded `all-mpnet-base-v2`
3. Performs cosine similarity search against project embeddings
4. Ranks chunks by relevance score
5. Routes top-5 chunks to LLM for synthesis
6. Returns answer with **cited sources** (document name, page, confidence)

### Research Basis
- [CITE: Fathima2024] Construction professionals in developing markets cite "information retrieval friction" as the #1 BIM adoption barrier.
- [CITE: APXML2025] Embedding + retrieval are the hot paths in RAG pipelines. Caching cuts latency from ~2.3s to ~0.45s.
- [CITE: Papaioannou2023] LLM outputs without cited sources are distrusted by engineers. Finder always includes `Sources: [doc_name]`.

### Capability
```
can_query
```

### Success Metric
- Query latency: < 5s (currently 3.3s)
- Source citation rate: 100%
- User satisfaction: "I found it faster than Ctrl+F"
