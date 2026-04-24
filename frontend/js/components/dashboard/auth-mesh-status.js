/**
 * auth-mesh-status.js — Auth Mesh Status Panel
 * SOLID: SRP — only auth factor indicators.
 */

import { state } from '../../state.js';

export function renderAuthMeshStatusHTML() {
  return `
    <section class="max-w-7xl mx-auto px-6 pb-4">
      <div class="card-structural border-bp-accent/20">
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-semibold text-white text-sm flex items-center gap-2">
            <i class="fas fa-shield-alt text-bp-accent text-xs"></i>
            <span class="font-mono">AUTH MESH STATUS</span>
          </h3>
          <span class="badge-info text-[10px]">3-FACTOR AGENTIC</span>
        </div>
        <div class="grid md:grid-cols-4 gap-3 text-xs">
          <div class="bg-bp-dark/50 rounded-sm p-3 text-center border border-bp-light/20">
            <div id="auth-factor-1" class="text-safe-yellow font-bold text-lg mb-1 font-mono">—</div>
            <div class="text-gray-500 font-mono">KNOWLEDGE PROOF</div>
          </div>
          <div class="bg-bp-dark/50 rounded-sm p-3 text-center border border-bp-light/20">
            <div id="auth-factor-2" class="text-safe-yellow font-bold text-lg mb-1 font-mono">—</div>
            <div class="text-gray-500 font-mono">BEHAVIORAL FP</div>
          </div>
          <div class="bg-bp-dark/50 rounded-sm p-3 text-center border border-bp-light/20">
            <div id="auth-factor-3" class="text-safe-yellow font-bold text-lg mb-1 font-mono">—</div>
            <div class="text-gray-500 font-mono">AGENT ATTESTATION</div>
          </div>
          <div class="bg-bp-dark/50 rounded-sm p-3 text-center border border-bp-light/20">
            <div id="auth-capabilities" class="text-bp-accent font-bold text-lg mb-1 font-mono">—</div>
            <div class="text-gray-500 font-mono">CAPABILITIES</div>
          </div>
        </div>
        <div id="auth-capability-list" class="mt-3 flex flex-wrap gap-1"></div>
      </div>
    </section>
  `;
}

export function updateAuthMeshStatus() {
  const f1 = document.getElementById('auth-factor-1');
  const f2 = document.getElementById('auth-factor-2');
  const f3 = document.getElementById('auth-factor-3');
  const caps = document.getElementById('auth-capabilities');
  const capList = document.getElementById('auth-capability-list');

  if (state.authenticated) {
    if (f1) f1.innerHTML = '<i class="fas fa-check text-safe-green"></i>';
    if (f2) f2.innerHTML = '<i class="fas fa-check text-safe-green"></i>';
    if (f3) f3.innerHTML = '<i class="fas fa-check text-safe-green"></i>';
    if (caps) caps.textContent = state.capabilities?.length || 0;
    if (capList) {
      capList.innerHTML = state.capabilities?.map((c) =>
        `<span class="text-[10px] px-2 py-0.5 rounded-sm bg-bp-accent/10 text-bp-accent border border-bp-accent/20 font-mono">${c.replace('can_', '')}</span>`
      ).join('') || '';
    }
  } else {
    if (f1) f1.innerHTML = '—';
    if (f2) f2.innerHTML = '—';
    if (f3) f3.innerHTML = '—';
    if (caps) caps.textContent = '—';
    if (capList) capList.innerHTML = '';
  }
}
