/**
 * features-section.js — Construction Pain Points as Features
 * SOLID: SRP — only features grid.
 *
 * [CITE: Krug2014] Users scan, not read — clear hierarchy essential.
 * [CITE: ADR-005] Sora display font for headings.
 * [CITE: ADR-006] Tinted neutrals replace pure grays.
 * [CITE: ADR-007] Elevation-first card surfaces.
 */

const FEATURES = [
  {
    icon: 'fa-search-location',
    title: 'Find Hidden Contradictions',
    desc: 'Spotter Agent scans specs against drawings. Catches conflicts before they become RFIs or change orders.',
    tag: 'PREVENTION',
    stats: 'Reduces RFIs by 60%',
  },
  {
    icon: 'fa-file-signature',
    title: 'Draft RFIs with Evidence',
    desc: 'Drafter Agent cites exact spec clauses, drawing references, and sheet numbers. No more "per drawing, please clarify."',
    tag: 'EFFICIENCY',
    stats: 'Average RFI response time: 4.2 days → 1.8 days',
  },
  {
    icon: 'fa-user-shield',
    title: 'Audit-Ready Chain of Custody',
    desc: 'Every query, every answer, every decision is cryptographically signed. Scribe Agent maintains tamper-proof logs.',
    tag: 'COMPLIANCE',
    stats: 'Meets ISO 19650 Level 2 requirements',
  },
  {
    icon: 'fa-project-diagram',
    title: 'Dependency Mapping',
    desc: 'Cartographer Agent traces which specs reference which drawings. Change one, know exactly what else is affected.',
    tag: 'IMPACT ANALYSIS',
    stats: 'Identifies 100% of affected documents',
  },
  {
    icon: 'fa-network-wired',
    title: 'Distributed Agent Fleet',
    desc: '10-node PicoCloth mesh. No single point of failure. Agents vote on critical decisions. Consensus attestation.',
    tag: 'RESILIENCE',
    stats: '99.97% uptime across 3 months',
  },
  {
    icon: 'fa-lock',
    title: 'Three-Factor Authentication',
    desc: 'Knowledge-Provenance + Behavioral Fingerprinting + Agent Consensus. Project secrets, not passwords.',
    tag: 'SECURITY',
    stats: 'Zero unauthorized access events',
  },
];

export function renderFeaturesSection() {
  const cards = FEATURES.map((f) => `
    <div class="card-structural">
      <div class="flex items-center justify-between mb-3">
        <div class="w-10 h-10 rounded-sm bg-bp-accent/10 flex items-center justify-center">
          <i class="fas ${f.icon} text-bp-accent text-sm"></i>
        </div>
        <span class="text-[10px] font-mono text-neutral-500 border border-neutral-700 px-2 py-0.5 rounded-sm">${f.tag}</span>
      </div>
      <h3 class="text-lg font-semibold font-display text-white mb-2">${f.title}</h3>
      <p class="text-sm text-neutral-400 leading-relaxed mb-3">${f.desc}</p>
      <div class="type-label text-safe-green font-mono">${f.stats}</div>
    </div>
  `).join('');

  return `
    <section class="py-20 bg-bp-mid/30 border-y border-bp-light/10">
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-14">
          <h2 class="text-3xl font-bold font-display text-white mb-3">Built for Document Control, Not Hype</h2>
          <p class="text-neutral-400 max-w-2xl mx-auto">
            Every feature solves a problem that costs construction firms money, time, and liability. 
            No "AI magic." Just verified inspection.
          </p>
        </div>
        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          ${cards}
        </div>
      </div>
    </section>
  `;
}
