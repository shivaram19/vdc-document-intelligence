/**
 * tier-section.js — Outreach Tier Section Renderer
 * SRP: Renders ONE tier section with target cards.
 */

import { renderTargetCard } from './target-card.js';

export function renderTierSection(tier, targets) {
  const cards = targets.map((t) => renderTargetCard(t)).join('');
  return `
    <details class="group mb-4" ${tier.id === 't3' ? 'open' : ''}>
      <summary class="card-structural cursor-pointer list-none">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-sm bg-bp-light/20 flex items-center justify-center text-bp-accent font-bold text-sm font-mono">${tier.id.toUpperCase()}</div>
            <div>
              <h3 class="text-sm font-bold text-white">${tier.name}</h3>
              <p class="text-[10px] text-gray-500 font-mono">${targets.length} TARGETS</p>
            </div>
          </div>
          <i class="fas fa-chevron-down text-gray-600 text-xs group-open:rotate-180 transition-transform"></i>
        </div>
        <p class="text-xs text-gray-400 mt-2">${tier.headline}</p>
        <p class="text-[10px] text-bp-accent mt-1 font-mono">${tier.cite}</p>
      </summary>
      <div class="mt-3 grid md:grid-cols-2 gap-3">${cards}</div>
    </details>
  `;
}
