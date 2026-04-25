/**
 * step-1-sources.js — Step 1: Choose Source
 *
 * SRP: Renders ONLY the source selection step.
 * OCP: Add sources to SOURCES data; this file needs no changes.
 */

import { SOURCES, PRIMARY_SOURCE_IDS } from '../../data/connector-sources.js';
import { renderStatusBadge } from './shared.js';

function sourceCard(s) {
  return `
    <div class="source-card card-structural border-bp-light/30 cursor-pointer hover:border-bp-accent transition group" data-source="${s.id}">
      <div class="flex items-start justify-between mb-3">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-sm bg-bp-light/10 flex items-center justify-center text-bp-accent group-hover:bg-bp-accent/20 transition">
            <i class="fas ${s.icon}"></i>
          </div>
          <div>
            <h3 class="text-sm font-bold text-white">${s.name}</h3>
            <p class="text-[10px] text-gray-500 font-mono">${s.subtitle}</p>
          </div>
        </div>
        ${renderStatusBadge(s.status)}
      </div>
      <p class="text-xs text-gray-500 leading-relaxed">${s.why}</p>
    </div>
  `;
}

function renderSampleOffer() {
  return `
    <div class="mt-8 card-structural border-bp-accent/50 bg-bp-accent/5">
      <div class="flex items-start gap-4">
        <div class="w-10 h-10 rounded-sm bg-bp-accent/20 flex items-center justify-center text-bp-accent flex-shrink-0">
          <i class="fas fa-bolt"></i>
        </div>
        <div>
          <h3 class="text-sm font-bold text-white mb-1">Not Ready to Connect? Start with Sample Data</h3>
          <p class="text-xs text-gray-400 leading-relaxed mb-3">
            We'll pre-load a real construction project with 5 documents and 2 pre-found contradictions.
            You can query instantly — no upload needed.
            <span class="text-gray-600 text-[10px] block mt-1">[CITE: NunesDreze2006] Endowed progress increases completion by 30-40%.</span>
          </p>
          <button data-sample class="btn-inspect font-mono text-xs">
            <i class="fas fa-play mr-2"></i>START WITH SAMPLE PROJECT
          </button>
        </div>
      </div>
    </div>
  `;
}

export function renderStep1() {
  const primary = SOURCES.filter((s) => PRIMARY_SOURCE_IDS.includes(s.id));
  const more = SOURCES.filter((s) => !PRIMARY_SOURCE_IDS.includes(s.id));

  return `
    <div>
      <div class="text-center mb-8">
        <h2 class="text-2xl font-bold text-white mb-2">Where Do Your Drawings Live?</h2>
        <p class="text-sm text-gray-400 max-w-lg mx-auto">
          We connect to your existing tools — no migration needed.
          <span class="text-bp-accent">Why?</span> Because replacing 11 platforms takes 18 months.
          Adding an inspection layer takes 20 minutes.
          <span class="text-gray-600 text-xs block mt-1">[CITE: Autodesk2022]</span>
        </p>
      </div>
      <div class="grid md:grid-cols-2 gap-4 mb-6">
        ${primary.map(sourceCard).join('')}
      </div>
      <details class="group">
        <summary class="text-xs text-gray-500 font-mono cursor-pointer hover:text-gray-300 transition list-none flex items-center gap-2">
          <i class="fas fa-chevron-right text-[10px] group-open:rotate-90 transition-transform"></i>
          MORE SOURCES
        </summary>
        <div class="grid md:grid-cols-2 gap-4 mt-4">
          ${more.map(sourceCard).join('')}
        </div>
      </details>
      ${renderSampleOffer()}
    </div>
  `;
}
