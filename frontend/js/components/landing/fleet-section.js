/**
 * fleet-section.js — Agent Fleet Status
 * SOLID: SRP — only fleet grid.
 */

const NODES = [
  { id: 'node-a', name: 'Finder', role: 'Document Search', status: 'online', problem: 'Waste 20 min searching for one spec clause' },
  { id: 'node-b', name: 'Builder', role: 'Batch Execution', status: 'online', problem: 'Uploaded 500 files and the system froze' },
  { id: 'node-c', name: 'Gatekeeper', role: 'Authentication', status: 'online', problem: 'Can\'t share docs with subs without data leaks' },
  { id: 'node-d', name: 'Scribe', role: 'Audit Logging', status: 'online', problem: 'Auditor asked for proof. We had nothing.' },
  { id: 'node-e', name: 'Librarian', role: 'Document Upload', status: 'online', problem: '10,000 pages and no way to search them' },
  { id: 'node-f', name: 'Spotter', role: 'Contradiction Scan', status: 'online', problem: 'Drawing said 6in, spec said 8in, we poured wrong' },
  { id: 'node-g', name: 'Drafter', role: 'RFI Drafting', status: 'online', problem: 'My RFIs sit unanswered for 3 weeks' },
  { id: 'node-h', name: 'Cartographer', role: 'Dependency Map', status: 'online', problem: 'Change HVAC spec, what drawings affected?' },
  { id: 'node-i', name: 'Dispatcher', role: 'Project Management', status: 'online', problem: 'Don\'t know if system is working or failing' },
  { id: 'node-j', name: 'Watchdog', role: 'System Monitoring', status: 'online', problem: 'System slow for 3 hours, nobody noticed' },
];

export function renderFleetSection() {
  const cards = NODES.map((n) => `
    <div class="card-structural flex items-center gap-3">
      <div class="w-2 h-2 rounded-full ${n.status === 'online' ? 'bg-safe-green animate-pulse-slow' : 'bg-safe-red'}"></div>
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2">
          <span class="text-xs font-mono text-gray-500">${n.id}</span>
          <span class="text-sm font-semibold text-white">${n.name}</span>
        </div>
        <p class="text-xs text-gray-500 mt-0.5 truncate">${n.problem}</p>
      </div>
      <span class="badge-pass text-[10px]">${n.status.toUpperCase()}</span>
    </div>
  `).join('');

  return `
    <section class="py-20">
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-14">
          <h2 class="text-3xl font-bold text-white mb-3">10-Agent Inspection Fleet</h2>
          <p class="text-gray-400 max-w-2xl mx-auto">
            No single point of failure. Each agent specializes in one document control task. 
            Consensus attestation on every critical decision.
          </p>
        </div>
        <div class="grid md:grid-cols-2 lg:grid-cols-5 gap-3">
          ${cards}
        </div>
        <div class="mt-8 text-center">
          <span class="inline-flex items-center gap-2 text-sm text-gray-500 font-mono">
            <span class="w-1.5 h-1.5 rounded-full bg-safe-green animate-pulse-slow"></span>
            10/10 NODES ONLINE — CONSENSUS THRESHOLD: 7/10
          </span>
        </div>
      </div>
    </section>
  `;
}
