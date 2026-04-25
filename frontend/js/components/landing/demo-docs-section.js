/**
 * demo-docs-section.js — Real Construction Documents for Live Demo
 * SOLID: SRP — only sample document listing.
 *
 * Visitors download real-world specs & drawings, then upload to test Medha.
 */

const DEMO_DOCS = [
  {
    name: 'SMACNA HVAC Duct Standards',
    file: 'SMACNA_HVAC_Duct_Standards.pdf',
    type: 'Mechanical Specification',
    pages: 416,
    size: '9.6 MB',
    desc: 'Industry-standard HVAC duct construction standards. Tests specification parsing, section hierarchy, and code reference extraction.',
    tags: ['HVAC', 'Ductwork', 'Standards'],
  },
  {
    name: 'SRP HVAC Construction Spec',
    file: 'SRP_HVAC_Construction_Spec.pdf',
    type: 'MEP Specification',
    pages: 434,
    size: '6.6 MB',
    desc: 'Full Division 23 HVAC specification for utility-scale construction. Tests equipment schedules, submittal requirements, and performance criteria.',
    tags: ['HVAC', 'Division 23', 'MEP'],
  },
  {
    name: 'Sanibel Fire Station Drawings',
    file: 'Sanibel_Fire_Station_Drawings_SAMPLE.pdf',
    type: 'Architectural Drawings',
    pages: 10,
    size: '13.6 MB',
    desc: 'Sample of structural & architectural drawing set for a municipal fire station. Tests drawing index parsing, sheet cross-references, and A/E coordination.',
    tags: ['Structural', 'Architectural', 'Public'],
  },
  {
    name: 'UCCS Cybersecurity Drawings',
    file: 'UCCS_Cybersecurity_Drawings_SAMPLE.pdf',
    type: 'Architectural Drawings',
    pages: 10,
    size: '10.2 MB',
    desc: 'Sample of campus building drawing set with site, architectural, and MEP sheets. Tests multi-discipline coordination and plan-section correlation.',
    tags: ['Site', 'MEP', 'Campus'],
  },
  {
    name: 'UMN Division 23 HVAC',
    file: 'UMN_Division23_HVAC.pdf',
    type: 'Division 23 Specification',
    pages: 167,
    size: '1.9 MB',
    desc: 'University Division 23 HVAC spec with controls, insulation, and testing requirements. Tests controls sequences, commissioning specs, and closeout submittals.',
    tags: ['Controls', 'Commissioning', 'University'],
  },
];

export function renderDemoDocsSection() {
  const cards = DEMO_DOCS.map((d) => `
    <div class="card-structural flex flex-col">
      <div class="flex items-center justify-between mb-3">
        <div class="w-10 h-10 rounded-sm bg-bp-accent/10 flex items-center justify-center">
          <i class="fas fa-file-pdf text-bp-accent text-sm"></i>
        </div>
        <span class="text-[10px] font-mono text-gray-500 border border-gray-700 px-2 py-0.5 rounded-sm">${d.type.toUpperCase()}</span>
      </div>
      <h3 class="text-lg font-semibold text-white mb-1">${d.name}</h3>
      <div class="flex items-center gap-2 text-xs text-gray-500 font-mono mb-3">
        <span>${d.pages} pages</span>
        <span class="text-gray-700">|</span>
        <span>${d.size}</span>
      </div>
      <p class="text-sm text-gray-400 leading-relaxed mb-3 flex-1">${d.desc}</p>
      <div class="flex flex-wrap gap-1.5 mb-4">
        ${d.tags.map((t) => `<span class="text-[10px] font-mono text-bp-accent bg-bp-accent/10 px-2 py-0.5 rounded-sm">${t}</span>`).join('')}
      </div>
      <a href="demo-docs/${d.file}" download
         class="w-full py-2.5 bg-bp-accent/10 hover:bg-bp-accent/20 border border-bp-accent/30 text-bp-accent text-sm font-medium rounded-sm text-center transition-colors flex items-center justify-center gap-2">
        <i class="fas fa-download text-xs"></i> Download PDF
      </a>
    </div>
  `).join('');

  return `
    <section class="py-20 bg-bp-mid/30 border-y border-bp-light/10">
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-14">
          <h2 class="text-3xl font-bold text-white mb-3">Test With Real Documents</h2>
          <p class="text-gray-400 max-w-2xl mx-auto">
            Download actual construction specs and drawings. Upload them to Medha and see how it 
            parses sections, finds contradictions, and drafts RFIs — on real project data.
          </p>
        </div>
        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          ${cards}
        </div>
        <div class="mt-10 text-center">
          <p class="text-xs text-gray-500 font-mono">
            All documents sourced from public repositories and government open-data portals.
            Drawing sets include first 10 pages as representative samples.
          </p>
        </div>
      </div>
    </section>
  `;
}
