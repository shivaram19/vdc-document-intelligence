"""Attribute and tolerance registries for deterministic comparators."""
from typing import Dict, List

# Attributes whose values are numeric after extraction.
NUMERIC_ATTRIBUTES = {
    "ceiling height",
    "U-factor",
    "R-value",
    "duct velocity",
    "pressure",
    "density",
    "spacing",
}

# Per-attribute tolerance: (absolute, relative).
NUMERIC_TOLERANCE: Dict[str, tuple] = {
    "ceiling height": (0.0, 0.05),
    "U-factor": (0.0, 0.05),
    "R-value": (0.0, 0.05),
    "duct velocity": (0.0, 0.10),
    "pressure": (0.0, 0.10),
    "density": (0.0, 0.10),
    "spacing": (0.0, 0.05),
}

# Material attributes and a small synonym dictionary.
MATERIAL_ATTRIBUTES = {
    "duct material",
    "floor finish",
    "fire rating",
    "valve type",
}

# Expected attributes for known entities; drives missing-attribute detection.
EXPECTED_ATTRIBUTES: Dict[str, List[str]] = {
    "exterior wall": ["R-value"],
    "window": ["U-factor"],
    "ductwork": ["duct material", "seal class"],
    "fire rated assembly": ["fire rating"],
}
