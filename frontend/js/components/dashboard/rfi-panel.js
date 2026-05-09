/**
 * rfi-panel.js — RFI Draft Panel
 * SOLID: SRP — only RFI number input, question textarea, and draft output.
 */

import { state } from '../../state.js';
import { sendCommand } from '../../ws.js';

export function renderRFIPanelHTML() {
  return `
    <div class="grid lg:grid-cols-2 gap-4">
      <div class="card-structural">
        <h3 class="font-semibold text-white mb-4 flex items-center gap-2 font-mono text-sm">
          <i class="fas fa-pen-fancy text-bp-accent text-xs"></i> RFI DRAFT GENERATOR
        </h3>
        <div class="space-y-4">
          <div>
            <label class="text-sm text-neutral-500 block mb-1 font-mono">RFI NUMBER</label>
            <input id="rfi-number" type="text" value="RFI-006" class="w-full bg-bp-dark border border-bp-light/50 text-white text-sm rounded-sm px-3 py-2 focus:outline-none focus:border-bp-accent font-mono">
          </div>
          <div>
            <label class="text-sm text-neutral-500 block mb-1 font-mono">QUESTION / ISSUE</label>
            <textarea id="rfi-question" rows="4" class="w-full bg-bp-dark border border-bp-light/50 text-white text-sm rounded-sm px-3 py-2 focus:outline-none focus:border-bp-accent font-mono" placeholder="Describe the issue or question..."></textarea>
          </div>
          <button id="rfi-btn" class="w-full px-4 py-3 bg-bp-accent hover:bg-blue-500 text-white font-semibold rounded-sm transition font-mono">
            <i class="fas fa-file-signature mr-2"></i> DRAFT RFI RESPONSE
          </button>
        </div>
      </div>
      <div class="card-structural">
        <h3 class="font-semibold text-white mb-4 font-mono text-sm">DRAFTED RESPONSE</h3>
        <div id="rfi-draft-output" class="bg-bp-dark/50 rounded-sm p-4 text-sm text-neutral-300 whitespace-pre-wrap min-h-[200px] border border-bp-light/20 font-mono">
          <p class="text-neutral-600 italic">Your drafted RFI response will appear here with cited sources.</p>
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
    if (btn) { btn.innerHTML = '<i class="fas fa-file-signature mr-2"></i> DRAFT RFI RESPONSE'; btn.disabled = false; }
    let output = '';
    if (ev.contradictions?.length > 0) {
      output += `<div class="p-3 rounded-sm bg-safe-red/5 border border-safe-red/30 text-safe-red text-xs font-mono mb-3"><i class="fas fa-exclamation-triangle mr-2"></i>${ev.contradictions.length} CONTRADICTIONS FOUND DURING DRAFTING</div>`;
    }
    output += ev.draft ? ev.draft.replace(/\n/g, '<br>') : 'No draft generated.';
    const rfiOut = document.getElementById('rfi-draft-output');
    if (rfiOut) rfiOut.innerHTML = output;
    if (ev.sources) {
      const srcEl = document.getElementById('rfi-sources');
      if (srcEl) srcEl.innerHTML = `
        <p class="text-xs text-neutral-500 mb-2 font-mono">SOURCES USED:</p>
        <div class="flex flex-wrap gap-2">
          ${ev.sources.map((s) => `<span class="text-xs px-2 py-1 rounded-sm bg-bp-mid text-neutral-400 border border-bp-light/20 font-mono">${s.doc_name}</span>`).join('')}
        </div>`;
    }
  };
}

function draftRFI() {
  const num = document.getElementById('rfi-number').value;
  const q = document.getElementById('rfi-question').value.trim();
  if (!q || !state.currentProject) return;
  const btn = document.getElementById('rfi-btn');
  btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> DRAFTER AGENT WORKING...';
  btn.disabled = true;
  sendCommand('rfi', { project: state.currentProject, question: q, number: num }, false);
}
