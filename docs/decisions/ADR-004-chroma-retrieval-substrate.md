# ADR-004: Pluggable Retrieval Substrate with Chroma-First and pgvector Scaffold

## Status
Accepted - native query path implemented for primary ask flows on 2026-04-30

## Context
Medha's current backend persists embeddings as one pickle file per project plus a
`chunks.json` file under the local filesystem. This works for a single-node demo,
but it does not provide a clean abstraction for tenant-aware retrieval storage or
for later migration to a managed vector store.

At the same time, Medha's product promise is still document-first: it sits
alongside BIM and PM systems, makes project documents queryable, and answers from
specs, RFIs, and contracts. The BIM and visual endpoints remain future work.

We need a retrieval substrate that:
- preserves the current project-scoped query contract;
- gives us a clean path to tenant/database/project isolation;
- does not force an immediate rewrite of graph, contradiction, and domain-analysis
  flows that still expect a full embedding matrix in memory.

We also need to decide how to use Chroma's newer Context-1 model without turning
the whole product into a vendor-shaped search loop, and without binding Medha to
one vector store before we have benchmark evidence.

## Decision
1. Adopt a **pluggable retrieval substrate** for Medha's document layer.
2. Keep the backend contract project-scoped for now, but introduce explicit
   retrieval scope dimensions: `tenant_id`, `database_id`, and `project_id`.
3. Map storage as:
   - `tenant = customer organization`
   - `database = environment or workspace`
   - `collection = project`
4. Add a `RetrievalStore` abstraction in the backend with:
   - `FilesystemRetrievalStore` as the default, preserving current behavior;
   - `ChromaRetrievalStore` as the first opt-in vector backend selected via
     `RETRIEVAL_BACKEND=chroma`;
   - `PgvectorRetrievalStore` as the second opt-in backend selected via
     `RETRIEVAL_BACKEND=pgvector`.
5. Move Medha's primary `/query` and `/draft-rfi` flows onto
   `RetrievalStore.search_project(...)` so vector-capable backends can use native
   search instead of forcing every query through "load all embeddings into app
   memory" first.
6. Do **not** make Context-1 the default path for every query. Use it later as a
   retrieval specialist for hard multi-hop search tasks: cross-document
   contradiction hunts, long-horizon submittal tracebacks, and code/spec/drawing
   triangulation.

## Consequences
- **Positive**: Retrieval persistence is no longer hard-coded into `backend/app.py`.
- **Positive**: We can move from local pickle files to Chroma or pgvector without
  rewriting Medha's query, contradiction, graph, and domain-analysis flows in one
  change.
- **Positive**: The storage model now matches the intended SaaS isolation shape.
- **Positive**: Backend choice is now a deployment concern rather than an
  application rewrite.
- **Positive**: The main ask flow now exercises backend-native search for Chroma
  and pgvector.
- **Negative**: Contradiction detection, graph expansion, and domain-analysis
  paths still load the full project snapshot into application memory.
- **Negative**: Neither Chroma nor pgvector replaces application-layer authz. Tenant and
  authorization enforcement still need proper identity and policy work.
- **Negative**: Context-1 remains unproven on Medha's own benchmark set and must
  be gated behind an ADR-backed evaluation before becoming a default retrieval
  strategy.

## Research Basis
- [ChromaContext1_2026] Chroma, "Context-1" research note,
  https://www.trychroma.com/research/context-1
  - Context-1 is presented as a retrieval subagent that returns a ranked set of
    supporting documents for a downstream model, not as a full application
    runtime.
- [ChromaCloud_2026] Chroma Cloud getting started docs,
  https://docs.trychroma.com/cloud/getting-started
  - Chroma Cloud supports managed deployments and single-tenant/BYOC deployment
    options.
- [ChromaClients_2026] Chroma cookbook, "Clients",
  https://cookbook.chromadb.dev/core/clients/
  - Chroma clients expose tenant/database scoping primitives, including cloud and
    local persistent clients.
- [ChromaTenants_2026] Chroma cookbook, "Tenants and Databases",
  https://cookbook.chromadb.dev/core/tenants-and-databases/
  - Chroma models organization through tenants, databases, and collections.
- [ChromaMultiTenancy_2026] Chroma cookbook, "Multi tenancy",
  https://cookbook.chromadb.dev/strategies/multi-tenancy/
  - Naive single-node multitenancy patterns are not sufficient for production;
    authorization must still be handled deliberately.

## Alternatives Considered
1. **Keep filesystem pickle storage indefinitely**
   - Rejected: acceptable for a single-node prototype, but it keeps tenant-aware
     retrieval and vector-store migration coupled to `backend/app.py`.
2. **Switch fully to a vector store's native query APIs in one rewrite**
   - Rejected: too much blast radius. Graph expansion, contradiction detection,
     and domain-analysis all still consume the in-memory embedding matrix.
3. **Adopt Context-1 as the default query engine immediately**
   - Rejected: wrong layer. Context-1 is promising for hard retrieval, but it is
     not the same thing as multi-tenant storage, authz, or the product's full
     reasoning path.

## Follow-Up Work
1. Add a Medha benchmark harness comparing filesystem retrieval, Chroma,
   pgvector, and Context-1-assisted retrieval on contradiction and RFI tasks.
2. Introduce authenticated tenant resolution so `tenant_id` and `database_id` are
   derived from identity rather than environment defaults.
3. Move graph expansion and contradiction-oriented retrieval from "load full
   matrix into app memory" to backend-native filtered query APIs where
   appropriate.

## Code Location
- `backend/retrieval_store.py`
- `backend/app.py`
