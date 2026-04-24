/**
 * header.js — Dashboard Header
 * SOLID: SRP — only the sticky header bar.
 */

export function renderHeaderHTML() {
  return `
    <header class="border-b border-bp-light/30 bg-bp-dark/80 backdrop-blur-sm sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-sm bg-bp-accent flex items-center justify-center text-white font-bold">M</div>
          <div>
            <h1 class="font-bold text-white">Medha</h1>
            <p class="text-xs text-gray-500 font-mono">DOCUMENT INSPECTION SYSTEM</p>
          </div>
        </div>
        <div class="flex items-center gap-4">
          <span id="agent-status" class="flex items-center gap-2 text-xs px-3 py-1.5 rounded-sm bg-bp-mid text-gray-500 border border-bp-light/30 font-mono">
            <span class="w-1.5 h-1.5 rounded-full bg-gray-600"></span>CONNECTING...
          </span>
          <button id="logout-btn" class="text-xs text-gray-500 hover:text-white transition font-mono">
            <i class="fas fa-sign-out-alt mr-1"></i>LOGOUT
          </button>
        </div>
      </div>
    </header>
  `;
}
