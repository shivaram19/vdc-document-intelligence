/**
 * cta-section.js — Call to Action
 *
 * SOLID: Single Responsibility — only CTA section.
 *
 * [CITE: Krug2014] Every page needs a clear, unambiguous next step.
 * [CITE: Fathima2024] Construction professionals value "prove it first"
 * over "trust us" — the CTA leads to knowledge-proof auth, not a sales form.
 */

export function renderCTASection() {
  return `
    <section class="border-t border-slate-800 py-20">
      <div class="max-w-4xl mx-auto px-6 text-center">
        <h2 class="text-3xl font-bold text-white mb-4">
          Prove You Know Your Project.
        </h2>
        <p class="text-slate-400 mb-8 max-w-xl mx-auto">
          No passwords. No forms. The agent mesh verifies your identity by asking 
          questions only someone with legitimate document access can answer.
        </p>
        <button data-nav="/login" class="px-10 py-4 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-xl transition shadow-lg shadow-blue-600/20 text-lg">
          <i class="fas fa-shield-alt mr-2"></i>Authenticate via Knowledge Proof
        </button>
        <p class="text-xs text-slate-500 mt-4">
          3-Factor Agentic Auth: Knowledge-Provenance + Behavioral Fingerprinting + Agent Consensus Attestation
        </p>
      </div>
    </section>
  `;
}
