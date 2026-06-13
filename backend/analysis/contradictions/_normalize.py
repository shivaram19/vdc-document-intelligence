"""Normalization helpers for comparator inputs."""
import re
from typing import Optional, Tuple, Union

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

NumericValue = Union[float, Tuple[float, float]]


def canonicalize_unit(unit: str) -> str:
    return UNIT_CANONICAL.get(unit.lower().strip(), unit.lower().strip())


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
    # Convert intervals to a representative distance check.
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
    # Look for a 4-digit year at the end or embedded in the value.
    year_match = re.search(r"\b(19|20)\d{2}\b", value)
    year = year_match.group(0) if year_match else None
    # Organization is the leading alphabetic token.
    org_match = re.match(r"^([A-Za-z]+)", value)
    org = org_match.group(1).upper() if org_match else value.upper()
    return org, year
