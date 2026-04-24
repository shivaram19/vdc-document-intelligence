# Builder (node-b)
## Problem: "I uploaded 500 files and the system froze."

### JTBD
When bulk-uploading documents or running a full-project contradiction scan, the user wants the task to complete in the background without blocking queries or the UI.

### What Builder Does
1. Accepts long-running task assignments from Dispatcher
2. Executes tasks in thread pool (ingestion, batch scans, re-indexing)
3. Reports progress via shared memory events
4. Handles task retry on failure
5. Cleans up temporary files after completion

### Research Basis
- [CITE: APXML2025] Async processing for non-blocking UI. Batch operations must not block interactive queries.
- [CITE: Milvus2026] CPU-bound work (embedding generation) should run in background threads to keep event loop responsive.

### Capability
```
can_execute
```

### Success Metric
- Background task throughput: > 50 files/hour
- UI blocking time: 0ms (always async)
- Retry success rate: > 95% after 3 attempts
