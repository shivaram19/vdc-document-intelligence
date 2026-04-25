/**
 * outreach.js — Global Outreach Pipeline Dashboard (Orchestrator)
 *
 * SRP: ONLY state assembly + event wiring. Rendering delegated.
 * [CITE: Krug2014] Every page answers: "What is this? Why? What do I do?"
 * [CITE: Gracker2025] Gracker.ai analysis (20M+ outreach attempts). Personalized outreach outperforms templated by 3x. https://gracker.ai/blog/increase-linkedin-acceptance-rate
 */

import { navigate } from '../router.js';
import { OUTREACH_TIERS, OUTREACH_TARGETS, getGlobalStats } from '../data/outreach-global.js';
import { renderTierSection } from '../components/outreach/tier-section.js';
import { renderJTBDBox, renderMethodologyBox } from '../components/outreach/info-boxes.js';

export function renderOutreach(container) {
  const stats = getGlobalStats();
  container.innerHTML = `
    <div class="min-h-screen blueprint-bg">
      ${renderHeader()}
      <main class="max-w-6xl mx-auto px-6 py-10">
        ${renderOverview(stats)}
        ${renderTiers()}
        ${renderJTBDBox()}
        ${renderMethodologyBox()}
      </main>
    </div>
  `;
  wireEvents();
}

function renderHeader() {
  return `
    <header class="border-b border-bp-light/30 bg-bp-dark/80 backdrop-blur-sm sticky top-0 z-50">
      <div class="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-sm bg-bp-accent flex items-center justify-center text-white font-bold">M</div>
          <div>
            <h1 class="font-bold text-white font-mono">MEDHA</h1>
            <p class="text-xs text-gray-500 font-mono">GLOBAL OUTREACH PIPELINE</p>
          </div>
        </div>
        <button data-nav="/" class="text-xs text-gray-500 hover:text-white transition font-mono">
          <i class="fas fa-arrow-left mr-1"></i>BACK
        </button>
      </div>
    </header>
  `;
}

function renderOverview(stats) {
  const stages = ['identified', 'contacted', 'demo', 'pilot', 'customer'];
  const labels = { identified: 'IDENTIFIED', contacted: 'CONTACTED', demo: 'DEMO', pilot: 'PILOT', customer: 'CUSTOMER' };
  const colors = { identified: 'bg-gray-600', contacted: 'bg-bp-accent', demo: 'bg-warn-yellow', pilot: 'bg-safe-orange', customer: 'bg-safe-green' };

  const bars = stages.map((s) => {
    const count = stats.byStage[s] || 0;
    const pct = stats.total ? Math.round((count / stats.total) * 100) : 0;
    return `
      <div class="flex items-center gap-3 text-xs">
        <span class="text-gray-500 font-mono w-20">${labels[s]}</span>
        <div class="flex-1 h-2 bg-bp-light/20 rounded-full overflow-hidden">
          <div class="h-full ${colors[s]} rounded-full" style="width:${pct}%"></div>
        </div>
        <span class="text-gray-400 font-mono w-8 text-right">${count}</span>
      </div>`;
  }).join('');

  const pills = OUTREACH_TIERS.map((t) => {
    const count = stats.byTier[t.id] || 0;
    return `<span class="px-2 py-1 rounded-sm text-[10px] font-mono bg-bp-light/20 text-gray-400">${t.name}: ${count}</span>`;
  }).join('');

  return `
    <div class="mb-10">
      <div class="flex items-end justify-between mb-4">
        <div>
          <h2 class="text-2xl font-bold text-white">Global Pipeline</h2>
          <p class="text-xs text-gray-500 mt-1 font-mono">${stats.total} TARGETS • 4 TIERS • RESEARCH-BACKED MESSAGING</p>
        </div>
        <div class="text-right">
          <div class="text-3xl font-bold text-white">${stats.total}</div>
          <p class="text-[10px] text-gray-500 font-mono">TOTAL TARGETS</p>
        </div>
      </div>
      <div class="card-structural border-bp-light/30 mb-4">
        <div class="space-y-2">${bars}</div>
      </div>
      <div class="flex flex-wrap gap-2">${pills}</div>
    </div>
  `;
}

function renderTiers() {
  return OUTREACH_TIERS.map((tier) => {
    const targets = OUTREACH_TARGETS.filter((t) => t.tier === tier.id);
    return renderTierSection(tier, targets);
  }).join('');
}

function wireEvents() {
  document.querySelectorAll('[data-nav]').forEach((el) => {
    el.addEventListener('click', () => navigate(el.dataset.nav));
  });

  document.querySelectorAll('.copy-msg-btn').forEach((el) => {
    el.addEventListener('click', () => {
      const text = decodeURIComponent(el.dataset.copy);
      navigator.clipboard?.writeText(text).then(() => {
        el.innerHTML = '<i class="fas fa-check mr-1"></i>COPIED';
        setTimeout(() => { el.innerHTML = '<i class="fas fa-copy mr-1"></i>COPY MESSAGE'; }, 2000);
      });
    });
  });
}
