/**
 * auth-mesh-status.js — Auth Mesh Status Panel
 * SOLID: SRP — only auth factor indicators.
 */

import { state } from '../../state.js';

export function renderAuthMeshStatusHTML() {
  return `
    <section class="max-w-7xl mx-auto px-6 pb-4">
      <div class="card-glass rounded-2xl p-4 border border-blue-500/20">
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-semibold text-white text-sm"><i class="fas fa-shield-alt mr-2 text-blue-400"></i>Auth Mesh Status</h3>
          <span class="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">3-Factor Agentic</span>
        </div>
        <div class="grid md:grid-cols-4 gap-3 text-xs">
          <div class="bg-slate-800/50 rounded-lg p-3 text-center">
            <div id="auth-factor-1" class="text-amber-400 font-bold text-lg mb-1">—</div>
            <div class="text-slate-400">Knowledge Proof</div>
          </div>
          <div class="bg-slate-800/50 rounded-lg p-3 text-center">
            <div id="auth-factor-2" class="text-amber-400 font-bold text-lg mb-1">—</div>
            <div class="text-slate-400">Behavioral FP</div>
          </div>
          <div class="bg-slate-800/50 rounded-lg p-3 text-center">
            <div id="auth-factor-3" class="text-amber-400 font-bold text-lg mb-1">—</div>
            <div class="text-slate-400">Agent Attestation</div>
          </div>
          <div class="bg-slate-800/50 rounded-lg p-3 text-center">
            <div id="auth-capabilities" class="text-blue-400 font-bold text-lg mb-1">—</div>
            <div class="text-slate-400">Capabilities</div>
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
    if (f1) f1.innerHTML = '<i class="fas fa-check text-emerald-400"></i>';
    if (f2) f2.innerHTML = '<i class="fas fa-check text-emerald-400"></i>';
    if (f3) f3.innerHTML = '<i class="fas fa-check text-emerald-400"></i>';
    if (caps) caps.textContent = state.capabilities?.length || 0;
    if (capList) {
      capList.innerHTML = state.capabilities?.map((c) =>
        `<span class="text-[10px] px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">${c.replace('can_', '')}</span>`
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
