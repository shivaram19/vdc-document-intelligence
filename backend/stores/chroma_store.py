import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import uuid


class ChromaStore:
    def __init__(self, persist_dir: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.embedder = SentenceTransformer("all-mpnet-base-v2")

    def _collection_name(self, project_id: str) -> str:
        return f"project_{project_id}"

    def add_chunks(self, project_id: str, doc_id: str, doc_type: str,
                   doc_name: str, chunks: List[str]) -> List[str]:
        collection = self.client.get_or_create_collection(
            name=self._collection_name(project_id)
        )

        chunk_ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
        embeddings = self.embedder.encode(chunks).tolist()
        metadatas = [
            {
                "doc_id": doc_id,
                "doc_type": doc_type,
                "doc_name": doc_name,
                "chunk_index": i,
            }
            for i in range(len(chunks))
        ]

        collection.add(
            ids=chunk_ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )
        return chunk_ids

    def search(self, project_id: str, query: str, n_results: int = 10,
               doc_type: Optional[str] = None) -> List[Dict]:
        collection = self.client.get_collection(
            name=self._collection_name(project_id)
        )
        query_embedding = self.embedder.encode([query]).tolist()[0]

        where_filter = {"doc_type": doc_type} if doc_type else None

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_filter
        )

        output = []
        for i in range(len(results["ids"][0])):
            output.append({
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
            })
        return output

    def delete_document(self, project_id: str, doc_id: str):
        collection = self.client.get_collection(
            name=self._collection_name(project_id)
        )
        results = collection.get(where={"doc_id": doc_id})
        if results["ids"]:
            collection.delete(ids=results["ids"])

    def count(self, project_id: str) -> int:
        try:
            collection = self.client.get_collection(
                name=self._collection_name(project_id)
            )
            return collection.count()
        except Exception:
            return 0
