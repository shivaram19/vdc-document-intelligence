"""
Retrieval store abstraction for project-scoped embeddings and chunks.

Phase 1 keeps Medha's current contract intact: callers still load a full
embedding matrix plus chunk records for one project. This lets us swap the
storage substrate before we rewrite query paths around a vector database's
native search API.
"""

from __future__ import annotations

import json
import os
import pickle
import re
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import numpy as np


@dataclass(frozen=True)
class RetrievalScope:
    tenant_id: str
    database_id: str
    project_id: str


@dataclass
class RetrievalSnapshot:
    embeddings: Optional[np.ndarray]
    chunks: List[dict]


@dataclass
class RetrievalMatch:
    score: float
    chunk: dict


class RetrievalStoreError(RuntimeError):
    """Raised when the configured retrieval backend cannot be used."""


class RetrievalStore(ABC):
    @abstractmethod
    def load_project(self, scope: RetrievalScope) -> RetrievalSnapshot:
        raise NotImplementedError

    @abstractmethod
    def save_project(
        self,
        scope: RetrievalScope,
        embeddings: Optional[np.ndarray],
        chunks: Sequence[dict],
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_project(self, scope: RetrievalScope) -> None:
        raise NotImplementedError

    @abstractmethod
    def search_project(
        self,
        scope: RetrievalScope,
        query_embedding: np.ndarray,
        top_k: int,
    ) -> List[RetrievalMatch]:
        raise NotImplementedError


def _normalize_query_embedding(query_embedding: np.ndarray) -> np.ndarray:
    vector = np.asarray(query_embedding, dtype=np.float32)
    if vector.ndim == 2:
        if vector.shape[0] != 1:
            raise RetrievalStoreError(
                f"Expected one query embedding, got shape {vector.shape}."
            )
        vector = vector[0]
    if vector.ndim != 1:
        raise RetrievalStoreError(
            f"Expected a 1D query embedding, got shape {vector.shape}."
        )
    return vector


def _cosine_similarity(query_matrix: np.ndarray, embeddings: np.ndarray) -> np.ndarray:
    query_norm = query_matrix / np.linalg.norm(query_matrix, axis=1, keepdims=True)
    emb_norm = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    return np.dot(query_norm, emb_norm.T)


def _score_from_cosine_distance(distance: Optional[float]) -> float:
    if distance is None:
        return 0.0
    return float(max(min(1.0 - float(distance), 1.0), -1.0))


class FilesystemRetrievalStore(RetrievalStore):
    """Compatibility store preserving the existing pickle + chunks.json layout."""

    def __init__(self, projects_dir: Path, embeddings_dir: Path):
        self.projects_dir = projects_dir
        self.embeddings_dir = embeddings_dir
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)

    def load_project(self, scope: RetrievalScope) -> RetrievalSnapshot:
        emb_path = self.embeddings_dir / f"{scope.project_id}.pkl"
        chunks_path = self.projects_dir / scope.project_id / "chunks.json"
        if emb_path.exists() and chunks_path.exists():
            with open(emb_path, "rb") as handle:
                embeddings = pickle.load(handle)
            chunks = json.loads(chunks_path.read_text())
            return RetrievalSnapshot(embeddings=embeddings, chunks=chunks)
        return RetrievalSnapshot(embeddings=None, chunks=[])

    def save_project(
        self,
        scope: RetrievalScope,
        embeddings: Optional[np.ndarray],
        chunks: Sequence[dict],
    ) -> None:
        emb_path = self.embeddings_dir / f"{scope.project_id}.pkl"
        chunks_path = self.projects_dir / scope.project_id / "chunks.json"
        chunks_path.parent.mkdir(parents=True, exist_ok=True)
        normalized_embeddings = embeddings if embeddings is not None else np.array([])
        with open(emb_path, "wb") as handle:
            pickle.dump(normalized_embeddings, handle)
        chunks_path.write_text(json.dumps(list(chunks)))

    def delete_project(self, scope: RetrievalScope) -> None:
        emb_path = self.embeddings_dir / f"{scope.project_id}.pkl"
        if emb_path.exists():
            emb_path.unlink()

    def search_project(
        self,
        scope: RetrievalScope,
        query_embedding: np.ndarray,
        top_k: int,
    ) -> List[RetrievalMatch]:
        snapshot = self.load_project(scope)
        embeddings = snapshot.embeddings
        chunks = snapshot.chunks
        if embeddings is None or len(chunks) == 0:
            return []

        query_vector = _normalize_query_embedding(query_embedding).reshape(1, -1)
        sims = _cosine_similarity(query_vector, embeddings)[0]
        limit = max(int(top_k), 1)
        top_indices = np.argsort(sims)[::-1][:limit]
        return [
            RetrievalMatch(
                score=float(sims[idx]),
                chunk=dict(chunks[idx]),
            )
            for idx in top_indices
        ]


class ChromaRetrievalStore(RetrievalStore):
    """
    Chroma-backed store.

    Collection mapping is intentionally simple in phase 1:
    one Chroma collection per project within a tenant/database scope.
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self._clients: Dict[tuple[str, str], object] = {}
        self.api_key = os.environ.get("CHROMA_API_KEY")
        self.host = os.environ.get("CHROMA_HOST")
        self.port = int(os.environ.get("CHROMA_PORT", "8000"))
        self.ssl = os.environ.get("CHROMA_SSL", "false").lower() == "true"
        headers_json = os.environ.get("CHROMA_HTTP_HEADERS_JSON")
        self.headers = json.loads(headers_json) if headers_json else None
        self.chroma_path = Path(os.environ.get("CHROMA_PATH", str(self.data_dir / "chroma")))
        try:
            import chromadb  # type: ignore
        except ImportError as exc:
            raise RetrievalStoreError(
                "RETRIEVAL_BACKEND=chroma requires the 'chromadb' package."
            ) from exc
        self.chromadb = chromadb

    def load_project(self, scope: RetrievalScope) -> RetrievalSnapshot:
        client = self._get_client(scope)
        collection = client.get_or_create_collection(
            name=self._collection_name(scope),
            metadata=self._collection_metadata(scope),
        )
        result = collection.get(include=["documents", "metadatas", "embeddings"])
        ids = result.get("ids")
        if ids is None or len(ids) == 0:
            return RetrievalSnapshot(embeddings=None, chunks=[])

        documents = result.get("documents")
        metadatas = result.get("metadatas")
        embeddings = result.get("embeddings")
        if documents is None:
            documents = []
        if metadatas is None:
            metadatas = []
        if embeddings is None:
            embeddings = []

        rows = []
        for idx, chunk_id in enumerate(ids):
            metadata = (metadatas[idx] if idx < len(metadatas) else {}) or {}
            rows.append(
                (
                    int(metadata.get("chunk_index", idx)),
                    chunk_id,
                    documents[idx] if idx < len(documents) else "",
                    metadata,
                    embeddings[idx] if idx < len(embeddings) else None,
                )
            )

        rows.sort(key=lambda row: row[0])

        chunk_records = [
            {
                "id": chunk_id,
                "text": text,
                "doc_id": metadata.get("doc_id", ""),
                "doc_name": metadata.get("doc_name", ""),
                "doc_type": metadata.get("doc_type", "drawing"),
                "index": int(metadata.get("chunk_index", order)),
            }
            for order, chunk_id, text, metadata, _embedding in rows
        ]

        if any(embedding is None for *_prefix, embedding in rows):
            embedding_matrix = None
        else:
            embedding_matrix = np.asarray([embedding for *_prefix, embedding in rows], dtype=np.float32)

        return RetrievalSnapshot(embeddings=embedding_matrix, chunks=chunk_records)

    def save_project(
        self,
        scope: RetrievalScope,
        embeddings: Optional[np.ndarray],
        chunks: Sequence[dict],
    ) -> None:
        client = self._get_client(scope)
        name = self._collection_name(scope)
        self._delete_collection_if_exists(client, name)

        if not chunks:
            return

        collection = client.get_or_create_collection(
            name=name,
            metadata=self._collection_metadata(scope),
        )

        if embeddings is not None and len(embeddings) != len(chunks):
            raise RetrievalStoreError(
                f"Embedding/chunk length mismatch for project {scope.project_id}: "
                f"{len(embeddings)} embeddings vs {len(chunks)} chunks."
            )

        payload = {
            "ids": [chunk["id"] for chunk in chunks],
            "documents": [chunk["text"] for chunk in chunks],
            "metadatas": [
                {
                    "tenant_id": scope.tenant_id,
                    "database_id": scope.database_id,
                    "project_id": scope.project_id,
                    "doc_id": chunk.get("doc_id", ""),
                    "doc_name": chunk.get("doc_name", ""),
                    "doc_type": chunk.get("doc_type", "drawing"),
                    "chunk_index": int(chunk.get("index", idx)),
                }
                for idx, chunk in enumerate(chunks)
            ],
        }

        if embeddings is not None:
            payload["embeddings"] = np.asarray(embeddings).tolist()

        collection.upsert(**payload)

    def delete_project(self, scope: RetrievalScope) -> None:
        client = self._get_client(scope)
        self._delete_collection_if_exists(client, self._collection_name(scope))

    def search_project(
        self,
        scope: RetrievalScope,
        query_embedding: np.ndarray,
        top_k: int,
    ) -> List[RetrievalMatch]:
        client = self._get_client(scope)
        collection = client.get_or_create_collection(
            name=self._collection_name(scope),
            metadata=self._collection_metadata(scope),
        )
        result = collection.query(
            query_embeddings=[_normalize_query_embedding(query_embedding).tolist()],
            n_results=max(int(top_k), 1),
            include=["documents", "metadatas", "distances"],
        )

        ids_batches = result.get("ids")
        if not ids_batches:
            return []

        ids = ids_batches[0] if ids_batches else []
        documents_batches = result.get("documents") or [[]]
        metadatas_batches = result.get("metadatas") or [[]]
        distances_batches = result.get("distances") or [[]]
        documents = documents_batches[0] if documents_batches else []
        metadatas = metadatas_batches[0] if metadatas_batches else []
        distances = distances_batches[0] if distances_batches else []

        matches: List[RetrievalMatch] = []
        for idx, chunk_id in enumerate(ids):
            metadata = (metadatas[idx] if idx < len(metadatas) else {}) or {}
            matches.append(
                RetrievalMatch(
                    score=_score_from_cosine_distance(
                        distances[idx] if idx < len(distances) else None
                    ),
                    chunk={
                        "id": chunk_id,
                        "text": documents[idx] if idx < len(documents) else "",
                        "doc_id": metadata.get("doc_id", ""),
                        "doc_name": metadata.get("doc_name", ""),
                        "doc_type": metadata.get("doc_type", "drawing"),
                        "index": int(metadata.get("chunk_index", idx)),
                    },
                )
            )
        return matches

    def _get_client(self, scope: RetrievalScope):
        cache_key = (scope.tenant_id, scope.database_id)
        if cache_key not in self._clients:
            self._clients[cache_key] = self._build_client(scope)
        return self._clients[cache_key]

    def _build_client(self, scope: RetrievalScope):
        if self.api_key:
            return self.chromadb.CloudClient(
                api_key=self.api_key,
                tenant=scope.tenant_id,
                database=scope.database_id,
            )

        if self.host:
            return self.chromadb.HttpClient(
                host=self.host,
                port=self.port,
                ssl=self.ssl,
                headers=self.headers,
                tenant=scope.tenant_id,
                database=scope.database_id,
            )

        self.chroma_path.mkdir(parents=True, exist_ok=True)
        bootstrap_client = self.chromadb.PersistentClient(
            path=str(self.chroma_path),
            tenant=getattr(self.chromadb, "DEFAULT_TENANT", "default_tenant"),
            database=getattr(self.chromadb, "DEFAULT_DATABASE", "default_database"),
        )
        self._ensure_namespace(bootstrap_client, scope)
        return self.chromadb.PersistentClient(
            path=str(self.chroma_path),
            tenant=scope.tenant_id,
            database=scope.database_id,
        )

    def _collection_name(self, scope: RetrievalScope) -> str:
        raw = f"project-{scope.project_id}"
        sanitized = re.sub(r"[^a-zA-Z0-9_-]", "-", raw).strip("-")
        if len(sanitized) < 3:
            sanitized = f"p-{scope.project_id[:12]}"
        return sanitized[:63]

    def _collection_metadata(self, scope: RetrievalScope) -> dict:
        return {
            "tenant_id": scope.tenant_id,
            "database_id": scope.database_id,
            "project_id": scope.project_id,
            "retrieval_backend": "chroma",
            "hnsw:space": "cosine",
        }

    @staticmethod
    def _ensure_namespace(client, scope: RetrievalScope) -> None:
        admin = getattr(client, "_admin_client", None)
        if admin is None:
            return

        try:
            admin.get_tenant(name=scope.tenant_id)
        except Exception:
            admin.create_tenant(name=scope.tenant_id)

        try:
            admin.get_database(name=scope.database_id, tenant=scope.tenant_id)
        except Exception:
            admin.create_database(name=scope.database_id, tenant=scope.tenant_id)

    @staticmethod
    def _delete_collection_if_exists(client, collection_name: str) -> None:
        try:
            client.delete_collection(collection_name)
        except Exception:
            pass


class PgvectorRetrievalStore(RetrievalStore):
    """
    pgvector-backed store.

    Phase 1 uses pgvector as a persistence substrate, not yet as the primary
    query path. The application still loads one project's full embedding matrix
    so existing graph/contradiction flows continue to work unchanged.
    """

    def __init__(self):
        self.dsn = os.environ.get("PGVECTOR_DSN", "").strip()
        if not self.dsn:
            raise RetrievalStoreError(
                "RETRIEVAL_BACKEND=pgvector requires PGVECTOR_DSN."
            )

        self.table_name = os.environ.get("PGVECTOR_TABLE", "medha_retrieval_chunks").strip()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", self.table_name):
            raise RetrievalStoreError(
                f"Invalid PGVECTOR_TABLE='{self.table_name}'. Use letters, numbers, and underscores only."
            )

        self.auto_init = os.environ.get("PGVECTOR_AUTO_INIT", "false").lower() == "true"
        self.embedding_dim = int(os.environ.get("PGVECTOR_EMBEDDING_DIM", "768"))

        try:
            import psycopg  # type: ignore
            from pgvector.psycopg import register_vector  # type: ignore
            from psycopg.rows import dict_row  # type: ignore
            from psycopg.types.json import Jsonb  # type: ignore
        except ImportError as exc:
            raise RetrievalStoreError(
                "RETRIEVAL_BACKEND=pgvector requires 'psycopg[binary]' and 'pgvector'."
            ) from exc

        self.psycopg = psycopg
        self.register_vector = register_vector
        self.dict_row = dict_row
        self.Jsonb = Jsonb
        self.scope_index_name = f"{self.table_name}_scope_order_idx"[:63]
        self.vector_index_name = f"{self.table_name}_embedding_cos_idx"[:63]
        self._thread_local = threading.local()

    def load_project(self, scope: RetrievalScope) -> RetrievalSnapshot:
        query = f"""
            SELECT
                chunk_id,
                doc_id,
                doc_name,
                doc_type,
                chunk_index,
                chunk_text,
                embedding,
                chunk_payload
            FROM {self.table_name}
            WHERE tenant_id = %s
              AND database_id = %s
              AND project_id = %s
            ORDER BY chunk_index ASC
        """

        conn = self._connect()
        with conn.cursor() as cur:
            cur.execute(query, self._scope_tuple(scope))
            rows = cur.fetchall()

        if not rows:
            return RetrievalSnapshot(embeddings=None, chunks=[])

        chunk_records: List[dict] = []
        embedding_rows = []
        missing_embedding = False

        for row in rows:
            payload = row.get("chunk_payload") or {}
            chunk = dict(payload) if isinstance(payload, dict) else {}
            chunk.update(
                {
                    "id": row["chunk_id"],
                    "text": row["chunk_text"],
                    "doc_id": row["doc_id"],
                    "doc_name": row["doc_name"],
                    "doc_type": row["doc_type"],
                    "index": int(row["chunk_index"]),
                }
            )
            chunk_records.append(chunk)

            embedding = row.get("embedding")
            if embedding is None:
                missing_embedding = True
            else:
                embedding_rows.append(np.asarray(embedding, dtype=np.float32))

        if missing_embedding:
            embedding_matrix = None
        else:
            embedding_matrix = np.vstack(embedding_rows) if embedding_rows else np.array([], dtype=np.float32)

        return RetrievalSnapshot(embeddings=embedding_matrix, chunks=chunk_records)

    def save_project(
        self,
        scope: RetrievalScope,
        embeddings: Optional[np.ndarray],
        chunks: Sequence[dict],
    ) -> None:
        if embeddings is not None and len(embeddings) != len(chunks):
            raise RetrievalStoreError(
                f"Embedding/chunk length mismatch for project {scope.project_id}: "
                f"{len(embeddings)} embeddings vs {len(chunks)} chunks."
            )

        delete_sql = f"""
            DELETE FROM {self.table_name}
            WHERE tenant_id = %s
              AND database_id = %s
              AND project_id = %s
        """
        insert_sql = f"""
            INSERT INTO {self.table_name} (
                tenant_id,
                database_id,
                project_id,
                chunk_id,
                doc_id,
                doc_name,
                doc_type,
                chunk_index,
                chunk_text,
                embedding,
                chunk_payload
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """

        conn = self._connect()
        with conn.cursor() as cur:
            cur.execute(delete_sql, self._scope_tuple(scope))
            if not chunks:
                return

            rows = []
            for idx, chunk in enumerate(chunks):
                vector = None
                if embeddings is not None:
                    vector = np.asarray(embeddings[idx], dtype=np.float32)
                rows.append(
                    (
                        scope.tenant_id,
                        scope.database_id,
                        scope.project_id,
                        chunk["id"],
                        str(chunk.get("doc_id", "")),
                        str(chunk.get("doc_name", "")),
                        str(chunk.get("doc_type", "drawing")),
                        int(chunk.get("index", idx)),
                        chunk["text"],
                        vector,
                        self.Jsonb(dict(chunk)),
                    )
                )
            cur.executemany(insert_sql, rows)

    def delete_project(self, scope: RetrievalScope) -> None:
        delete_sql = f"""
            DELETE FROM {self.table_name}
            WHERE tenant_id = %s
              AND database_id = %s
              AND project_id = %s
        """
        conn = self._connect()
        with conn.cursor() as cur:
            cur.execute(delete_sql, self._scope_tuple(scope))

    def search_project(
        self,
        scope: RetrievalScope,
        query_embedding: np.ndarray,
        top_k: int,
    ) -> List[RetrievalMatch]:
        vector = _normalize_query_embedding(query_embedding)
        query = f"""
            SELECT
                chunk_id,
                doc_id,
                doc_name,
                doc_type,
                chunk_index,
                chunk_text,
                chunk_payload,
                (1 - (embedding <=> %s)) AS score
            FROM {self.table_name}
            WHERE tenant_id = %s
              AND database_id = %s
              AND project_id = %s
              AND embedding IS NOT NULL
            ORDER BY embedding <=> %s ASC
            LIMIT %s
        """
        conn = self._connect()
        with conn.cursor() as cur:
            cur.execute(
                query,
                (
                    vector,
                    scope.tenant_id,
                    scope.database_id,
                    scope.project_id,
                    vector,
                    max(int(top_k), 1),
                ),
            )
            rows = cur.fetchall()

        matches: List[RetrievalMatch] = []
        for row in rows:
            payload = row.get("chunk_payload") or {}
            chunk = dict(payload) if isinstance(payload, dict) else {}
            chunk.update(
                {
                    "id": row["chunk_id"],
                    "text": row["chunk_text"],
                    "doc_id": row["doc_id"],
                    "doc_name": row["doc_name"],
                    "doc_type": row["doc_type"],
                    "index": int(row["chunk_index"]),
                }
            )
            matches.append(
                RetrievalMatch(
                    score=float(row.get("score") or 0.0),
                    chunk=chunk,
                )
            )
        return matches

    def _connect(self):
        conn = getattr(self._thread_local, "conn", None)
        if conn is not None and not conn.closed:
            return conn

        conn = self.psycopg.connect(
            self.dsn,
            row_factory=self.dict_row,
            autocommit=True,
        )
        self._thread_local.conn = conn
        if self.auto_init:
            self._ensure_schema(conn)
        self.register_vector(conn)
        return conn

    def _ensure_schema(self, conn) -> None:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                tenant_id TEXT NOT NULL,
                database_id TEXT NOT NULL,
                project_id TEXT NOT NULL,
                chunk_id TEXT NOT NULL,
                doc_id TEXT NOT NULL,
                doc_name TEXT NOT NULL,
                doc_type TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                chunk_text TEXT NOT NULL,
                embedding vector({self.embedding_dim}),
                chunk_payload JSONB NOT NULL DEFAULT '{{}}'::jsonb,
                PRIMARY KEY (tenant_id, database_id, project_id, chunk_id)
            )
            """
        )
        conn.execute(
            f"""
            CREATE INDEX IF NOT EXISTS {self.scope_index_name}
            ON {self.table_name} (tenant_id, database_id, project_id, chunk_index)
            """
        )
        conn.execute(
            f"""
            CREATE INDEX IF NOT EXISTS {self.vector_index_name}
            ON {self.table_name} USING hnsw (embedding vector_cosine_ops)
            WHERE embedding IS NOT NULL
            """
        )

    @staticmethod
    def _scope_tuple(scope: RetrievalScope) -> tuple[str, str, str]:
        return (scope.tenant_id, scope.database_id, scope.project_id)


def build_retrieval_store(data_dir: Path, projects_dir: Path, embeddings_dir: Path) -> RetrievalStore:
    backend = os.environ.get("RETRIEVAL_BACKEND", "filesystem").strip().lower()
    if backend == "filesystem":
        return FilesystemRetrievalStore(projects_dir=projects_dir, embeddings_dir=embeddings_dir)
    if backend == "chroma":
        return ChromaRetrievalStore(data_dir=data_dir)
    if backend == "pgvector":
        return PgvectorRetrievalStore()
    raise RetrievalStoreError(
        f"Unsupported RETRIEVAL_BACKEND='{backend}'. Expected 'filesystem', 'chroma', or 'pgvector'."
    )
