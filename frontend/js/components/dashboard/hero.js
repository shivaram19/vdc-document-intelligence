/**
 * hero.js — Dashboard Hero Section
 * SOLID: SRP — only the hero + agent log panel.
 */

export function renderDashboardHeroHTML() {
  return `
    <section class="max-w-7xl mx-auto px-6 py-10">
      <div class="grid md:grid-cols-3 gap-4 items-start">
        <div class="md:col-span-2">
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-sm bg-bp-accent/10 text-bp-accent text-xs font-mono mb-4 border border-bp-accent/20">
            <i class="fas fa-network-wired text-xs"></i> 10-NODE AGENT FLEET
          </div>
          <h2 class="text-3xl font-bold text-white leading-tight mb-3">
            Prevent Rework.<br>
            <span class="text-bp-accent">Before It Costs You.</span>
          </h2>
          <p class="text-gray-400 mb-4 text-sm leading-relaxed">
            Drop documents into the inbox. The agent fleet parses, embeds, and inspects them automatically.
            Ask questions. Draft RFIs. Detect contradictions. All agent-orchestrated.
          </p>
          <div class="flex flex-wrap gap-2 text-xs font-mono">
            <span class="px-2 py-1 rounded-sm bg-bp-mid text-gray-500 border border-bp-light/30">node-a: Finder</span>
            <span class="px-2 py-1 rounded-sm bg-bp-mid text-gray-500 border border-bp-light/30">node-e: Librarian</span>
            <span class="px-2 py-1 rounded-sm bg-bp-mid text-gray-500 border border-bp-light/30">node-f: Spotter</span>
            <span class="px-2 py-1 rounded-sm bg-bp-mid text-gray-500 border border-bp-light/30">node-g: Drafter</span>
          </div>
        </div>
        <div class="card-structural">
          <h3 class="font-semibold text-white mb-3 text-sm flex items-center gap-2">
            <i class="fas fa-terminal text-safe-green text-xs"></i>
            <span class="font-mono">AGENT ACTIVITY LOG</span>
          </h3>
          <div id="agent-log" class="space-y-0 max-h-[140px] overflow-y-auto text-xs font-mono">
            <div class="text-gray-600 italic py-2">Waiting for agent events...</div>
          </div>
        </div>
      </div>
    </section>
  `;
}
