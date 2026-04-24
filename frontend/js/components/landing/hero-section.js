/**
 * hero-section.js — Landing Page Hero
 *
 * SOLID: Single Responsibility — only the hero section.
 *
 * [CITE: Krug2014] Value proposition must be self-evident without scrolling.
 * [CITE: Nielsen1994] Visibility of system status — show what the product IS.
 */

export function renderHeroSection() {
  return `
    <section class="relative overflow-hidden">
      <div class="max-w-7xl mx-auto px-6 py-20 lg:py-28">
        <div class="grid lg:grid-cols-2 gap-12 items-center">
          <div>
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 text-blue-400 text-xs font-medium mb-6 border border-blue-500/20">
              <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              Agent Mesh Online — 10 Nodes Active
            </div>
            <h1 class="text-4xl lg:text-6xl font-bold text-white leading-tight mb-6">
              No APIs.<br>
              <span class="text-blue-400">Pure Agents.</span><br>
              Document Intelligence.
            </h1>
            <p class="text-lg text-slate-400 mb-8 max-w-lg">
              Drop your construction documents into the inbox. The agent fleet parses, 
              embeds, and analyzes them. Ask questions. Draft RFIs. Catch contradictions 
              before they become change orders.
            </p>
            <div class="flex flex-wrap gap-4">
              <button data-nav="/login" class="px-8 py-4 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-xl transition shadow-lg shadow-blue-600/20">
                <i class="fas fa-rocket mr-2"></i>Enter Agent Mesh
              </button>
              <button data-nav="/login" class="px-8 py-4 bg-slate-800 hover:bg-slate-700 text-white font-semibold rounded-xl transition border border-slate-700">
                <i class="fas fa-shield-alt mr-2"></i>Prove Project Knowledge
              </button>
            </div>
            <div class="mt-8 flex items-center gap-6 text-xs text-slate-500">
              <span><i class="fas fa-check text-emerald-400 mr-1"></i>No passwords</span>
              <span><i class="fas fa-check text-emerald-400 mr-1"></i>3-Factor Auth</span>
              <span><i class="fas fa-check text-emerald-400 mr-1"></i>Research-backed</span>
            </div>
          </div>
          <div class="relative">
            <div class="card-glass rounded-2xl p-6 border border-slate-700/50">
              <div class="flex items-center gap-2 mb-4">
                <div class="w-3 h-3 rounded-full bg-red-400"></div>
                <div class="w-3 h-3 rounded-full bg-amber-400"></div>
                <div class="w-3 h-3 rounded-full bg-emerald-400"></div>
                <span class="ml-2 text-xs text-slate-500">Agent Activity Log</span>
              </div>
              <div class="space-y-2 text-xs font-mono">
                <div class="text-slate-400"><span class="text-emerald-400">✓</span> node-e: Ingested STRUCT_SPEC.txt (142 chunks)</div>
                <div class="text-slate-400"><span class="text-blue-400">⚙</span> node-a: Query "concrete strength" routed to retriever</div>
                <div class="text-slate-400"><span class="text-amber-400">!</span> node-f: Contradiction detected — spec says 5,000 psi, drawing says 4,000 psi</div>
                <div class="text-slate-400"><span class="text-purple-400">✎</span> node-g: Drafting RFI-006 with cited sources</div>
                <div class="text-slate-400"><span class="text-emerald-400">✓</span> node-d: Audit trail appended — SHA-256 verified</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  `;
}
