# ADR-001: Embedding Model Preloading at Startup

## Status
Accepted — implemented 2026-04-24

## Context
WebSocket queries were timing out after 90–120s because `SentenceTransformer('all-mpnet-base-v2')` was loaded lazily on the first `encode()` call inside a thread pool worker. The asyncio event loop could not respond to pings/keepalives while the thread blocked on model I/O.

## Decision
Preload the embedding model in `main()` before `await runner.setup()`, so it is warm before any WebSocket connections are accepted.

## Consequences
- **Positive**: First-query latency dropped from 90–120s to ~3s. No timeouts.
- **Positive**: Predictable memory usage at startup — no surprise 400MB allocation mid-request.
- **Negative**: Bridge startup time increases by ~10s (model download/load). Acceptable for a long-running daemon.

## Research Basis
- [Milvus2026] "Why is the first inference call on a Sentence Transformer model much slower?" https://milvus.io/ai-quick-reference/why-is-the-first-inference-call-on-a-sentence-transformer-model-much-slower-than-subsequent-calls-the-cold-start-problem-and-how-can-i-mitigate-this-in-a-production-setting — First inference is slow because weights are read from disk, computational graphs are built, and hardware-specific optimizations (CUDA kernel init) are triggered. PyTorch may JIT-compile operations during first inference.
- [SBERT2025] Sentence Transformers Efficiency Docs, https://sbert.net/docs/sentence_transformer/usage/efficiency.html — Default PyTorch backend triggers JIT compilation on first `encode()`.
- [APXML2025] "Practical RAG Latency Optimization", https://apxml.com/courses/optimizing-rag-for-production/chapter-4-end-to-end-rag-performance/hands-on-rag-latency-optimization — Embedding + retrieval are the hot paths in RAG pipelines. Caching cuts latency from ~2.3s to ~0.45s.

## Alternatives Considered
1. **ProcessPoolExecutor** for encode() — rejected: model would be loaded in *every* process (4GB RAM waste), and serialization overhead for numpy arrays is high.
2. **Async model load with asyncio.to_thread()** — rejected: still blocks first query; just moves the problem.
3. **Keep lazy load, increase client timeout** — rejected: masks the root cause; clients on mobile networks would still fail.

## Code Location
- `picocloth/agents/vdc_core.py:preload_model()`
- `picocloth/bridge/agent_bridge.py:main()`
