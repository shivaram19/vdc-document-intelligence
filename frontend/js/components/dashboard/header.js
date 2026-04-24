/**
 * header.js — Dashboard Header
 * SOLID: SRP — only the sticky header bar.
 */

export function renderHeaderHTML() {
  return `
    <header class="border-b border-slate-700/50 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-lg">M</div>
          <div>
            <h1 class="font-bold text-lg text-white">Medha</h1>
            <p class="text-xs text-slate-400">Agent-Driven Document Intelligence</p>
          </div>
        </div>
        <div class="flex items-center gap-4">
          <span id="agent-status" class="flex items-center gap-2 text-xs px-3 py-1 rounded-full bg-slate-700/50 text-slate-400 border border-slate-600/20">
            <span class="w-2 h-2 rounded-full bg-slate-500"></span>Connecting...
          </span>
          <button id="logout-btn" class="text-xs text-slate-400 hover:text-white transition">
            <i class="fas fa-sign-out-alt mr-1"></i>Logout
          </button>
        </div>
      </div>
    </header>
  `;
}
