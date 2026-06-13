"""Normalization helpers for comparator inputs."""
import re
from typing import Dict, List, Optional, Tuple, Union

# Canonical surface-form units. Keep in sync with the claim-extraction pipeline.
UNIT_CANONICAL = {
    "feet": "ft",
    "ft": "ft",
    "'": "ft",
    "fpm": "fpm",
    "psi": "psi",
    "psig": "psi",
    "gpm/sf": "gpm/sf",
    "inches": "in",
    "in": "in",
    '"': "in",
    "sf": "sf",
}

# (base_unit, factor_to_base) for unit conversion before numeric comparison.
UNIT_BASE: Dict[str, Tuple[str, float]] = {
    "ft": ("ft", 1.0),
    "in": ("ft", 1.0 / 12.0),
    "fpm": ("fpm", 1.0),
    "psi": ("psi", 1.0),
    "gpm/sf": ("gpm/sf", 1.0),
    "sf": ("sf", 1.0),
}

# Material synonyms used to collapse surface forms to a canonical term.
MATERIAL_SYNONYMS: Dict[str, List[str]] = {
    "galvanized steel": ["galvanized steel"],
    "aluminum": ["aluminum", "aluminium"],
    "carbon steel": ["carbon steel", "black steel"],
    "stainless steel": ["stainless steel"],
    "copper": ["copper"],
    "polished concrete": ["polished concrete"],
    "carpet tile": ["carpet tile"],
    "luxury vinyl tile": ["luxury vinyl tile", "lvt"],
    "terrazzo": ["terrazzo"],
    "ball valve": ["ball valve"],
    "butterfly valve": ["butterfly valve"],
    "2-hour": ["2-hour", "2 hour"],
    "1-hour": ["1-hour", "1 hour"],
}

NumericValue = Union[float, Tuple[float, float]]


def canonicalize_unit(unit: str) -> str:
    """Return the canonical unit for a surface-form unit string."""
    return UNIT_CANONICAL.get(unit.lower().strip(), unit.lower().strip())


def to_base_value(value: NumericValue, unit: str) -> Optional[Tuple[NumericValue, str]]:
    """Convert a numeric value to its base unit, if a conversion is known."""
    canonical = canonicalize_unit(unit)
    mapping = UNIT_BASE.get(canonical)
    if mapping is None:
        return None
    base_unit, factor = mapping
    if isinstance(value, tuple):
        return (value[0] * factor, value[1] * factor), base_unit
    return value * factor, base_unit


def parse_numeric_value(value: str) -> Optional[NumericValue]:
    """Parse a numeric value or a hyphen range."""
    cleaned = re.sub(r",", "", value.strip())
    if "-" in cleaned:
        parts = cleaned.split("-")
        if len(parts) == 2:
            try:
                return (float(parts[0]), float(parts[1]))
            except ValueError:
                return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def values_conflict(
    a: NumericValue,
    b: NumericValue,
    absolute_tolerance: float = 0.0,
    relative_tolerance: float = 0.05,
) -> bool:
    """Return True if two numeric values are outside the combined tolerance."""

    def mid_and_radius(v: NumericValue) -> Tuple[float, float]:
        if isinstance(v, tuple):
            low, high = v
            return ((low + high) / 2.0), ((high - low) / 2.0)
        return float(v), 0.0

    mid_a, rad_a = mid_and_radius(a)
    mid_b, rad_b = mid_and_radius(b)
    distance = abs(mid_a - mid_b)
    combined_radius = rad_a + rad_b
    threshold = max(
        absolute_tolerance,
        relative_tolerance * max(abs(mid_a), abs(mid_b), 1e-9),
    )
    return distance > threshold + combined_radius


def parse_standard(value: str) -> Tuple[str, Optional[str]]:
    """Extract organization and optional year from a standard citation."""
    year_match = re.search(r"\b(19|20)\d{2}\b", value)
    year = year_match.group(0) if year_match else None
    org_match = re.match(r"^([A-Za-z]+)", value)
    org = org_match.group(1).upper() if org_match else value.upper()
    return org, year


def _build_material_reverse_map() -> Dict[str, str]:
    reverse: Dict[str, str] = {}
    for canonical, variants in MATERIAL_SYNONYMS.items():
        for variant in variants:
            reverse[variant.lower()] = canonical
    return reverse


_MATERIAL_CANONICAL = _build_material_reverse_map()


def canonicalize_material(value: str) -> str:
    """Collapse a material surface form to its canonical term."""
    key = value.lower().strip()
    return _MATERIAL_CANONICAL.get(key, key)
