CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS medha_retrieval_chunks (
    tenant_id TEXT NOT NULL,
    database_id TEXT NOT NULL,
    project_id TEXT NOT NULL,
    chunk_id TEXT NOT NULL,
    doc_id TEXT NOT NULL,
    doc_name TEXT NOT NULL,
    doc_type TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding vector(768),
    chunk_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    PRIMARY KEY (tenant_id, database_id, project_id, chunk_id)
);

CREATE INDEX IF NOT EXISTS medha_retrieval_chunks_scope_order_idx
    ON medha_retrieval_chunks (tenant_id, database_id, project_id, chunk_index);

CREATE INDEX IF NOT EXISTS medha_retrieval_chunks_embedding_cos_idx
    ON medha_retrieval_chunks USING hnsw (embedding vector_cosine_ops)
    WHERE embedding IS NOT NULL;
