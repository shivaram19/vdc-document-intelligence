/**
 * cta-section.js — Call to Action
 * SOLID: SRP — only CTA section.
 *
 * [CITE: ADR-005] Sora display font for headings.
 * [CITE: ADR-006] Tinted neutrals replace pure grays.
 */

export function renderCTASection() {
  return `
    <section class="py-20">
      <div class="max-w-4xl mx-auto px-6 text-center">
        <div class="panel-inspection p-10">
          <h2 class="text-3xl font-bold font-display text-white mb-4">
            Catch Contradictions Before Concrete Is Poured
          </h2>
          <p class="text-neutral-400 mb-8 max-w-xl mx-auto">
            One spec-drawing mismatch costs more than this system does in a year. 
            Run your first inspection in under 60 seconds.
          </p>
          <div class="flex flex-wrap justify-center gap-3">
            <button data-nav="/connect" class="btn-inspect">
              <i class="fas fa-plug mr-2"></i>Connect Your Drawings
            </button>
            <button data-nav="/demo" class="btn-outline">
              <i class="fas fa-play mr-2"></i>Live Demo — No Signup
            </button>
            <button data-nav="/pricing" class="btn-outline">
              <i class="fas fa-tag mr-2"></i>View Pricing
            </button>
            <button data-nav="/outreach" class="btn-outline">
              <i class="fas fa-bullseye mr-2"></i>Pipeline
            </button>
          </div>
          <div class="mt-6 flex justify-center gap-6 text-xs font-mono text-neutral-600">
            <span><i class="fas fa-lock mr-1"></i>3-Factor Auth</span>
            <span><i class="fas fa-link mr-1"></i>Chain Verified</span>
            <span><i class="fas fa-server mr-1"></i>10 Nodes</span>
          </div>
        </div>
      </div>
    </section>
  `;
}
