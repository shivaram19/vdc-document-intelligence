/**
 * contradiction-panel.js — Contradiction Scanner Panel
 * SOLID: SRP — only contradiction scan UI and results rendering.
 *
 * [CITE: Ejiofor2025] Construction rework from document errors costs 5–15%
 * of project budget. Early contradiction detection prevents this.
 */

import { state } from '../../state.js';
import { sendCommand } from '../../ws.js';

export function renderContradictionPanelHTML() {
  return `
    <div class="card-structural">
      <div class="flex items-center justify-between mb-6">
        <div>
          <h3 class="font-semibold text-white flex items-center gap-2 font-mono text-sm">
            <i class="fas fa-exclamation-triangle text-safe-yellow text-xs"></i> DRAWING-SPEC CONTRADICTIONS
          </h3>
          <p class="text-sm text-gray-500 mt-1">Spotter Agent scans your documents for conflicts that cause rework.</p>
        </div>
        <button id="contradiction-btn" class="px-5 py-3 bg-safe-orange hover:bg-orange-500 text-white font-semibold rounded-sm transition font-mono">
          <i class="fas fa-search mr-2"></i> RUN INSPECTION SCAN
        </button>
      </div>
      <div id="contradictions-output">
        <div class="p-8 text-center text-gray-600">
          <i class="fas fa-clipboard-check text-4xl mb-3 opacity-30"></i>
          <p class="font-mono text-sm">Upload drawings and specifications, then run scan to detect contradictions.</p>
        </div>
      </div>
    </div>
  `;
}

export function wireContradictionPanel() {
  document.getElementById('contradiction-btn')?.addEventListener('click', runContradictionCheck);

  window._renderScanResult = (ev) => {
    const btn = document.getElementById('contradiction-btn');
    if (btn) { btn.innerHTML = '<i class="fas fa-search mr-2"></i> RUN INSPECTION SCAN'; btn.disabled = false; }
    renderContradictions(ev);
  };
}

function runContradictionCheck() {
  if (!state.currentProject) return;
  const btn = document.getElementById('contradiction-btn');
  btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> SPOTTER AGENT SCANNING...';
  btn.disabled = true;
  sendCommand('scan', { project: state.currentProject }, false);
}

function renderContradictions(data) {
  const out = document.getElementById('contradictions-output');
  const items = data.contradictions || [];
  if (!items.length) {
    out.innerHTML = `
      <div class="p-6 text-center">
        <i class="fas fa-check-circle text-safe-green text-3xl mb-2"></i>
        <p class="text-gray-300 font-medium font-mono">${data.message || 'NO CONTRADICTIONS FOUND'}</p>
        <p class="text-sm text-gray-600 mt-1 font-mono">CHECKED ${data.checked_pairs || 0} DOCUMENT PAIRS</p>
      </div>`;
    return;
  }
  out.innerHTML = `
    <div class="mb-4 flex items-center gap-2">
      <span class="badge-warn font-mono">
        <i class="fas fa-exclamation-triangle mr-1"></i>${items.length} POTENTIAL ISSUES FOUND
      </span>
    </div>
    <div class="space-y-3">
      ${items.map((c) => `
        <div class="bg-bp-dark/60 rounded-sm p-5 border border-safe-yellow/20 fade-in">
          <div class="flex items-center gap-2 mb-3">
            <span class="text-xs font-bold px-2 py-0.5 rounded-sm bg-safe-orange/10 text-safe-orange uppercase font-mono">${c.severity || 'WARNING'}</span>
            <span class="text-xs text-gray-600 font-mono">CONFIDENCE: ${Math.round((c.confidence || 0) * 100)}%</span>
          </div>
          <p class="text-sm text-white font-medium mb-3">${c.issue || c.unit || 'Contradiction detected'}</p>
          <div class="grid md:grid-cols-2 gap-3">
            <div class="bg-bp-dark/50 rounded-sm p-3 border-l-2 border-bp-accent">
              <p class="text-xs text-bp-accent font-medium mb-1 font-mono">${c.spec_doc || c.documents?.[0] || 'SPEC'}</p>
              <p class="text-xs text-gray-400">${c.spec_text || c.details?.[0]?.contexts?.[0] || ''}</p>
            </div>
            <div class="bg-bp-dark/50 rounded-sm p-3 border-l-2 border-safe-orange">
              <p class="text-xs text-safe-orange font-medium mb-1 font-mono">${c.drawing_doc || c.documents?.[1] || 'DRAWING'}</p>
              <p class="text-xs text-gray-400">${c.drawing_text || c.details?.[0]?.contexts?.[1] || ''}</p>
            </div>
          </div>
        </div>
      `).join('')}
    </div>`;
}
