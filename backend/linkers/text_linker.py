from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Tuple
from extractors.entity_extractor import Entity


class TextLinker:
    def __init__(self):
        self.embedder = SentenceTransformer("all-mpnet-base-v2")

    def find_links(self, spec_entities: List[Entity],
                   drawing_entities: List[Entity],
                   threshold: float = 0.65) -> List[Tuple[Entity, Entity, float]]:
        """Link spec entities to drawing entities by text similarity."""

        if not spec_entities or not drawing_entities:
            return []

        spec_texts = [e.text for e in spec_entities]
        draw_texts = [e.text for e in drawing_entities]

        spec_embeddings = self.embedder.encode(spec_texts)
        draw_embeddings = self.embedder.encode(draw_texts)

        # Normalize
        spec_embeddings = spec_embeddings / np.linalg.norm(spec_embeddings, axis=1, keepdims=True)
        draw_embeddings = draw_embeddings / np.linalg.norm(draw_embeddings, axis=1, keepdims=True)

        # Compute similarity matrix
        similarity_matrix = np.dot(spec_embeddings, draw_embeddings.T)

        links = []
        for i, spec_e in enumerate(spec_entities):
            best_idx = np.argmax(similarity_matrix[i])
            best_score = similarity_matrix[i][best_idx]

            if best_score >= threshold:
                links.append((spec_e, drawing_entities[best_idx], float(best_score)))

        return links
