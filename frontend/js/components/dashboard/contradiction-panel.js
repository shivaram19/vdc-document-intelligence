/**
 * contradiction-panel.js — Contradiction Scanner Panel
 *
 * SOLID: SRP — only contradiction scan UI and results rendering.
 *
 * [CITE: Ejiofor2025] Construction rework from document errors costs 5–15%
 * of project budget. Early contradiction detection prevents this.
 */

import { state } from '../../state.js';
import { sendCommand } from '../../ws.js';

export function renderContradictionPanelHTML() {
  return `
    <div class="card-glass rounded-2xl p-6">
      <div class="flex items-center justify-between mb-6">
        <div>
          <h3 class="font-semibold text-white"><i class="fas fa-exclamation-triangle mr-2 text-amber-400"></i>Drawing-Spec Contradictions</h3>
          <p class="text-sm text-slate-400 mt-1">The contradiction detector agent scans your documents for conflicts.</p>
        </div>
        <button id="contradiction-btn" class="px-5 py-3 bg-amber-600 hover:bg-amber-500 text-white font-semibold rounded-lg transition">
          <i class="fas fa-search mr-2"></i> Scan for Contradictions
        </button>
      </div>
      <div id="contradictions-output">
        <div class="p-8 text-center text-slate-500">
          <i class="fas fa-clipboard-check text-4xl mb-3 opacity-30"></i>
          <p>Upload both drawings and specifications, then click "Scan" to detect contradictions.</p>
        </div>
      </div>
    </div>
  `;
}

export function wireContradictionPanel() {
  document.getElementById('contradiction-btn')?.addEventListener('click', runContradictionCheck);

  window._renderScanResult = (ev) => {
    const btn = document.getElementById('contradiction-btn');
    if (btn) { btn.innerHTML = '<i class="fas fa-search mr-2"></i> Scan for Contradictions'; btn.disabled = false; }
    renderContradictions(ev);
  };
}

function runContradictionCheck() {
  if (!state.currentProject) return;
  const btn = document.getElementById('contradiction-btn');
  btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Agent scanning...';
  btn.disabled = true;
  sendCommand('scan', { project: state.currentProject }, false);
}

function renderContradictions(data) {
  const out = document.getElementById('contradictions-output');
  const items = data.contradictions || [];
  if (!items.length) {
    out.innerHTML = `
      <div class="p-6 text-center">
        <i class="fas fa-check-circle text-emerald-400 text-3xl mb-2"></i>
        <p class="text-slate-300 font-medium">${data.message || 'No contradictions found.'}</p>
        <p class="text-sm text-slate-500 mt-1">Checked ${data.checked_pairs || 0} document pairs.</p>
      </div>`;
    return;
  }
  out.innerHTML = `
    <div class="mb-4 flex items-center gap-2">
      <span class="px-3 py-1 rounded-full bg-amber-500/10 text-amber-400 text-xs font-medium border border-amber-500/20">
        <i class="fas fa-exclamation-triangle mr-1"></i>${items.length} potential issues found
      </span>
    </div>
    <div class="space-y-4">
      ${items.map((c) => `
        <div class="bg-slate-900/60 rounded-xl p-5 border border-amber-500/20 fade-in">
          <div class="flex items-center gap-2 mb-3">
            <span class="text-xs font-bold px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 uppercase">${c.severity || 'WARNING'}</span>
            <span class="text-xs text-slate-500">Confidence: ${Math.round((c.confidence || 0) * 100)}%</span>
          </div>
          <p class="text-sm text-white font-medium mb-3">${c.issue || c.unit || 'Contradiction detected'}</p>
          <div class="grid md:grid-cols-2 gap-4">
            <div class="bg-slate-800/50 rounded-lg p-3 border-l-2 border-blue-400">
              <p class="text-xs text-blue-400 font-medium mb-1">${c.spec_doc || c.documents?.[0] || 'Spec'}</p>
              <p class="text-xs text-slate-300">${c.spec_text || c.details?.[0]?.contexts?.[0] || ''}</p>
            </div>
            <div class="bg-slate-800/50 rounded-lg p-3 border-l-2 border-purple-400">
              <p class="text-xs text-purple-400 font-medium mb-1">${c.drawing_doc || c.documents?.[1] || 'Drawing'}</p>
              <p class="text-xs text-slate-300">${c.drawing_text || c.details?.[0]?.contexts?.[1] || ''}</p>
            </div>
          </div>
        </div>
      `).join('')}
    </div>`;
}
