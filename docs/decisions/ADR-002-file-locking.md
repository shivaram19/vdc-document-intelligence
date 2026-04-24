# ADR-002: Cross-Process File Locking for Shared Memory

## Status
Accepted — implemented 2026-04-24

## Context
Multiple agents (bridge, inbox watcher, orchestrator daemon, fleet nodes) read/write the same JSON files. Race conditions caused:
- Lost documents during concurrent ingest
- Corrupted `state.json` when bridge + orchestrator wrote simultaneously
- Session store inconsistency under parallel auth flows

## Decision
Use `filelock.FileLock` (fcntl-based on Linux) around all read-modify-write cycles, plus atomic writes via `tempfile.mkstemp` + `os.replace`.

## Consequences
- **Positive**: Eliminates TOCTOU races on all shared state.
- **Positive**: Crash-safe writes — `os.replace` is atomic on POSIX.
- **Negative**: Adds ~1–2ms latency per state operation. Negligible vs. LLM API calls (1–3s).

## Research Basis
- [Brewer2012] CAP theorem: shared-state systems must choose consistency over availability for critical data.
- [ZetCode2025] "Python os.replace Function — Complete Guide", https://zetcode.com/python/os-replace/ — `os.replace` atomically replaces destination on POSIX (rename(2)) and Windows (MoveFileEx). Pattern: write to tempfile in same directory, then `os.replace(temp, target)`.
- [ActiveState2015] "Safely and atomically write to a file", https://code.activestate.com/recipes/579097-safely-and-atomically-write-to-a-file/ — Uses `tempfile.mkstemp` + `os.fdopen` + `os.replace` for atomic writes with cleanup on exception.
- [PythonOrg2021] "Adding atomicwrite in stdlib", https://discuss.python.org/t/adding-atomicwrite-in-stdlib/11899 — Community consensus: atomic write via tempfile + rename is the correct idiom. `os.replace` preferred over `os.rename` for cross-platform overwrite.
- [StackOverflow2021] "How to do atomic file replacement?", https://stackoverflow.com/questions/7645338/how-to-do-atomic-file-replacement — `os.replace()` is atomic on ALL platforms under most conditions.

## Alternatives Considered
1. **SQLite** — rejected: good for structured data, but our schema is fluid JSON. Migration complexity too high for current stage.
2. **Redis** — rejected: adds external dependency; this is designed to run on a single node or air-gapped.
3. **mmap + atomic CAS** — rejected: overkill; filelock + atomic write is sufficient and simpler.

## Code Location
- `picocloth/shared/locks.py` (new module)
- `picocloth/agents/vdc_core.py` (all I/O functions)
- `picocloth/agents/auth/session_store.py`
