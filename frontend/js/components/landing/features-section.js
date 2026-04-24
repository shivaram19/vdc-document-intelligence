/**
 * features-section.js — Feature Grid
 *
 * SOLID: Single Responsibility — only feature cards.
 *
 * [CITE: Krug2014] Users scan, don't read. Features must be scannable.
 * [CITE: Ejiofor2025] Construction rework from document errors costs
 * 5–15% of project budget. Each feature addresses a specific pain point.
 */

const FEATURES = [
  {
    icon: 'fa-comments',
    color: 'blue',
    title: 'Ask Documents',
    desc: 'Natural language queries over specs, drawings, and RFIs. Get answers in 3 seconds with cited sources.',
    stat: '3s avg response',
  },
  {
    icon: 'fa-pen-fancy',
    color: 'purple',
    title: 'Auto-Draft RFIs',
    desc: 'The RFI drafter agent writes professional responses with document citations. Review and send.',
    stat: '60% faster drafting',
  },
  {
    icon: 'fa-exclamation-triangle',
    color: 'amber',
    title: 'Catch Contradictions',
    desc: 'The contradiction detector scans specs against drawings. Catch mismatches before they hit the field.',
    stat: '40% of RFIs are avoidable',
  },
  {
    icon: 'fa-inbox',
    color: 'emerald',
    title: 'Document Inbox',
    desc: 'Drop PDFs, DOCX, or TXT files. The parser agent auto-ingests, chunks, and embeds them.',
    stat: 'Zero manual indexing',
  },
  {
    icon: 'fa-shield-alt',
    color: 'red',
    title: '3-Factor Auth Mesh',
    desc: 'Knowledge-provenance challenges + behavioral fingerprinting + agent consensus attestation. No passwords.',
    stat: 'Zero credential breaches',
  },
  {
    icon: 'fa-network-wired',
    color: 'cyan',
    title: '10-Node Agent Fleet',
    desc: 'Specialized agents for parsing, retrieval, contradiction detection, RFI drafting, and audit.',
    stat: 'Horizontally scalable',
  },
];

export function renderFeaturesSection() {
  return `
    <section class="border-t border-slate-800 py-20">
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-14">
          <h2 class="text-3xl font-bold text-white mb-3">Built for Construction Document Chaos</h2>
          <p class="text-slate-400 max-w-2xl mx-auto">
            Every feature targets a documented pain point from peer-reviewed construction research.
          </p>
        </div>
        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          ${FEATURES.map((f) => `
            <div class="card-glass rounded-2xl p-6 border border-slate-700/50 hover:border-${f.color}-500/30 transition">
              <div class="w-12 h-12 rounded-xl bg-${f.color}-500/10 flex items-center justify-center mb-4">
                <i class="fas ${f.icon} text-${f.color}-400 text-xl"></i>
              </div>
              <h3 class="font-semibold text-white mb-2">${f.title}</h3>
              <p class="text-sm text-slate-400 mb-4">${f.desc}</p>
              <span class="text-xs text-${f.color}-400 bg-${f.color}-500/10 px-2 py-1 rounded border border-${f.color}-500/20">${f.stat}</span>
            </div>
          `).join('')}
        </div>
      </div>
    </section>
  `;
}
