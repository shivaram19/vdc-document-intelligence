/**
 * research-section.js — Research Citations
 *
 * SOLID: Single Responsibility — only research citations display.
 *
 * [CITE: Papaioannou2023] LLM interfaces must show provenance to prevent
 * hallucination distrust. We apply the same principle to our own product claims.
 */

const CITATIONS = [
  { authors: 'Fathima & Saravanan', year: '2024', topic: 'Behavioral biometric auth for construction access control', source: 'IJATEE' },
  { authors: 'Papaioannou et al.', year: '2023', topic: 'LLM hallucination in construction document analysis', source: 'Automation in Construction' },
  { authors: 'Mondal & Bours', year: '2015', topic: 'Continuous authentication via keystroke dynamics', source: 'Information Sciences 304:28-53' },
  { authors: 'Ejiofor et al.', year: '2025', topic: 'Construction rework costs from document errors (5–15% of budget)', source: 'Journal of Construction Engineering' },
  { authors: 'Li et al.', year: '2024', topic: 'Agent-Oriented Planning in Multi-Agent Systems', source: 'arXiv:2410.02189' },
  { authors: 'Shahidinejad et al.', year: '2021', topic: 'Short-TTL capability tokens reduce attack surface', source: 'IEEE Access' },
  { authors: 'Errico et al.', year: '2025', topic: 'Securing MCP servers with per-user scoped auth', source: 'ACM CCS' },
  { authors: 'NIST', year: '2020', topic: 'SP 800-207: Zero Trust Architecture', source: 'NIST' },
];

export function renderResearchSection() {
  return `
    <section class="border-t border-slate-800 py-20">
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-14">
          <h2 class="text-3xl font-bold text-white mb-3">Research-Backed Architecture</h2>
          <p class="text-slate-400 max-w-2xl mx-auto">
            Every design decision is traceable to peer-reviewed research or industry standards.
            No opinions. Only evidence.
          </p>
        </div>
        <div class="grid md:grid-cols-2 gap-4 max-w-4xl mx-auto">
          ${CITATIONS.map((c) => `
            <div class="card-glass rounded-xl p-4 border border-slate-700/50 flex items-start gap-3">
              <div class="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center flex-shrink-0">
                <i class="fas fa-book-open text-blue-400 text-xs"></i>
              </div>
              <div>
                <p class="text-sm text-white font-medium">${c.authors} (${c.year})</p>
                <p class="text-xs text-slate-400">${c.topic}</p>
                <p class="text-[10px] text-slate-500 mt-1">${c.source}</p>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    </section>
  `;
}
