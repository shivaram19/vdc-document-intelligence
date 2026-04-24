/**
 * hero.js — Dashboard Hero Section
 * SOLID: SRP — only the hero + agent log panel.
 */

export function renderDashboardHeroHTML() {
  return `
    <section class="max-w-7xl mx-auto px-6 py-10">
      <div class="grid md:grid-cols-3 gap-6 items-start">
        <div class="md:col-span-2">
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 text-blue-400 text-xs font-medium mb-4 border border-blue-500/20">
            <i class="fas fa-network-wired"></i> 10-Node Agent Fleet
          </div>
          <h2 class="text-3xl font-bold text-white leading-tight mb-3">
            No APIs. Pure Agents.<br>
            <span class="text-blue-400">Document Intelligence</span> by Medha
          </h2>
          <p class="text-slate-400 mb-4">
            Drop documents into the inbox. The agent fleet parses, embeds, and analyzes them automatically.
            Ask questions. Draft RFIs. Detect contradictions. All agent-orchestrated.
          </p>
          <div class="flex flex-wrap gap-2 text-xs">
            <span class="px-2 py-1 rounded bg-slate-800 text-slate-400 border border-slate-700">node-a: Curiosity Brain</span>
            <span class="px-2 py-1 rounded bg-slate-800 text-slate-400 border border-slate-700">node-e: Document Parser</span>
            <span class="px-2 py-1 rounded bg-slate-800 text-slate-400 border border-slate-700">node-f: Contradiction Detector</span>
            <span class="px-2 py-1 rounded bg-slate-800 text-slate-400 border border-slate-700">node-g: RFI Drafter</span>
          </div>
        </div>
        <div class="card-glass rounded-2xl p-4">
          <h3 class="font-semibold text-white mb-3 text-sm"><i class="fas fa-terminal mr-2 text-emerald-400"></i>Agent Activity Log</h3>
          <div id="agent-log" class="space-y-0 max-h-[140px] overflow-y-auto text-xs">
            <div class="text-slate-500 italic py-2">Waiting for agent events...</div>
          </div>
        </div>
      </div>
    </section>
  `;
}
