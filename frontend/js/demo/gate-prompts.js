/**
 * gate-prompts.js — Upgrade Prompts for Demo Limits
 *
 * [CITE: Cialdini1984] Commitment & Consistency: users who make small
 * commitments are more likely to make larger ones. The demo IS the
 * small commitment. The prompt asks for the next logical step.
 *
 * [CITE: KahnemanTversky1979] Loss Aversion: emphasize what will be
 * lost (demo data, inspection progress) not what they must pay.
 */

import { gatePrompt } from './demo-state.js';

export function renderGatePrompt(feature, onCtaClick) {
  const msg = gatePrompt(feature);
  return `
    <div class="card-structural border-safe-orange/40 bg-safe-orange/5 my-4">
      <div class="flex items-start gap-3">
        <i class="fas fa-lock text-safe-orange mt-1"></i>
        <div class="flex-1">
          <p class="text-sm font-semibold text-white mb-1">${msg.headline}</p>
          <p class="text-xs text-neutral-400 mb-3">${msg.body}</p>
          <button class="btn-inspect text-xs py-2 px-4" id="demo-gate-cta">
            <i class="fas fa-unlock mr-2"></i>${msg.cta}
          </button>
          <p class="text-[10px] text-neutral-600 mt-2 font-mono">${msg.sub}</p>
        </div>
      </div>
    </div>
  `;
}

export function wireGatePrompt(onCtaClick) {
  document.getElementById('demo-gate-cta')?.addEventListener('click', onCtaClick);
}

export function renderDemoBanner() {
  return `
    <div class="fixed bottom-0 left-0 right-0 bg-safe-orange/10 border-t border-safe-orange/30 px-6 py-2 z-50 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <span class="badge-pending text-[10px]"><i class="fas fa-flask mr-1"></i>LIVE DEMO</span>
        <span class="text-xs text-neutral-400 font-mono">Your demo data is temporary. <strong class="text-white">Request access</strong> to preserve your work.</span>
      </div>
      <div class="flex items-center gap-3">
        <span class="text-[10px] text-neutral-500 font-mono">Queries: <span id="demo-q-count">3</span> left</span>
        <span class="text-[10px] text-neutral-500 font-mono">Uploads: <span id="demo-u-count">1</span> left</span>
        <button id="demo-request-access" class="text-xs px-3 py-1.5 bg-bp-accent hover:bg-blue-500 text-white rounded-sm transition font-mono">
          REQUEST ACCESS
        </button>
      </div>
    </div>
  `;
}

export function updateDemoBanner(usage) {
  const qEl = document.getElementById('demo-q-count');
  const uEl = document.getElementById('demo-u-count');
  if (qEl) qEl.textContent = Math.max(0, 3 - (usage.customQueries || 0));
  if (uEl) uEl.textContent = Math.max(0, 1 - (usage.uploads || 0));
}
