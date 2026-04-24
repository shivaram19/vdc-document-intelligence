#!/usr/bin/env python3
"""Test suite for Medha v2 Phase 2: Domain Knowledge Engine"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from v2.domain_knowledge import DomainKnowledgeEngine

SAMPLE_HVAC_TEXT = """
HVAC DESIGN PARAMETERS
Space temperature setpoints: 72°F heating, 75°F cooling
Outside air ventilation: 20 CFM/person per ASHRAE 62.1
VAV units: Model ABC-500, 500 CFM each
Chiller efficiency: 0.55 kW/ton (meets ASHRAE 90.1)
Ductwork sealing: SMACNA Seal Class A
Economizer: Integrated dry bulb, high limit 75°F
Ceiling plenum depth: 12 inches
Mechanical room ceiling height: 10 feet
Fire dampers: Not shown
"""

SAMPLE_ARCH_TEXT = """
ARCHITECTURAL SPECIFICATIONS
Wall R-value: R-21 minimum continuous insulation
Roof R-value: R-30 above deck
Window U-factor: 0.30 maximum
Window SHGC: 0.25 maximum
Door width: 30 inches (typical office)
Lobby ceiling height: 18 feet
Office ceiling height: 9 feet AFF
Fire-rated corridor: 1-hour
"""

def test_checklist():
    print("\n🧪 Testing Checklist Engine...")
    engine = DomainKnowledgeEngine()
    issues = engine.check_document(SAMPLE_HVAC_TEXT, trade="hvac")

    critical_missing = [i for i in issues if i.severity == "critical" and i.status == "missing"]
    print(f"  Total checks: {len(issues)}")
    print(f"  Critical missing: {len(critical_missing)}")
    for issue in critical_missing[:3]:
        print(f"    ⚠️  [{issue.checklist_id}] {issue.description}")

    assert len(issues) > 0
    print("  ✅ Checklist test passed")

def test_anomaly_detection():
    print("\n🧪 Testing Anomaly Detection...")
    engine = DomainKnowledgeEngine()

    # Test mechanical room ceiling height anomaly
    text_with_anomaly = "Mechanical room ceiling height: 9 feet clear"
    anomalies = engine.detect_anomalies(text_with_anomaly)
    assert any(a.rule_triggered == "mech_room_ceiling_low" for a in anomalies), "Should detect low mech room ceiling"

    # Test window U-factor anomaly
    text_bad_window = "Window U-factor: 0.40"
    anomalies = engine.detect_anomalies(text_bad_window)
    assert any(a.rule_triggered == "window_u_factor_high" for a in anomalies), "Should detect high U-factor"

    print(f"  Detected {len(anomalies)} anomalies")
    for a in anomalies:
        print(f"    ⚠️  [{a.severity}] {a.description} (rule: {a.rule_triggered})")

    print("  ✅ Anomaly detection test passed")

def test_code_compliance():
    print("\n🧪 Testing Code Compliance...")
    engine = DomainKnowledgeEngine()

    # This should trigger violations in climate zone 5
    text_bad = """
    Wall R-value: R-13
    Roof R-value: R-30
    Window U-factor: 0.40
    """
    violations = engine.check_code_compliance(text_bad, climate_zone="5")

    print(f"  Violations found: {len(violations)}")
    for v in violations:
        print(f"    🚨 [{v.code}] {v.requirement} — Found: {v.found_value}")

    assert len(violations) >= 2, f"Expected >=2 violations, got {len(violations)}"
    print("  ✅ Code compliance test passed")

def test_full_analysis():
    print("\n🧪 Testing Full Document Analysis...")
    engine = DomainKnowledgeEngine()

    result = engine.analyze_document(SAMPLE_ARCH_TEXT, trade="architectural", climate_zone="5")

    print(f"  Checklist items: {len(result['checklist_results'])}")
    print(f"  Anomalies: {len(result['anomalies'])}")
    print(f"  Code violations: {len(result['code_violations'])}")
    print(f"  Critical issues: {result['summary']['critical_issues']}")

    assert result['summary']['total_checks'] > 0
    print("  ✅ Full analysis test passed")

def run_all_tests():
    print("=" * 60)
    print("MEDHA v2 PHASE 2: DOMAIN KNOWLEDGE ENGINE TESTS")
    print("=" * 60)

    try:
        test_checklist()
        test_anomaly_detection()
        test_code_compliance()
        test_full_analysis()

        print("\n" + "=" * 60)
        print("🎉 ALL DOMAIN KNOWLEDGE TESTS PASSED")
        print("=" * 60)
        return True
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n💥 TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
