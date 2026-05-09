/**
 * hero-section.js — Landing Hero
 * SOLID: SRP — only hero section.
 *
 * [CITE: Krug2014] Value prop must be self-evident in < 5s.
 * [CITE: Ejiofor2025] Document errors cause 5-15% rework.
 * [CITE: ADR-005] Sora display font for headings.
 * [CITE: ADR-006] Tinted neutrals replace pure grays.
 * [CITE: ADR-007] Elevation-first surfaces.
 */

export function renderHeroSection() {
  return `
    <section class="relative overflow-hidden border-b border-bp-light/20">
      <div class="max-w-7xl mx-auto px-6 py-16 lg:py-24">
        <div class="grid lg:grid-cols-2 gap-12 items-center">
          <div>
            <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-sm bg-safe-green/10 text-safe-green text-xs font-mono mb-6 border border-safe-green/30">
              <span class="w-1.5 h-1.5 rounded-full bg-safe-green animate-pulse"></span>
              INSPECTION SYSTEM ACTIVE — 10 AGENTS ONLINE
            </div>
            <h1 class="text-4xl lg:text-5xl font-bold font-display text-white leading-tight mb-6">
              Prevent Rework.<br>
              <span class="text-bp-accent">Before It Costs You.</span>
            </h1>
            <p class="text-lg text-neutral-400 mb-4 max-w-lg leading-relaxed">
              Construction documents contradict each other. Specs say 5,000 psi. Drawings say 4,000. 
              <strong class="text-white">Medha finds these conflicts before concrete is poured.</strong>
            </p>
            <div class="flex items-center gap-6 mb-8">
              <div class="text-center">
                <div class="type-impact text-safe-green">$50K</div>
                <div class="type-label text-neutral-500">per contradiction caught</div>
              </div>
              <div class="w-px h-10 bg-neutral-700"></div>
              <div class="text-center">
                <div class="type-impact text-safe-green">40%</div>
                <div class="type-label text-neutral-500">of RFIs are avoidable</div>
              </div>
              <div class="w-px h-10 bg-neutral-700"></div>
              <div class="text-center">
                <div class="type-impact text-safe-green">5-15%</div>
                <div class="type-label text-neutral-500">of budget lost to rework</div>
              </div>
            </div>
            <div class="flex flex-wrap gap-3">
              <button data-nav="/workbench" class="px-6 py-3 bg-bp-accent hover:bg-blue-500 text-white font-semibold rounded-sm transition shadow-lg shadow-bp-accent/20">
                <i class="fas fa-table-columns mr-2"></i>Open Workbench
              </button>
              <button data-nav="/connect" class="px-6 py-3 bg-transparent hover:bg-bp-light/30 text-neutral-300 font-semibold rounded-sm transition border border-bp-accent/40">
                <i class="fas fa-plug mr-2"></i>Connect Drawings
              </button>
              <button data-nav="/demo" class="px-6 py-3 text-neutral-400 hover:text-white font-semibold rounded-sm transition text-sm">
                Demo
              </button>
            </div>
          </div>
          <div class="relative">
            <div class="panel-inspection rounded-sm p-5 scanline">
              <div class="flex items-center justify-between mb-4 border-b border-bp-accent/20 pb-3">
                <div class="flex items-center gap-2">
                  <i class="fas fa-file-contract text-bp-accent text-sm"></i>
                  <span class="text-xs font-mono text-neutral-400">INSPECTION REPORT #2026-0424</span>
                </div>
                <span class="badge-critical text-xs">2 CRITICAL ISSUES</span>
              </div>
              <div class="space-y-3 font-mono text-xs">
                <div class="flex items-start gap-3 p-3 bg-safe-red/5 border-l-2 border-safe-red rounded-sm">
                  <i class="fas fa-times-circle text-safe-red mt-0.5"></i>
                  <div>
                    <p class="text-neutral-300 font-semibold">CONCRETE STRENGTH mismatch</p>
                    <p class="text-neutral-500 mt-0.5">SPEC: 5,000 psi | DRAWING: 4,000 psi</p>
                    <p class="text-safe-orange mt-1">ESTIMATED IMPACT: $47,000 rework</p>
                  </div>
                </div>
                <div class="flex items-start gap-3 p-3 bg-safe-yellow/5 border-l-2 border-safe-yellow rounded-sm">
                  <i class="fas fa-exclamation-triangle text-safe-yellow mt-0.5"></i>
                  <div>
                    <p class="text-neutral-300 font-semibold">FIRE RATING gap</p>
                    <p class="text-neutral-500 mt-0.5">SPEC: 2-hour | ARCH: 1-hour noted</p>
                    <p class="text-safe-orange mt-1">ESTIMATED IMPACT: $12,000 + inspection delay</p>
                  </div>
                </div>
                <div class="flex items-start gap-3 p-3 bg-safe-green/5 border-l-2 border-safe-green rounded-sm">
                  <i class="fas fa-check-circle text-safe-green mt-0.5"></i>
                  <div>
                    <p class="text-neutral-300 font-semibold">HVAC SETPOINTS verified</p>
                    <p class="text-neutral-500 mt-0.5">All specs consistent across M-101 to M-205</p>
                    <p class="text-safe-green mt-1">STATUS: PASS</p>
                  </div>
                </div>
              </div>
              <div class="mt-4 pt-3 border-t border-bp-accent/20 flex items-center justify-between">
                <span class="text-xs font-mono text-neutral-500">INSPECTED: 14 docs | 1,247 chunks</span>
                <span class="text-xs font-mono text-safe-green">CHAIN VERIFIED ✓</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  `;
}
