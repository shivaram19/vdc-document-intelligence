#!/usr/bin/env python3
"""
Benchmark retrieval backends on Medha query and contradiction workloads.

This harness compares:
- filesystem (baseline)
- chroma (embedded by default)
- pgvector (requires local Postgres/pgvector)

It does not need the Flask API. It exercises the retrieval seam directly.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Sequence

import numpy as np
from sentence_transformers import SentenceTransformer

from backend.retrieval_store import (
    ChromaRetrievalStore,
    FilesystemRetrievalStore,
    PgvectorRetrievalStore,
    RetrievalScope,
    RetrievalSnapshot,
    RetrievalStoreError,
)

REPO_ROOT = Path(__file__).resolve().parent
DATA_DIR = REPO_ROOT / "data"
PROJECTS_DIR = DATA_DIR / "projects"
EMBEDDINGS_DIR = DATA_DIR / "embeddings"
BENCH_DIR = REPO_ROOT / ".bench"
BENCH_DIR.mkdir(exist_ok=True)

DEFAULT_MODEL = os.environ.get("BENCHMARK_EMBEDDING_MODEL", "all-mpnet-base-v2")
DEFAULT_REPORT = BENCH_DIR / "retrieval_backend_benchmark_report.json"
ALLOW_MODEL_DOWNLOAD = os.environ.get("BENCHMARK_ALLOW_MODEL_DOWNLOAD", "false").lower() == "true"

QUERY_CASES = [
    {
        "project": "Downtown Office Tower",
        "query": "What is the HVAC temperature setpoint for office spaces?",
        "expected_doc": "MECH_SPEC_HVAC.txt",
        "expected_snippet": "70",
        "tags": ["hvac", "setpoint"],
    },
    {
        "project": "Downtown Office Tower",
        "query": "What is the concrete strength for columns?",
        "expected_doc": "STRUCT_SPEC.txt",
        "expected_snippet": "5,000 psi",
        "tags": ["structural", "concrete"],
    },
    {
        "project": "Downtown Office Tower",
        "query": "What are the live loads for mechanical rooms?",
        "expected_doc": "STRUCT_SPEC.txt",
        "expected_snippet": "150 psf",
        "tags": ["loads", "mechanical"],
    },
    {
        "project": "Construction Robotics Study",
        "query": "What are the key findings of the construction robotics report?",
        "expected_doc": "Construction_Robotics_Report_2026.pdf",
        "expected_snippet": "robot",
        "tags": ["robotics", "dynamic"],
    },
]

CONTRADICTION_PROJECTS = [
    "Downtown Office Tower",
]


@dataclass
class ProjectRecord:
    project_id: str
    name: str
    tenant_id: str
    database_id: str
    total_chunks: int
    created: str


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a_norm = a / np.linalg.norm(a, axis=1, keepdims=True)
    b_norm = b / np.linalg.norm(b, axis=1, keepdims=True)
    return np.dot(a_norm, b_norm.T)


def contradiction_scan(snapshot: RetrievalSnapshot) -> dict:
    embeddings = snapshot.embeddings
    chunks = snapshot.chunks
    if embeddings is None or len(chunks) < 2:
        return {"count": 0, "checked_pairs": 0, "issues": []}

    drawing_chunks = [(i, c) for i, c in enumerate(chunks) if c.get("doc_type") in ("drawing", "plan")]
    spec_chunks = [(i, c) for i, c in enumerate(chunks) if c.get("doc_type") in ("spec", "specification")]
    if not drawing_chunks or not spec_chunks:
        return {"count": 0, "checked_pairs": 0, "issues": []}

    spec_indices = [i for i, _ in spec_chunks]
    drawing_indices = [i for i, _ in drawing_chunks]
    spec_embs = embeddings[spec_indices]
    drawing_embs = embeddings[drawing_indices]
    sim_matrix = cosine_similarity(spec_embs, drawing_embs)

    issues = []
    for si, spec_idx in enumerate(spec_indices):
        best_di = int(np.argmax(sim_matrix[si]))
        best_score = float(sim_matrix[si][best_di])
        drawing_idx = drawing_indices[best_di]
        if best_score <= 0.5:
            continue

        spec_text = chunks[spec_idx]["text"]
        draw_text = chunks[drawing_idx]["text"]
        spec_dims = set(re.findall(r"\b(\d+(?:\.\d+)?)\s*(?:ft|inches|in)\b", spec_text))
        draw_dims = set(re.findall(r"\b(\d+(?:\.\d+)?)\s*(?:ft|inches|in)\b", draw_text))
        if spec_dims and draw_dims and spec_dims != draw_dims:
            issues.append(
                {
                    "severity": "medium",
                    "confidence": round(best_score, 3),
                    "spec_doc": chunks[spec_idx]["doc_name"],
                    "drawing_doc": chunks[drawing_idx]["doc_name"],
                    "issue": "Potential dimension mismatch between spec and drawing",
                }
            )

    return {
        "count": len(issues),
        "checked_pairs": len(spec_chunks) * len(drawing_chunks),
        "issues": issues[:10],
    }


def summarize_matches(matches, top_k: int = 5) -> dict:
    if not matches:
        return {
            "top_score": None,
            "top_docs": [],
            "top_hits": [],
        }

    hits = []
    for match in matches[:top_k]:
        chunk = match.chunk
        hits.append(
            {
                "doc_name": chunk["doc_name"],
                "doc_type": chunk.get("doc_type", "drawing"),
                "score": round(float(match.score), 4),
                "text": chunk["text"][:240],
            }
        )

    top_docs = list(dict.fromkeys(hit["doc_name"] for hit in hits))
    top_score = round(float(matches[0].score), 4) if matches else None
    return {
        "top_score": top_score,
        "top_docs": top_docs,
        "top_hits": hits,
    }


def load_projects() -> List[ProjectRecord]:
    projects = []
    for project_dir in PROJECTS_DIR.iterdir():
        if not project_dir.is_dir():
            continue
        meta_path = project_dir / "meta.json"
        index_path = project_dir / "index.json"
        if not meta_path.exists():
            continue
        meta = json.loads(meta_path.read_text())
        index = json.loads(index_path.read_text()) if index_path.exists() else {}
        projects.append(
            ProjectRecord(
                project_id=project_dir.name,
                name=meta.get("name", project_dir.name),
                tenant_id=meta.get("tenant_id", os.environ.get("RETRIEVAL_TENANT_ID", "local-dev")),
                database_id=meta.get("database_id", os.environ.get("RETRIEVAL_DATABASE_ID", "vdc-document-intelligence")),
                total_chunks=index.get("total_chunks", 0),
                created=meta.get("created", ""),
            )
        )
    return projects


def resolve_project(selector: str, projects: Sequence[ProjectRecord]) -> ProjectRecord:
    for project in projects:
        if project.project_id == selector:
            return project

    matches = [project for project in projects if project.name.lower() == selector.lower()]
    if not matches:
        raise KeyError(selector)

    matches.sort(key=lambda project: (project.total_chunks, project.created), reverse=True)
    return matches[0]


def scope_for(project: ProjectRecord) -> RetrievalScope:
    return RetrievalScope(
        tenant_id=project.tenant_id,
        database_id=project.database_id,
        project_id=project.project_id,
    )


@contextmanager
def temp_env(updates: Dict[str, str], removals: Iterable[str] = ()) -> Iterator[None]:
    keys = set(updates) | set(removals)
    old_values = {key: os.environ.get(key) for key in keys}
    try:
        for key in removals:
            os.environ.pop(key, None)
        for key, value in updates.items():
            os.environ[key] = value
        yield
    finally:
        for key, old_value in old_values.items():
            if old_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old_value


def instantiate_store(name: str):
    if name == "filesystem":
        return FilesystemRetrievalStore(projects_dir=PROJECTS_DIR, embeddings_dir=EMBEDDINGS_DIR)
    if name == "chroma":
        chroma_path = BENCH_DIR / "chroma"
        with temp_env(
            {"CHROMA_PATH": str(chroma_path)},
            removals=("CHROMA_HOST", "CHROMA_API_KEY", "CHROMA_HTTP_HEADERS_JSON"),
        ):
            return ChromaRetrievalStore(data_dir=DATA_DIR)
    if name == "pgvector":
        dsn = os.environ.get("PGVECTOR_DSN", "postgresql://medha:medha@127.0.0.1:5433/medha")
        with temp_env({"PGVECTOR_DSN": dsn, "PGVECTOR_AUTO_INIT": os.environ.get("PGVECTOR_AUTO_INIT", "true")}):
            return PgvectorRetrievalStore()
    raise ValueError(f"Unknown backend '{name}'")


def seed_backend(store, source_store, project: ProjectRecord) -> dict:
    if isinstance(store, FilesystemRetrievalStore):
        return {"seeded": False, "duration_ms": 0.0}

    scope = scope_for(project)
    source_snapshot = source_store.load_project(scope)
    started = time.perf_counter()
    store.save_project(scope, source_snapshot.embeddings, source_snapshot.chunks)
    elapsed_ms = (time.perf_counter() - started) * 1000
    return {"seeded": True, "duration_ms": round(elapsed_ms, 2)}


def benchmark_backend(
    backend_name: str,
    store,
    source_store,
    projects_by_selector: Dict[str, ProjectRecord],
    model: SentenceTransformer,
) -> dict:
    project_scope_cache = {}
    project_snapshot_cache = {}
    seeding = {}

    unique_projects = {record.project_id: record for record in projects_by_selector.values()}

    for project in unique_projects.values():
        seeding[project.project_id] = seed_backend(store, source_store, project)

    load_latencies = []
    query_latencies = []
    contradiction_latencies = []
    query_results = []
    contradiction_results = []

    for project in unique_projects.values():
        scope = project_scope_cache.setdefault(project.project_id, scope_for(project))
        load_started = time.perf_counter()
        snapshot = store.load_project(scope)
        load_ms = (time.perf_counter() - load_started) * 1000
        load_latencies.append(load_ms)
        project_snapshot_cache[project.project_id] = snapshot

    baseline_contradictions = {}
    for selector in CONTRADICTION_PROJECTS:
        project = projects_by_selector[selector]
        baseline_snapshot = source_store.load_project(scope_for(project))
        baseline_contradictions[project.project_id] = contradiction_scan(baseline_snapshot)

    for case in QUERY_CASES:
        project = projects_by_selector[case["project"]]
        scope = project_scope_cache.setdefault(project.project_id, scope_for(project))

        query_embedding = model.encode([case["query"]], show_progress_bar=False)[0]
        query_started = time.perf_counter()
        result = summarize_matches(
            store.search_project(scope, query_embedding=query_embedding, top_k=5),
            top_k=5,
        )
        query_ms = (time.perf_counter() - query_started) * 1000
        query_latencies.append(query_ms)

        hits_expected_doc = case["expected_doc"] in result["top_docs"]
        hits_expected_text = any(case["expected_snippet"].lower() in hit["text"].lower() for hit in result["top_hits"])
        query_results.append(
            {
                **case,
                "project_id": project.project_id,
                "query_ms": round(query_ms, 2),
                "top_score": result["top_score"],
                "top_docs": result["top_docs"],
                "hits_expected_doc": hits_expected_doc,
                "hits_expected_snippet": hits_expected_text,
            }
        )

    for selector in CONTRADICTION_PROJECTS:
        project = projects_by_selector[selector]
        scope = project_scope_cache.setdefault(project.project_id, scope_for(project))
        snapshot = project_snapshot_cache.get(project.project_id)
        if snapshot is None:
            snapshot = store.load_project(scope)
            project_snapshot_cache[project.project_id] = snapshot

        started = time.perf_counter()
        result = contradiction_scan(snapshot)
        contradiction_ms = (time.perf_counter() - started) * 1000
        contradiction_latencies.append(contradiction_ms)

        baseline = baseline_contradictions[project.project_id]
        contradiction_results.append(
            {
                "project": selector,
                "project_id": project.project_id,
                "contradiction_ms": round(contradiction_ms, 2),
                "count": result["count"],
                "checked_pairs": result["checked_pairs"],
                "matches_filesystem_count": result["count"] == baseline["count"],
            }
        )

    return {
        "backend": backend_name,
        "seeding": seeding,
        "summary": {
            "avg_load_ms": round(statistics.mean(load_latencies), 2) if load_latencies else 0.0,
            "avg_query_ms": round(statistics.mean(query_latencies), 2) if query_latencies else 0.0,
            "avg_contradiction_ms": round(statistics.mean(contradiction_latencies), 2) if contradiction_latencies else 0.0,
            "query_doc_hits": sum(1 for item in query_results if item["hits_expected_doc"]),
            "query_snippet_hits": sum(1 for item in query_results if item["hits_expected_snippet"]),
            "query_case_count": len(query_results),
            "contradiction_match_count": sum(1 for item in contradiction_results if item["matches_filesystem_count"]),
            "contradiction_case_count": len(contradiction_results),
        },
        "queries": query_results,
        "contradictions": contradiction_results,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark Medha retrieval backends.")
    parser.add_argument(
        "--backends",
        nargs="+",
        default=["filesystem", "chroma", "pgvector"],
        choices=["filesystem", "chroma", "pgvector"],
        help="Backends to benchmark.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="SentenceTransformer model used to encode benchmark queries.",
    )
    parser.add_argument(
        "--report-path",
        default=str(DEFAULT_REPORT),
        help="Where to write the JSON benchmark report.",
    )
    parser.add_argument(
        "--allow-model-download",
        action="store_true",
        default=ALLOW_MODEL_DOWNLOAD,
        help="Allow Hugging Face model download if the embedding model is not already cached locally.",
    )
    return parser.parse_args()


def load_embedding_model(model_name: str, allow_download: bool) -> SentenceTransformer:
    try:
        return SentenceTransformer(model_name, local_files_only=not allow_download)
    except Exception as exc:
        if allow_download:
            raise
        raise RuntimeError(
            f"Embedding model '{model_name}' could not be loaded from local cache. "
            "Either pre-cache the model or rerun with --allow-model-download."
        ) from exc


def main() -> int:
    args = parse_args()
    projects = load_projects()
    projects_by_selector: Dict[str, ProjectRecord] = {}

    try:
        for case in QUERY_CASES:
            projects_by_selector[case["project"]] = resolve_project(case["project"], projects)
        for selector in CONTRADICTION_PROJECTS:
            projects_by_selector[selector] = resolve_project(selector, projects)
    except KeyError as exc:
        print(
            f"Required benchmark project '{exc.args[0]}' was not found. "
            "Seed the demo data first or create a matching project.",
            file=sys.stderr,
        )
        return 1

    print("=" * 68)
    print("Medha Retrieval Backend Benchmark")
    print(f"Started: {datetime.now().isoformat()}")
    print(f"Backends: {', '.join(args.backends)}")
    print("=" * 68)

    print(
        f"Loading embedding model: {args.model}"
        f"{' (download allowed)' if args.allow_model_download else ' (offline cache only)'}"
    )
    model = load_embedding_model(args.model, allow_download=args.allow_model_download)
    source_store = FilesystemRetrievalStore(projects_dir=PROJECTS_DIR, embeddings_dir=EMBEDDINGS_DIR)

    report = {
        "timestamp": datetime.now().isoformat(),
        "model": args.model,
        "backends": [],
    }

    for backend_name in args.backends:
        print(f"\n[{backend_name}]")
        try:
            store = instantiate_store(backend_name)
            backend_report = benchmark_backend(
                backend_name=backend_name,
                store=store,
                source_store=source_store,
                projects_by_selector=projects_by_selector,
                model=model,
            )
            report["backends"].append(backend_report)
            summary = backend_report["summary"]
            print(
                f"  avg load {summary['avg_load_ms']} ms | "
                f"avg query {summary['avg_query_ms']} ms | "
                f"avg contradiction {summary['avg_contradiction_ms']} ms"
            )
            print(
                f"  query doc hits {summary['query_doc_hits']}/{summary['query_case_count']} | "
                f"contradiction matches {summary['contradiction_match_count']}/{summary['contradiction_case_count']}"
            )
        except Exception as exc:
            print(f"  FAILED: {exc}")
            report["backends"].append(
                {
                    "backend": backend_name,
                    "error": str(exc),
                }
            )

    report_path = Path(args.report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2))
    print(f"\nReport saved to {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
