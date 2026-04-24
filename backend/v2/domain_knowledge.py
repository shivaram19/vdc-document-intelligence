"""
Medha v2 Phase 2: Domain Knowledge Engine

Encodes tacit construction domain knowledge:
- Trade-specific checklists (HVAC, structural, electrical, plumbing, fire, architectural)
- Code standard minimums (IBC, ASHRAE, ACI, NFPA)
- Anomaly detection rules
- Standard sizes and typical values

Usage:
    engine = DomainKnowledgeEngine()
    issues = engine.check_document(text, doc_type="hvac")
    anomalies = engine.detect_anomalies(text)
    code_check = engine.check_code_compliance(text, climate_zone="5")
"""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any


@dataclass
class ChecklistIssue:
    """A checklist item that may be missing or non-compliant."""
    checklist_id: str
    trade: str
    category: str
    description: str
    severity: str  # 'critical', 'medium', 'low'
    status: str = "unchecked"  # 'pass', 'fail', 'missing', 'unchecked'
    evidence: str = ""  # Text from document that triggered this
    recommendation: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.checklist_id,
            "trade": self.trade,
            "category": self.category,
            "description": self.description,
            "severity": self.severity,
            "status": self.status,
            "evidence": self.evidence,
            "recommendation": self.recommendation,
        }


@dataclass
class Anomaly:
    """A detected anomaly — something unusual that may indicate an error."""
    anomaly_type: str
    description: str
    severity: str
    confidence: float
    location: str = ""  # Where in the document it was found
    expected_value: str = ""
    actual_value: str = ""
    rule_triggered: str = ""

    def to_dict(self) -> dict:
        return {
            "type": self.anomaly_type,
            "description": self.description,
            "severity": self.severity,
            "confidence": self.confidence,
            "location": self.location,
            "expected": self.expected_value,
            "actual": self.actual_value,
            "rule": self.rule_triggered,
        }


@dataclass
class CodeViolation:
    """A potential code compliance issue."""
    code: str  # 'IBC', 'ASHRAE 90.1', 'ACI 318', etc.
    section: str
    requirement: str
    found_value: str
    required_value: str
    severity: str

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "section": self.section,
            "requirement": self.requirement,
            "found": self.found_value,
            "required": self.required_value,
            "severity": self.severity,
        }


# =============================================================================
# DOMAIN KNOWLEDGE ENGINE
# =============================================================================

class DomainKnowledgeEngine:
    """Construction domain knowledge engine for anomaly detection and compliance checking."""

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path(__file__).parent
        self.checklists: Dict[str, dict] = {}
        self.code_standards: Dict[str, dict] = {}
        self.standard_sizes: Dict[str, Any] = {}
        self.anomaly_rules: List[dict] = []

        self._load_checklists()
        self._load_code_standards()
        self._load_anomaly_rules()

    def _load_checklists(self):
        """Load all trade-specific checklists from JSON files."""
        checklist_dir = self.data_dir / "checklists"
        if not checklist_dir.exists():
            return
        for path in checklist_dir.glob("*.json"):
            try:
                data = json.loads(path.read_text())
                self.checklists[data.get("trade", path.stem).lower()] = data
            except Exception as e:
                print(f"Failed to load checklist {path}: {e}")

    def _load_code_standards(self):
        """Load code standard databases."""
        code_dir = self.data_dir / "code_standards"
        if not code_dir.exists():
            return
        for path in code_dir.glob("*.json"):
            try:
                data = json.loads(path.read_text())
                self.code_standards[data.get("standard", path.stem)] = data
            except Exception as e:
                print(f"Failed to load code standard {path}: {e}")

    def _load_anomaly_rules(self):
        """Load hard-coded anomaly detection heuristics."""
        self.anomaly_rules = [
            {
                "name": "column_spacing_too_wide",
                "pattern": r'(\d{2,3})\s*["\u201d\']?\s*(?:ft|feet|\'-0")?\s*(?:OC|o\.c\.|on center)',
                "condition": lambda m: int(m.group(1)) > 30,
                "severity": "medium",
                "message": "Column spacing > 30' may require intermediate beams. Verify with structural engineer.",
                "category": "structural",
            },
            {
                "name": "window_u_factor_high",
                "pattern": r'[Uu][\s\-]?factor\s*[:\s]*\s*(0\.\d{2,3})',
                "condition": lambda m: float(m.group(1)) > 0.35,
                "severity": "critical",
                "message": "Window U-factor exceeds typical energy code maximum (0.35). Verify climate zone requirements.",
                "category": "envelope",
            },
            {
                "name": "mech_room_ceiling_low",
                "pattern": r'(?:mechanical room|mech room|equipment room).*?(\d{1,2})\s*(?:ft|feet|\'-0")',
                "condition": lambda m: int(m.group(1)) < 10,
                "severity": "critical",
                "message": "Mechanical room ceiling < 10' may not accommodate equipment. Verify clearances.",
                "category": "hvac",
            },
            {
                "name": "wall_r_value_low",
                "pattern": r'(?:wall\s*)?[Rr][\s\-]?value\s*[:\s]*\s*(?:[Rr][\s\-]?)?(\d{1,2})',
                "condition": lambda m: int(m.group(1)) < 13,
                "severity": "critical",
                "message": "Wall R-value below minimum code requirement (R-13). Verify climate zone.",
                "category": "envelope",
            },
            {
                "name": "roof_r_value_low",
                "pattern": r'(?:roof\s*)?[Rr][\s\-]?value\s*[:\s]*\s*(?:[Rr][\s\-]?)?(\d{1,2})',
                "condition": lambda m: int(m.group(1)) < 20,
                "severity": "critical",
                "message": "Roof R-value below minimum code requirement (R-20). Verify climate zone.",
                "category": "envelope",
            },
            {
                "name": "concrete_strength_low",
                "pattern": r'(\d{1,2}),?000?\s*(?:psi|PSI)',
                "condition": lambda m: int(m.group(1)) < 3,
                "severity": "medium",
                "message": "Concrete strength below 3,000 psi may not meet structural requirements. Verify with engineer.",
                "category": "structural",
            },
            {
                "name": "fire_rating_missing",
                "pattern": r'(?:shaft|corridor|stair|exit).*?(\d)[\s\-]?(?:hour|hr)',
                "condition": lambda m: False,  # Just flag presence for verification
                "severity": "info",
                "message": "Fire-rated assembly identified. Verify rating matches occupancy and code requirements.",
                "category": "fire_safety",
            },
            {
                "name": "door_width_narrow",
                "pattern": r'(?:door|opening)\s*(?:width)?\s*[:\s]*\s*(\d{1,2})\s*(?:in|inches|"|\u201d)',
                "condition": lambda m: int(m.group(1)) < 32,
                "severity": "critical",
                "message": "Door width < 32\" may not meet ADA/IBC minimum clear width requirement.",
                "category": "accessibility",
            },
            {
                "name": "rebar_cover_low",
                "pattern": r'(?:concrete cover|rebar cover|cover)\s*[:\s]*\s*(\d\.?\d*)\s*(?:in|inches|"|\u201d)',
                "condition": lambda m: float(m.group(1)) < 1.5,
                "severity": "critical",
                "message": "Rebar cover < 1.5\" may not meet ACI 318 minimum for cast-in-place concrete.",
                "category": "structural",
            },
        ]

    # -------------------------------------------------------------------------
    # CHECKLIST VERIFICATION
    # -------------------------------------------------------------------------

    def check_document(self, text: str, trade: Optional[str] = None) -> List[ChecklistIssue]:
        """
        Run trade-specific checklists against document text.

        Args:
            text: Document text content
            trade: Specific trade to check (hvac, structural, fire_protection, architectural)
                   If None, runs all checklists.

        Returns:
            List of ChecklistIssue items with pass/fail/missing status
        """
        results = []
        trades_to_check = [trade] if trade else list(self.checklists.keys())

        for t in trades_to_check:
            checklist = self.checklists.get(t.lower())
            if not checklist:
                continue

            for item in checklist.get("items", []):
                issue = self._evaluate_checklist_item(text, item, checklist.get("trade", t))
                results.append(issue)

        return results

    def _evaluate_checklist_item(self, text: str, item: dict, trade: str) -> ChecklistIssue:
        """Evaluate a single checklist item against document text."""
        check_text = item.get("check", "")
        keywords = self._extract_keywords(check_text)

        # Simple keyword-based presence detection
        text_lower = text.lower()
        found_keywords = [kw for kw in keywords if kw in text_lower]
        coverage = len(found_keywords) / max(len(keywords), 1)

        if coverage >= 0.5:
            status = "pass"
            evidence = f"Found keywords: {', '.join(found_keywords[:3])}"
        elif coverage > 0:
            status = "partial"
            evidence = f"Partial match: {', '.join(found_keywords)}"
        else:
            status = "missing"
            evidence = "No relevant keywords found"

        return ChecklistIssue(
            checklist_id=item.get("id", ""),
            trade=trade,
            category=item.get("category", ""),
            description=check_text,
            severity=item.get("severity", "medium"),
            status=status,
            evidence=evidence,
            recommendation="Verify with design team" if status == "missing" else "",
        )

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract significant keywords from a checklist description."""
        # Remove common stop words and extract nouns/adjectives
        stop_words = {"the", "a", "an", "and", "or", "for", "to", "of", "in", "on", "at", "by", "with", "per", "all", "shall", "be", "is", "are", "specified", "defined", "provided", "required", "listed", "noted", "shown"}
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        return [w for w in words if w not in stop_words][:8]

    # -------------------------------------------------------------------------
    # ANOMALY DETECTION
    # -------------------------------------------------------------------------

    def detect_anomalies(self, text: str) -> List[Anomaly]:
        """
        Run anomaly detection heuristics against document text.

        Returns:
            List of detected anomalies with severity and confidence.
        """
        anomalies = []
        text_lower = text.lower()

        for rule in self.anomaly_rules:
            for match in re.finditer(rule["pattern"], text, re.IGNORECASE):
                try:
                    if rule["condition"](match):
                        anomalies.append(Anomaly(
                            anomaly_type=rule["category"],
                            description=rule["message"],
                            severity=rule["severity"],
                            confidence=0.85,
                            location=match.group(0),
                            actual_value=match.group(1) if match.lastindex else "",
                            rule_triggered=rule["name"],
                        ))
                except Exception:
                    continue

        # Additional contextual anomalies
        anomalies.extend(self._check_contextual_anomalies(text))

        return anomalies

    def _check_contextual_anomalies(self, text: str) -> List[Anomaly]:
        """Check for anomalies that require cross-document or contextual analysis."""
        anomalies = []
        text_lower = text.lower()

        # Check for missing fire damper references when shafts are mentioned
        if "shaft" in text_lower and "fire damper" not in text_lower and "damper" not in text_lower:
            anomalies.append(Anomaly(
                anomaly_type="fire_safety",
                description="Shaft penetrations mentioned but no fire damper locations specified.",
                severity="critical",
                confidence=0.75,
                rule_triggered="missing_fire_dampers",
            ))

        # Check for energy recovery in climate zones where it might be required
        if "economizer" in text_lower and "erv" not in text_lower and "energy recovery" not in text_lower:
            anomalies.append(Anomaly(
                anomaly_type="hvac",
                description="Economizer specified but no energy recovery ventilator mentioned. Verify if ERV is required per ASHRAE 90.1.",
                severity="medium",
                confidence=0.6,
                rule_triggered="erv_not_specified",
            ))

        return anomalies

    # -------------------------------------------------------------------------
    # CODE COMPLIANCE CHECKING
    # -------------------------------------------------------------------------

    def check_code_compliance(self, text: str, climate_zone: str = "5") -> List[CodeViolation]:
        """
        Check document text against known code minimums.

        Args:
            text: Document text
            climate_zone: IECC climate zone (1-8)

        Returns:
            List of potential code violations
        """
        violations = []
        text_lower = text.lower()

        # Building envelope checks
        envelope = self.code_standards.get("Building Envelope Code Minimums")
        if envelope:
            cz_data = envelope.get("climate_zones", {}).get(climate_zone, {})

            # Window U-factor check
            for match in re.finditer(r'[Uu][\s\-]?factor\s*[:\s]*\s*(0\.\d{2,3})', text):
                val = float(match.group(1))
                max_u = cz_data.get("window_u", 0.30)
                if val > max_u:
                    violations.append(CodeViolation(
                        code="IECC",
                        section=f"Climate Zone {climate_zone}",
                        requirement=f"Window U-factor ≤ {max_u}",
                        found_value=str(val),
                        required_value=str(max_u),
                        severity="critical",
                    ))

            # Wall R-value check
            for match in re.finditer(r'(?:wall\s*)?[Rr][\s\-]?value\s*[:\s]*\s*(?:[Rr][\s\-]?)?(\d{1,2})', text):
                val = int(match.group(1))
                min_r = cz_data.get("wall_r", 20)
                if val < min_r:
                    violations.append(CodeViolation(
                        code="IECC",
                        section=f"Climate Zone {climate_zone}",
                        requirement=f"Wall R-value ≥ {min_r}",
                        found_value=str(val),
                        required_value=str(min_r),
                        severity="critical",
                    ))

            # Roof R-value check
            for match in re.finditer(r'(?:roof\s*)?[Rr][\s\-]?value\s*[:\s]*\s*(?:[Rr][\s\-]?)?(\d{1,2})', text):
                val = int(match.group(1))
                min_r = cz_data.get("roof_r", 38)
                if val < min_r:
                    violations.append(CodeViolation(
                        code="IECC",
                        section=f"Climate Zone {climate_zone}",
                        requirement=f"Roof R-value ≥ {min_r}",
                        found_value=str(val),
                        required_value=str(min_r),
                        severity="critical",
                    ))

        # Fire-rated assembly checks
        fire_std = self.code_standards.get("Fire-Rated Assembly Requirements")
        if fire_std:
            for assembly in fire_std.get("assemblies", []):
                asm_type = assembly["type"].lower()
                required_rating = assembly["rating"]
                ibc_ref = assembly["ibc_reference"]

                # Look for mention of this assembly type
                if asm_type in text_lower:
                    # Check if rating is mentioned
                    rating_pattern = rf'{re.escape(asm_type)}.*?([\d.]+)[\s\-]?(?:hour|hr)'
                    found_ratings = re.findall(rating_pattern, text_lower)
                    if found_ratings:
                        for found in found_ratings:
                            req_hours = float(required_rating.replace("-hour", "").replace("hour", ""))
                            found_hours = float(found)
                            if found_hours < req_hours:
                                violations.append(CodeViolation(
                                    code="IBC",
                                    section=ibc_ref,
                                    requirement=f"{assembly['type']} requires {required_rating} rating",
                                    found_value=f"{found_hours}-hour",
                                    required_value=required_rating,
                                    severity="critical",
                                ))

        return violations

    # -------------------------------------------------------------------------
    # STANDARD SIZES LOOKUP
    # -------------------------------------------------------------------------

    def get_standard_sizes(self, category: str) -> Optional[dict]:
        """Get standard sizes for a component category."""
        standards = {
            "door_widths": {
                "standard": ["24\"", "28\"", "30\"", "32\"", "36\""],
                "ada_minimum": "32\" clear",
                "typical_office": "36\"",
            },
            "ceiling_heights": {
                "office": "9' AFF",
                "corridor": "8' AFF",
                "mechanical_room": "12' minimum clear",
                "lobby": "12-18'",
            },
            "column_spacing": {
                "typical_office": "20'-30'",
                "parking": "18'-24'",
                "wide_span": "30'-40' (requires deeper beams)",
            },
            "window_rough_openings": {
                "typical_office": "Width + 2\", Height + 2\"",
                "block_frame": "Width + 1\", Height + 0.5\"",
            },
            "concrete_slabs": {
                "office_building": "4\"-6\"",
                "parking_garage": "5\"-7\"",
                "warehouse": "6\"-8\"",
            },
        }
        return standards.get(category)

    def validate_dimension(self, value: float, unit: str, category: str) -> Optional[str]:
        """
        Validate if a dimension is within standard ranges.

        Returns:
            Warning message if outside typical range, None if OK.
        """
        warnings = {
            "door_width": {
                "min": 32, "unit": "in",
                "msg": "Door width {val}{unit} is below ADA minimum of 32\" clear.",
            },
            "ceiling_height": {
                "min": 8, "max": 20, "unit": "ft",
                "msg_low": "Ceiling height {val}{unit} is unusually low for commercial construction.",
                "msg_high": "Ceiling height {val}{unit} is unusually high — verify structural depth.",
            },
            "mech_room_height": {
                "min": 10, "unit": "ft",
                "msg": "Mechanical room height {val}{unit} may not accommodate equipment. Verify with MEP engineer.",
            },
        }

        rule = warnings.get(category)
        if not rule:
            return None

        if "min" in rule and value < rule["min"]:
            msg = rule.get("msg", rule.get("msg_low", ""))
            return msg.format(val=value, unit=unit)
        if "max" in rule and value > rule["max"]:
            msg = rule.get("msg_high", "")
            return msg.format(val=value, unit=unit)

        return None

    # -------------------------------------------------------------------------
    # AGGREGATE ANALYSIS
    # -------------------------------------------------------------------------

    def analyze_document(self, text: str, trade: Optional[str] = None,
                         climate_zone: str = "5") -> dict:
        """
        Run full domain knowledge analysis on a document.

        Returns:
            Comprehensive analysis dict with checklists, anomalies, and code violations.
        """
        return {
            "checklist_results": [i.to_dict() for i in self.check_document(text, trade)],
            "anomalies": [a.to_dict() for a in self.detect_anomalies(text)],
            "code_violations": [v.to_dict() for v in self.check_code_compliance(text, climate_zone)],
            "summary": {
                "critical_issues": (
                    sum(1 for i in self.check_document(text, trade) if i.severity == "critical" and i.status == "missing") +
                    sum(1 for a in self.detect_anomalies(text) if a.severity == "critical") +
                    sum(1 for v in self.check_code_compliance(text, climate_zone) if v.severity == "critical")
                ),
                "total_checks": len(self.check_document(text, trade)),
                "total_anomalies": len(self.detect_anomalies(text)),
                "total_violations": len(self.check_code_compliance(text, climate_zone)),
            },
        }
