/**
 * sample-data.js — Pre-loaded Demo Project Data
 *
 * [CITE: NunesDreze2006] Endowed Progress Effect: users who perceive they
 * have already started a task are 2x more likely to complete it. Pre-loaded
 * documents and pre-discovered contradictions create instant "progress."
 *
 * [CITE: KahnemanTversky1979] Loss Aversion: data must feel owned by the
 * user. Label as "Your Demo Project" not "Sample Data."
 */

export const DEMO_PROJECT = {
  id: 'demo_medha_tower',
  name: 'Demo Tower — Mixed-Use Development',
  client: 'Medha Demo Client',
  docs: [
    { id: 'd1', name: 'STRUCT_SPEC.txt', type: 'spec', chunk_count: 312 },
    { id: 'd2', name: 'ARCH_DRAWING_NOTES.txt', type: 'drawing', chunk_count: 198 },
    { id: 'd3', name: 'MECH_SPEC_HVAC.txt', type: 'spec', chunk_count: 256 },
    { id: 'd4', name: 'FIRE_PROTECTION_SPEC.txt', type: 'spec', chunk_count: 178 },
    { id: 'd5', name: 'RFI_LOG.txt', type: 'rfi', chunk_count: 42 },
  ],
  document_count: 5,
  chunk_count: 986,
  contradictions: [
    {
      severity: 'CRITICAL',
      confidence: 0.94,
      issue: 'CONCRETE STRENGTH mismatch',
      spec_doc: 'STRUCT_SPEC.txt',
      spec_text: 'All structural concrete shall achieve minimum compressive strength of 5,000 psi at 28 days per ASTM C39.',
      drawing_doc: 'ARCH_DRAWING_NOTES.txt',
      drawing_text: 'Foundation notes indicate 4,000 psi concrete for column footings.',
      impact: '$47,000 estimated rework + schedule delay',
    },
    {
      severity: 'WARNING',
      confidence: 0.87,
      issue: 'FIRE RATING gap',
      spec_doc: 'FIRE_PROTECTION_SPEC.txt',
      spec_text: 'All corridor walls shall achieve 2-hour fire resistance rating per NFPA 251.',
      drawing_doc: 'ARCH_DRAWING_NOTES.txt',
      drawing_text: 'Wall type annotation W-4 shows 1-hour rating for Level 3 corridors.',
      impact: '$12,000 + inspection delay',
    },
  ],
  checked_pairs: 12,
};

export const DEMO_QUICK_ANSWERS = [
  {
    q: 'What is the HVAC temperature setpoint for office spaces?',
    a: 'Per MECH_SPEC_HVAC.txt Section 4.2, office spaces shall maintain 72°F ± 2°F heating setpoint and 74°F ± 2°F cooling setpoint. Zone thermostats located at TSTAT-O-01 through TSTAT-O-48.',
    sources: [
      { doc_name: 'MECH_SPEC_HVAC.txt', score: 0.98, text: 'Office zone thermostat setpoints: heating 72°F, cooling 74°F. Tolerance ±2°F.', doc_type: 'spec' },
    ],
  },
  {
    q: 'What are the fire protection sprinkler requirements?',
    a: 'Per FIRE_PROTECTION_SPEC.txt: Light hazard occupancy requires NFPA 13 standard spray sprinklers, K-factor 5.6, spaced per hydraulic calculation. Design density 0.10 gpm/sq ft over 1,500 sq ft.',
    sources: [
      { doc_name: 'FIRE_PROTECTION_SPEC.txt', score: 0.96, text: 'Sprinkler system designed per NFPA 13. Light hazard: K5.6 standard spray, design density 0.10 gpm/sq ft.', doc_type: 'spec' },
    ],
  },
  {
    q: 'What is the concrete strength for columns?',
    a: 'STRUCT_SPEC.txt specifies 5,000 psi minimum compressive strength at 28 days for all structural concrete per ASTM C39. NOTE: ARCH_DRAWING_NOTES.txt indicates 4,000 psi for footings — this is a contradiction flagged by Spotter Agent.',
    sources: [
      { doc_name: 'STRUCT_SPEC.txt', score: 0.99, text: 'Minimum compressive strength: 5,000 psi at 28 days per ASTM C39.', doc_type: 'spec' },
      { doc_name: 'ARCH_DRAWING_NOTES.txt', score: 0.91, text: 'Column footing concrete: 4,000 psi per detail F-12.', doc_type: 'drawing' },
    ],
    contradictions: [
      { spec_doc: 'STRUCT_SPEC.txt', spec_text: '5,000 psi', drawing_doc: 'ARCH_DRAWING_NOTES.txt', drawing_text: '4,000 psi' },
    ],
  },
];

export const DEMO_RFI_DRAFT = {
  number: 'RFI-007',
  question: 'Concrete strength discrepancy between structural spec and foundation drawings',
  draft: `TO: Structural Engineer
FROM: General Contractor
RE: RFI-007 — Concrete Strength Discrepancy

ISSUE:
STRUCT_SPEC.txt Section 3.1 specifies 5,000 psi minimum compressive strength for all structural concrete.
ARCH_DRAWING_NOTES.txt Detail F-12 indicates 4,000 psi for column footings.

IMPACT:
If 4,000 psi is used, the footing design does not meet the spec requirement. Estimated rework: $47,000.

REQUEST:
Please confirm the correct concrete strength for column footings and issue a drawing revision if 5,000 psi is required.

REFERENCES:
- STRUCT_SPEC.txt, Section 3.1, "Compressive Strength"
- ARCH_DRAWING_NOTES.txt, Detail F-12, "Foundation Notes"`,
  sources: [
    { doc_name: 'STRUCT_SPEC.txt' },
    { doc_name: 'ARCH_DRAWING_NOTES.txt' },
  ],
};
