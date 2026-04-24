/**
 * fleet-section.js — Fleet Visualization
 *
 * SOLID: Single Responsibility — only fleet node cards.
 *
 * [CITE: Li2024] Agent-Oriented Planning: Role specialization (Solvability
 * principle) requires clear visibility of each agent's capability.
 */

const NODES = [
  { id: 'node-a', role: 'Curiosity Brain', cap: 'Query Routing', color: 'blue' },
  { id: 'node-b', role: 'Executor Builder', cap: 'Task Execution', color: 'emerald' },
  { id: 'node-c', role: 'Memory Guardian', cap: 'Persistence', color: 'purple' },
  { id: 'node-d', role: 'Safety Auditor', cap: 'Audit Trail', color: 'red' },
  { id: 'node-e', role: 'Document Parser', cap: 'Ingestion', color: 'cyan' },
  { id: 'node-f', role: 'Contradiction Detector', cap: 'Conflict Scan', color: 'amber' },
  { id: 'node-g', role: 'RFI Drafter', cap: 'Draft Generation', color: 'pink' },
  { id: 'node-h', role: 'Knowledge Graph', cap: 'Relationship Map', color: 'indigo' },
  { id: 'node-i', role: 'Fleet Router', cap: 'Coordination', color: 'emerald', primary: true },
  { id: 'node-j', role: 'Metrics Collector', cap: 'Telemetry', color: 'slate' },
];

export function renderFleetSection() {
  return `
    <section class="border-t border-slate-800 py-20">
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-14">
          <h2 class="text-3xl font-bold text-white mb-3">10-Node Agent Fleet</h2>
          <p class="text-slate-400 max-w-2xl mx-auto">
            Each node has a single responsibility. They communicate through shared memory,
            not APIs. Add new nodes without restarting the mesh.
          </p>
        </div>
        <div class="grid md:grid-cols-5 gap-4">
          ${NODES.map((n) => `
            <div class="card-glass rounded-xl p-4 border border-slate-700/50 ${n.primary ? 'border-emerald-500/30' : ''} text-center">
              <div class="w-10 h-10 rounded-lg bg-${n.color}-500/10 flex items-center justify-center mx-auto mb-3">
                <span class="text-${n.color}-400 font-bold text-xs">${n.id.replace('node-', '')}</span>
              </div>
              <p class="text-xs font-medium text-white mb-1">${n.role}</p>
              <p class="text-[10px] text-slate-500">${n.cap}</p>
            </div>
          `).join('')}
        </div>
      </div>
    </section>
  `;
}
