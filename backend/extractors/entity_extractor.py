import json
import re
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class Entity:
    id: str
    doc_id: str
    chunk_id: str
    text: str
    entity_type: str  # material, property, constraint, action, reference
    value: str
    unit: str
    confidence: float


def extract_entities(chunk_text: str, chunk_id: str, doc_id: str,
                     llm_generate_fn) -> List[Entity]:
    """Extract construction-specific entities from a text chunk using LLM."""

    prompt = f"""Extract all construction-specific entities from this text.

For each entity, identify:
- entity_type: material | property | constraint | action | reference
- text: the exact phrase from the text
- value: the numeric or categorical value (if any)
- unit: the unit of measurement (if any)

Focus on: concrete strength, rebar specs, dimensions, fire ratings, code references.

Return as JSON array:
[{{"entity_type": "material", "text": "3500 psi concrete", "value": "3500", "unit": "psi"}}]

Text:
{chunk_text}
"""

    response = llm_generate_fn(prompt, max_new_tokens=300)

    try:
        parsed = json.loads(response)
    except Exception:
        # Fallback: try to extract JSON from markdown
        match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group(1))
            except Exception:
                return []
        else:
            # Try to find any JSON array in the response
            match = re.search(r'\[.*\]', response, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group(0))
                except Exception:
                    return []
            else:
                return []

    if not isinstance(parsed, list):
        return []

    entities = []
    for i, item in enumerate(parsed):
        if not isinstance(item, dict):
            continue
        entities.append(Entity(
            id=f"{chunk_id}_ent_{i}",
            doc_id=doc_id,
            chunk_id=chunk_id,
            text=item.get("text", ""),
            entity_type=item.get("entity_type", "unknown"),
            value=str(item.get("value", "")),
            unit=item.get("unit", ""),
            confidence=0.85  # LLM-based, reasonably high
        ))

    return entities
