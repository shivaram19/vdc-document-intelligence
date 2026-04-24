/**
 * cta-section.js — Call to Action
 * SOLID: SRP — only CTA section.
 */

export function renderCTASection() {
  return `
    <section class="py-20">
      <div class="max-w-4xl mx-auto px-6 text-center">
        <div class="panel-inspection p-10">
          <h2 class="text-3xl font-bold text-white mb-4">
            Catch Contradictions Before Concrete Is Poured
          </h2>
          <p class="text-gray-400 mb-8 max-w-xl mx-auto">
            One spec-drawing mismatch costs more than this system does in a year. 
            Run your first inspection in under 60 seconds.
          </p>
          <div class="flex flex-wrap justify-center gap-3">
            <button data-nav="/demo" class="btn-inspect">
              <i class="fas fa-play mr-2"></i>Start Live Demo — No Signup
            </button>
            <button data-nav="/login" class="btn-outline">
              <i class="fas fa-shield-alt mr-2"></i>Secure Login
            </button>
          </div>
          <div class="mt-6 flex justify-center gap-6 text-xs font-mono text-gray-600">
            <span><i class="fas fa-lock mr-1"></i>3-Factor Auth</span>
            <span><i class="fas fa-link mr-1"></i>Chain Verified</span>
            <span><i class="fas fa-server mr-1"></i>10 Nodes</span>
          </div>
        </div>
      </div>
    </section>
  `;
}
