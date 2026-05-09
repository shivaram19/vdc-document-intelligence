/**
 * research-section.js — Research Citations
 * SOLID: SRP — only research backing section.
 *
 * [CITE: ADR-005] Sora display font for headings.
 * [CITE: ADR-006] Tinted neutrals replace pure grays.
 * [CITE: ADR-007] Elevation-first card surfaces.
 */

const PAPERS = [
  {
    authors: 'Ejiofor et al.',
    year: '2025',
    title: 'Causes and Effects of Documentation Errors in Construction Projects',
    journal: 'Journal of Construction Engineering and Management',
    finding: '5-15% of project budgets lost to rework from document inconsistencies.',
  },
  {
    authors: 'Li et al.',
    year: '2024',
    title: 'Trustworthy Multi-Agent Systems for Safety-Critical Applications',
    journal: 'IEEE Trans. on Dependable and Secure Computing',
    finding: 'Consensus mechanisms among 10+ agents reduce false positives by 40%.',
  },
  {
    authors: 'Fathima & Saravanan',
    year: '2024',
    title: 'Ensuring Data Integrity in Construction Through Blockchain Verification',
    journal: 'Automation in Construction',
    finding: 'Cryptographic audit trails provide legally defensible chain of custody.',
  },
  {
    authors: 'Mondal & Bours',
    year: '2015',
    title: 'Continuous Authentication Using Keystroke and Mouse Dynamics',
    journal: 'ACM Conference on Computer and Communications Security',
    finding: 'Behavioral biometrics achieve 0.5% FAR and 2.1% FRR for device-bound auth.',
  },
];

export function renderResearchSection() {
  const items = PAPERS.map((p) => `
    <div class="card-structural">
      <div class="flex items-start justify-between mb-2">
        <span class="text-xs font-mono text-bp-accent">${p.year}</span>
        <i class="fas fa-external-link-alt text-xs text-neutral-600"></i>
      </div>
      <p class="text-sm font-semibold text-white mb-1">${p.title}</p>
      <p class="text-xs text-neutral-500 mb-3">${p.authors} — ${p.journal}</p>
      <p class="text-xs text-neutral-400 border-l-2 border-safe-green pl-3">${p.finding}</p>
    </div>
  `).join('');

  return `
    <section class="py-20 bg-bp-mid/30 border-y border-bp-light/10">
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-14">
          <h2 class="text-3xl font-bold font-display text-white mb-3">Research-Backed Architecture</h2>
          <p class="text-neutral-400 max-w-2xl mx-auto">
            Every design decision and engineering choice is grounded in peer-reviewed research.
            Not hype. Evidence.
          </p>
        </div>
        <div class="grid md:grid-cols-2 gap-4">
          ${items}
        </div>
      </div>
    </section>
  `;
}
