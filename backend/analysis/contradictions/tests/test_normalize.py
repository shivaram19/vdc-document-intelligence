"""Tests for contradiction-detection normalization helpers."""
import pytest

from analysis.contradictions._normalize import (
    canonicalize_unit,
    parse_numeric_value,
    parse_standard,
    values_conflict,
)


class TestCanonicalizeUnit:
    def test_common_units(self):
        assert canonicalize_unit("feet") == "ft"
        assert canonicalize_unit("ft") == "ft"
        assert canonicalize_unit("'") == "ft"
        assert canonicalize_unit("inches") == "in"
        assert canonicalize_unit('"') == "in"
        assert canonicalize_unit("psig") == "psi"

    def test_unknown_unit_lowercased(self):
        assert canonicalize_unit("Widgets") == "widgets"

    def test_empty_unit(self):
        assert canonicalize_unit("") == ""


class TestParseNumericValue:
    def test_scalar(self):
        assert parse_numeric_value("12") == 12.0

    def test_decimal(self):
        assert parse_numeric_value("0.30") == 0.30

    def test_comma(self):
        assert parse_numeric_value("1,800") == 1800.0

    def test_range(self):
        assert parse_numeric_value("18-24") == (18.0, 24.0)

    def test_invalid_returns_none(self):
        assert parse_numeric_value("galvanized steel") is None
        assert parse_numeric_value("") is None


class TestValuesConflict:
    def test_identical_no_conflict(self):
        assert values_conflict(10.0, 10.0) is False

    def test_different_conflict(self):
        assert values_conflict(10.0, 12.0) is True

    def test_within_relative_tolerance_no_conflict(self):
        # 5% relative tolerance; 10 vs 10.4 differs by 4%.
        assert values_conflict(10.0, 10.4) is False

    def test_outside_relative_tolerance_conflict(self):
        assert values_conflict(10.0, 12.0, relative_tolerance=0.05) is True

    def test_absolute_tolerance_used_when_larger(self):
        assert values_conflict(10.0, 10.4, absolute_tolerance=1.0) is False
        assert values_conflict(10.0, 12.0, absolute_tolerance=1.0) is True

    def test_overlapping_intervals_no_conflict(self):
        assert values_conflict((10.0, 12.0), (11.0, 13.0)) is False

    def test_disjoint_intervals_conflict(self):
        assert values_conflict((10.0, 11.0), (12.0, 13.0)) is True

    def test_scalar_and_interval_overlap(self):
        assert values_conflict(11.5, (10.0, 12.0)) is False

    def test_scalar_and_interval_disjoint(self):
        assert values_conflict(15.0, (10.0, 12.0)) is True


class TestParseStandard:
    def test_org_only(self):
        org, year = parse_standard("NFPA 13")
        assert org == "NFPA"
        assert year is None

    def test_org_and_year(self):
        org, year = parse_standard("ASTM E119-2022")
        assert org == "ASTM"
        assert year == "2022"

    def test_lowercase_input(self):
        org, year = parse_standard("nfpa 2019")
        assert org == "NFPA"
        assert year == "2019"

    def test_year_at_end(self):
        org, year = parse_standard("IBC 2021")
        assert org == "IBC"
        assert year == "2021"
