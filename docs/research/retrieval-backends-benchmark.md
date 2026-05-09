# Retrieval Backends Benchmark

## Scope
Local development setup and benchmark harness for Medha's pluggable retrieval
substrate.

## What This Covers
- Filesystem retrieval (current baseline)
- Chroma in embedded mode (`PersistentClient`)
- pgvector via local Dockerized Postgres
- Native `search_project(...)` retrieval for the primary ask flow

## Repo-Local Environment

Build an isolated retrieval environment instead of installing optional backend
dependencies into user site-packages:

```bash
./backend/bootstrap_retrieval_env.sh
source venv-retrieval/bin/activate
```

Optional local-LLM fallback dependencies remain separate:

```bash
pip install -r backend/requirements-local-llm.txt
```

## Local pgvector Setup

```bash
docker compose -f docker-compose.pgvector.yml up -d
```

Connection defaults:

```bash
export RETRIEVAL_BACKEND=pgvector
export PGVECTOR_DSN=postgresql://medha:medha@127.0.0.1:5433/medha
export PGVECTOR_AUTO_INIT=true
```

The SQL bootstrap is mounted from:

- `backend/sql/001_medha_retrieval_chunks_pgvector.sql`

## Optional Python Dependencies

For Chroma:

```bash
pip install -r backend/requirements-chroma.txt
```

For pgvector client access:

```bash
pip install -r backend/requirements-pgvector.txt
```

## Benchmark Harness

Run the benchmark from the repo root:

```bash
python3 benchmark_retrieval_backends.py --backends filesystem chroma pgvector
```

The harness:
- resolves the benchmark projects by name;
- seeds non-filesystem backends from the current filesystem baseline;
- measures load latency, native query retrieval latency, and contradiction-scan latency;
- checks query hit quality against expected source documents;
- checks contradiction counts against the filesystem baseline.

Default report path:

- `.bench/retrieval_backend_benchmark_report.json`

## Latest Local Run

Snapshot from `2026-04-30` using `all-mpnet-base-v2`:

| Backend | Avg load | Avg query | Avg contradiction | Query doc hits | Query snippet hits | Contradiction matches |
|---------|----------|-----------|-------------------|----------------|--------------------|-----------------------|
| `filesystem` | 0.40 ms | 0.78 ms | 0.36 ms | 4/4 | 2/4 | 1/1 |
| `chroma` | 28.73 ms | 5.86 ms | 0.60 ms | 4/4 | 2/4 | 1/1 |
| `pgvector` | 25.65 ms | 2.75 ms | 0.48 ms | 4/4 | 2/4 | 1/1 |

Observed seeding times:

- `chroma`: ~316 ms for `Downtown Office Tower`, ~452 ms for `Construction Robotics Study`
- `pgvector`: ~53 ms for `Downtown Office Tower`, ~47 ms for `Construction Robotics Study`

Interpretation:

- `filesystem` still wins raw project load latency because it is just local pickle +
  JSON file reads.
- `chroma` and `pgvector` preserve retrieval quality on this benchmark set.
- Query latency now reflects each backend's native retrieval call rather than the
  previous in-process cosine-scoring loop.
- On this local benchmark, pgvector outperforms embedded Chroma on query latency,
  while both vector backends are slower than the filesystem baseline on tiny demo
  projects.

## Notes

- Chroma does **not** need a local server for this harness; the default path uses
  embedded persistence under `.bench/chroma`.
- pgvector **does** require the Docker service unless you point `PGVECTOR_DSN` at
  an existing Postgres instance with the `vector` extension enabled.
- The pgvector benchmark needs actual local database access. In a restricted
  sandbox, run it outside the sandbox or point `PGVECTOR_DSN` at a reachable
  instance.
- The backend query and RFI routes now use `RetrievalStore.search_project(...)`,
  so this benchmark is aligned with the main user-facing ask flow.
- This harness benchmarks the current Medha retrieval contract, where the app
  still loads a full project snapshot for contradiction and graph workflows. It is
  useful for comparing the current hybrid state, not as a final large-scale vector
  serving benchmark.
