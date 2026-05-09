/**
 * fleet-section.js — Agent Fleet Grid
 * SOLID: SRP — only fleet grid with navigation to agent pages.
 *
 * [CITE: ADR-005] Sora display font for headings.
 * [CITE: ADR-006] Tinted neutrals replace pure grays.
 * [CITE: ADR-007] Elevation-first card surfaces.
 */

import { AGENTS } from '../../data/agents.js';
import { navigate } from '../../router.js';

export function renderFleetSection() {
  const cards = AGENTS.map((a) => `
    <div class="card-structural cursor-pointer hover:border-bp-accent/60 transition" data-agent="${a.slug}">
      <div class="flex items-center justify-between mb-3">
        <div class="w-9 h-9 rounded-sm bg-${a.color}/10 flex items-center justify-center">
          <i class="fas ${a.icon} text-${a.color} text-sm"></i>
        </div>
        <span class="text-[10px] font-mono text-neutral-500 border border-neutral-700 px-2 py-0.5 rounded-sm">${a.role.toUpperCase()}</span>
      </div>
      <h3 class="text-base font-semibold font-display text-white mb-1">${a.name}</h3>
      <p class="text-xs text-neutral-400 mb-3 leading-relaxed">${a.problem}</p>
      <div class="flex items-center justify-between">
        <span class="type-label text-${a.color}">${a.metric}</span>
        <span class="text-[10px] text-bp-accent font-mono">VIEW PROFILE →</span>
      </div>
    </div>
  `).join('');

  return `
    <section class="py-20">
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-14">
          <h2 class="text-3xl font-bold font-display text-white mb-3">10-Agent Inspection Fleet</h2>
          <p class="text-neutral-400 max-w-2xl mx-auto">
            No single point of failure. Each agent specializes in one document control task.
            Click any card to see what it solves, how it works, and the proof behind it.
          </p>
        </div>
        <div class="grid md:grid-cols-2 lg:grid-cols-5 gap-3">
          ${cards}
        </div>
        <div class="mt-8 text-center">
          <span class="inline-flex items-center gap-2 text-sm text-neutral-500 font-mono">
            <span class="w-1.5 h-1.5 rounded-full bg-safe-green animate-pulse-slow"></span>
            10/10 AGENTS ONLINE — CONSENSUS THRESHOLD: 7/10
          </span>
        </div>
      </div>
    </section>
  `;
}

export function wireFleetEvents() {
  document.querySelectorAll('[data-agent]').forEach((el) => {
    el.addEventListener('click', () => navigate(`/agent/${el.dataset.agent}`));
  });
}
