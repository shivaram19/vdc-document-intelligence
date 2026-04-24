/**
 * rfi-panel.js — RFI Draft Panel
 *
 * SOLID: SRP — only RFI number input, question textarea, and draft output.
 */

import { state } from '../../state.js';
import { sendCommand } from '../../ws.js';

export function renderRFIPanelHTML() {
  return `
    <div class="grid lg:grid-cols-2 gap-6">
      <div class="card-glass rounded-2xl p-6">
        <h3 class="font-semibold text-white mb-4"><i class="fas fa-pen-fancy mr-2 text-purple-400"></i>RFI Draft Generator</h3>
        <div class="space-y-4">
          <div>
            <label class="text-sm text-slate-400 block mb-1">RFI Number</label>
            <input id="rfi-number" type="text" value="RFI-006" class="w-full bg-slate-800 border border-slate-600 text-white text-sm rounded-lg px-3 py-2 focus:outline-none focus:border-purple-500">
          </div>
          <div>
            <label class="text-sm text-slate-400 block mb-1">Question / Issue</label>
            <textarea id="rfi-question" rows="4" class="w-full bg-slate-800 border border-slate-600 text-white text-sm rounded-lg px-3 py-2 focus:outline-none focus:border-purple-500" placeholder="Describe the issue or question..."></textarea>
          </div>
          <button id="rfi-btn" class="w-full px-4 py-3 bg-purple-600 hover:bg-purple-500 text-white font-semibold rounded-lg transition">
            <i class="fas fa-magic mr-2"></i> Auto-Draft Response
          </button>
        </div>
      </div>
      <div class="card-glass rounded-2xl p-6">
        <h3 class="font-semibold text-white mb-4">Drafted Response</h3>
        <div id="rfi-draft-output" class="bg-slate-800/50 rounded-lg p-4 text-sm text-slate-300 whitespace-pre-wrap min-h-[200px]">
          <p class="text-slate-500 italic">Your auto-drafted RFI response will appear here.</p>
        </div>
        <div id="rfi-sources" class="mt-4"></div>
      </div>
    </div>
  `;
}

export function wireRFIPanel() {
  document.getElementById('rfi-btn')?.addEventListener('click', draftRFI);

  window._renderRFIResult = (ev) => {
    const btn = document.getElementById('rfi-btn');
    if (btn) { btn.innerHTML = '<i class="fas fa-magic mr-2"></i> Auto-Draft Response'; btn.disabled = false; }
    let output = '';
    if (ev.contradictions?.length > 0) {
      output += `<div class="contradiction-banner"><strong>⚠️ Contradictions:</strong> ${ev.contradictions.length} found during drafting.</div>`;
    }
    output += ev.draft ? ev.draft.replace(/\n/g, '<br>') : 'No draft generated.';
    const rfiOut = document.getElementById('rfi-draft-output');
    if (rfiOut) rfiOut.innerHTML = output;
    if (ev.sources) {
      const srcEl = document.getElementById('rfi-sources');
      if (srcEl) srcEl.innerHTML = `
        <p class="text-xs text-slate-400 mb-2">Sources used:</p>
        <div class="flex flex-wrap gap-2">
          ${ev.sources.map((s) => `<span class="text-xs px-2 py-1 rounded bg-slate-700 text-slate-300">${s.doc_name}</span>`).join('')}
        </div>`;
    }
  };
}

function draftRFI() {
  const num = document.getElementById('rfi-number').value;
  const q = document.getElementById('rfi-question').value.trim();
  if (!q || !state.currentProject) return;
  const btn = document.getElementById('rfi-btn');
  btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Agent drafting...';
  btn.disabled = true;
  sendCommand('rfi', { project: state.currentProject, question: q, number: num }, false);
}
