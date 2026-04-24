# Search Log — 2026-04-24

## Query 1: SentenceTransformer model preload startup latency RAG optimization 2024

### Findings
- **Source**: Milvus AI Quick Reference (2026-02-10)  
  URL: https://milvus.io/ai-quick-reference/why-is-the-first-inference-call-on-a-sentence-transformer-model-much-slower-than-subsequent-calls-the-cold-start-problem-and-how-can-i-mitigate-this-in-a-production-setting
  
  First inference is slow because: weights read from disk, computational graphs built, hardware-specific optimizations (CUDA kernel init) triggered. PyTorch/ONNX may JIT-compile operations during first inference. Solution: pre-warm with dummy data at startup. Deploy as persistent service, not per-request reload.

- **Source**: APXML Practical RAG Latency Optimization (2025-05-23)  
  URL: https://apxml.com/courses/optimizing-rag-for-production/chapter-4-end-to-end-rag-performance/hands-on-rag-latency-optimization
  
  RAG pipeline profiling shows embedding + retrieval are the hot paths. Caching LLM responses and selective reranking cuts latency from ~2.3s to ~0.45s.

- **Source**: SBERT Efficiency Docs  
  URL: https://sbert.net/docs/sentence_transformer/usage/efficiency.html
  
  Flash Attention 2 with input flattening eliminates padding overhead. Default PyTorch backend triggers JIT compilation on first encode().

- **Source**: TowardsAI — Speeding Up RAG Pipelines (2025-11-27)  
  URL: https://pub.towardsai.net/speeding-up-rag-pipelines-how-to-cut-latency-by-90-in-production-8e70aa03dd70
  
  Total latency reduction from ~2.3s to ~0.45s via caching and optimization.

## Query 2: Python filelock atomic write tempfile os.replace cross-process 2024

### Findings
- **Source**: ZetCode Python os.replace Guide (2025-04-11)  
  URL: https://zetcode.com/python/os-replace/
  
  `os.replace` atomically replaces destination on POSIX (rename(2)) and Windows (MoveFileEx). Pattern: write to tempfile in same directory, then `os.replace(temp, target)`. Ensures target is always consistent.

- **Source**: ActiveState Recipe — Safely and atomically write to a file (2015-09-02)  
  URL: https://code.activestate.com/recipes/579097-safely-and-atomically-write-to-a-file/
  
  Uses `tempfile.mkstemp` + `os.fdopen` + `os.replace` for atomic writes. Cleanup on exception.

- **Source**: Python.org Discussions — Adding atomicwrite in stdlib (2021-11-12)  
  URL: https://discuss.python.org/t/adding-atomicwrite-in-stdlib/11899
  
  Community consensus: atomic write via tempfile + rename is the correct idiom. `os.replace` preferred over `os.rename` for cross-platform overwrite.

- **Source**: StackOverflow — How to do atomic file replacement? (2021-12-15)  
  URL: https://stackoverflow.com/questions/7645338/how-to-do-atomic-file-replacement
  
  `os.replace()` is atomic on ALL platforms under most conditions. `os.rename()` throws FileExistsError on Windows.

- **Source**: python-atomicwrites docs  
  URL: https://python-atomicwrites.readthedocs.io/
  
  Uses `tempfile.mkstemp` in same directory for same-filesystem atomic move. POSIX uses `rename`, Windows uses `MoveFileEx`.

## Query 3: HMAC secret key stability token invalidation security best practice

### Findings
- **Source**: GitGuardian — HMAC Secrets Explained (2026-01-15)  
  URL: https://blog.gitguardian.com/hmac-secrets-explained-authentication/
  
  Key management: use cryptographically secure RNG, min 32 bytes. Never commit secrets. Include timestamp in signed payload. Use constant-time comparison.

- **Source**: WhoisArjen — HMAC Timestamp Tokens (2026-03-15)  
  URL: https://whoisarjen.com/blog/hmac-timestamp-tokens-zero-trust-service-communication
  
  Shared secrets should never travel over wire. Time-limited tokens eliminate replay. Rotation should be env var change, not migration. "No database updates, no token invalidation, no coordination beyond deploying the new secret."

- **Source**: Permify — Token Based Authentication (2024-10-28)  
  URL: https://permify.co/post/token-based-authentication/
  
  Token revocation mechanism essential for security breaches. Maintain token blacklist for immediate invalidation.

- **Source**: Clavax — Secure App APIs Against Token Theft (2025-07-16)  
  URL: https://www.clavax.com/blog/how-to-secure-app-apis-against-token-theft-and-replay-attacks/
  
  Short-lived tokens (minutes) + secure refresh. Rate limiting. Behavioral analytics for anomaly detection.

- **Source**: S4E — Fragile Trust Behind JWTs  
  URL: https://resources.s4e.io/blog/the-fragile-trust-behind-jwts-understanding-exploits-and-defenses/
  
  Proper secret storage and key rotation policies: keep signing secrets out of code. Use secrets manager. Rotate on schedule. Support multiple active keys during transitions.
