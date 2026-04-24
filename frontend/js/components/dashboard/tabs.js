/**
 * tabs.js — Tab Navigation
 * SOLID: SRP — only tab switching logic.
 */

import { state } from '../../state.js';

export function renderTabsHTML() {
  return `
    <div class="flex border-b border-bp-light/30 mb-6 font-mono text-sm">
      <button data-tab="query" class="tab-btn px-5 py-3 font-medium tab-active transition">Ask Documents</button>
      <button data-tab="rfi" class="tab-btn px-5 py-3 font-medium tab-inactive transition">Draft RFI</button>
      <button data-tab="contradictions" class="tab-btn px-5 py-3 font-medium tab-inactive transition">Contradictions</button>
      <button data-tab="upload" class="tab-btn px-5 py-3 font-medium tab-inactive transition">Inbox</button>
    </div>
  `;
}

export function wireTabs() {
  document.querySelectorAll('.tab-btn').forEach((btn) => {
    btn.addEventListener('click', () => switchTab(btn.dataset.tab));
  });
}

export function switchTab(tab) {
  state.currentTab = tab;
  document.querySelectorAll('.tab-panel').forEach((p) => p.classList.add('hidden'));
  document.getElementById(`panel-${tab}`)?.classList.remove('hidden');
  document.querySelectorAll('.tab-btn').forEach((t) => {
    t.classList.remove('tab-active');
    t.classList.add('tab-inactive');
  });
  const active = document.querySelector(`.tab-btn[data-tab="${tab}"]`);
  if (active) { active.classList.add('tab-active'); active.classList.remove('tab-inactive'); }
}
