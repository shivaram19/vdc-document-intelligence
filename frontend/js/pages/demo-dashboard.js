/**
 * demo-dashboard.js — Customer-Centric Live Demo
 *
 * [CITE: Krug2014] Time-to-Value: value must be visible in < 5 min.
 * Demo loads instantly with pre-indexed documents and pre-found contradictions.
 *
 * [CITE: NunesDreze2006] Endowed Progress: user sees "5 docs indexed,
 * 2 contradictions found" — they have already made progress.
 *
 * [CITE: NortonMochonAriely2012] IKEA Effect: user can upload 1 file.
 * They "build" the demo, increasing perceived value.
 */

import { state } from '../state.js';
import { navigate } from '../router.js';
import { renderDashboard } from './dashboard.js';
import { injectDemoProject, isDemo, use, canUse, demoUsage, resetDemoUsage } from '../demo/demo-state.js';
import { DEMO_QUICK_ANSWERS, DEMO_RFI_DRAFT, DEMO_PROJECT } from '../demo/sample-data.js';
import { renderDemoBanner, updateDemoBanner, renderGatePrompt, wireGatePrompt } from '../demo/gate-prompts.js';

export function renderDemo(container) {
  resetDemoUsage();
  state.testMode = true;
  state.authenticated = true;
  state.capabilities = ['can_query', 'can_draft_rfi', 'can_scan_contradictions', 'can_upload', 'can_manage_projects'];

  injectDemoProject(state);
  renderDashboard(container);

  // Append demo banner
  const banner = document.createElement('div');
  banner.innerHTML = renderDemoBanner();
  document.body.appendChild(banner.firstElementChild);

  // Wire demo banner CTA
  document.getElementById('demo-request-access')?.addEventListener('click', () => {
    navigate('/login');
  });

  // Override panel behaviors for demo
  hijackQueryPanel();
  hijackRFIPanel();
  hijackScanPanel();
  hijackInboxPanel();

  // Pre-fill agent log with demo context
  prefillAgentLog();
}

function prefillAgentLog() {
  const logEl = document.getElementById('agent-log');
  if (!logEl) return;
  const entries = [
    { icon: '📁', text: 'Demo project loaded: Demo Tower — Mixed-Use Development', time: new Date().toLocaleTimeString() },
    { icon: '📄', text: 'Ingested STRUCT_SPEC.txt (312 chunks)', time: new Date(Date.now() - 60000).toLocaleTimeString() },
    { icon: '📄', text: 'Ingested ARCH_DRAWING_NOTES.txt (198 chunks)', time: new Date(Date.now() - 55000).toLocaleTimeString() },
    { icon: '📄', text: 'Ingested MECH_SPEC_HVAC.txt (256 chunks)', time: new Date(Date.now() - 50000).toLocaleTimeString() },
    { icon: '⚠️', text: 'Spotter Agent found 2 contradictions', time: new Date(Date.now() - 45000).toLocaleTimeString() },
  ];
  logEl.innerHTML = entries.map((e) =>
    `<div class="flex items-center gap-2 text-xs text-slate-400 py-1 border-b border-slate-800/50">
      <span>${e.icon}</span><span class="flex-1">${e.text}</span><span class="text-slate-600">${e.time}</span>
    </div>`
  ).join('');
}

function hijackQueryPanel() {
  window._renderQueryResult = (ev) => {
    hideTyping();
    if (ev.contradictions?.length > 0) addContradictionBubble(ev.contradictions);
    addChatBubble(ev.answer || 'No answer found.', 'ai');
    renderSources(ev.sources || []);
  };

  // Override sendQuery for demo
  const origSendQuery = window._demoSendQuery;
  if (!origSendQuery) {
    window._demoSendQuery = true;
    const btn = document.getElementById('send-btn');
    const input = document.getElementById('query-input');

    if (btn) {
      const newBtn = btn.cloneNode(true);
      btn.parentNode.replaceChild(newBtn, btn);
      newBtn.addEventListener('click', demoSendQuery);
    }
    if (input) {
      const newInput = input.cloneNode(true);
      input.parentNode.replaceChild(newInput, input);
      newInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') demoSendQuery(); });
    }
  }
}

function demoSendQuery() {
  const input = document.getElementById('query-input');
  const query = input?.value.trim();
  if (!query) return;

  // Check if this matches a pre-loaded quick answer
  const matched = DEMO_QUICK_ANSWERS.find((a) =>
    query.toLowerCase().includes(a.q.toLowerCase().split(' ').slice(0, 3).join(' '))
  );

  if (matched) {
    addChatBubble(query, 'user');
    input.value = '';
    showTyping();
    setTimeout(() => {
      hideTyping();
      if (matched.contradictions) addContradictionBubble(matched.contradictions);
      addChatBubble(matched.a, 'ai');
      renderSources(matched.sources);
    }, 800);
    return;
  }

  // Custom query — check limit
  if (!canUse('customQueries')) {
    addChatBubble(query, 'user');
    input.value = '';
    const chatHistory = document.getElementById('chat-history');
    const gate = document.createElement('div');
    gate.className = 'fade-in';
    gate.innerHTML = renderGatePrompt('customQueries');
    chatHistory.appendChild(gate);
    wireGatePrompt(() => navigate('/login'));
    chatHistory.scrollTop = chatHistory.scrollHeight;
    updateDemoBanner(demoUsage);
    return;
  }

  use('customQueries');
  addChatBubble(query, 'user');
  input.value = '';
  showTyping();
  setTimeout(() => {
    hideTyping();
    addChatBubble('This is a demo response. In the full platform, Finder Agent would retrieve the most relevant spec clauses and drawing references for your query.', 'ai');
    renderSources([]);
    updateDemoBanner(demoUsage);
  }, 1200);
}

function hijackRFIPanel() {
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

  const btn = document.getElementById('rfi-btn');
  if (btn) {
    const newBtn = btn.cloneNode(true);
    btn.parentNode.replaceChild(newBtn, btn);
    newBtn.addEventListener('click', demoDraftRFI);
  }
}

function demoDraftRFI() {
  if (!canUse('rfiDrafts')) {
    const output = document.getElementById('rfi-draft-output');
    if (output) {
      const gate = document.createElement('div');
      gate.innerHTML = renderGatePrompt('rfiDrafts');
      output.appendChild(gate);
      wireGatePrompt(() => navigate('/login'));
      updateDemoBanner(demoUsage);
    }
    return;
  }

  const num = document.getElementById('rfi-number')?.value || 'RFI-007';
  const q = document.getElementById('rfi-question')?.value.trim();
  if (!q) return;

  use('rfiDrafts');
  const btn = document.getElementById('rfi-btn');
  btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> DRAFTER AGENT WORKING...';
  btn.disabled = true;

  setTimeout(() => {
    const ev = { ...DEMO_RFI_DRAFT, draft: DEMO_RFI_DRAFT.draft.replace(/RFI-007/g, num) };
    window._renderRFIResult(ev);
    updateDemoBanner(demoUsage);
  }, 1500);
}

function hijackScanPanel() {
  window._renderScanResult = (ev) => {
    const btn = document.getElementById('contradiction-btn');
    if (btn) { btn.innerHTML = '<i class="fas fa-search mr-2"></i> RUN INSPECTION SCAN'; btn.disabled = false; }
    renderContradictions(ev);
  };

  const btn = document.getElementById('contradiction-btn');
  if (btn) {
    const newBtn = btn.cloneNode(true);
    btn.parentNode.replaceChild(newBtn, btn);
    newBtn.addEventListener('click', demoScan);
  }
}

function demoScan() {
  if (!canUse('scans')) {
    const output = document.getElementById('contradictions-output');
    if (output) {
      const gate = document.createElement('div');
      gate.innerHTML = renderGatePrompt('scans');
      output.appendChild(gate);
      wireGatePrompt(() => navigate('/login'));
      updateDemoBanner(demoUsage);
    }
    return;
  }

  use('scans');
  const btn = document.getElementById('contradiction-btn');
  btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> SPOTTER AGENT SCANNING...';
  btn.disabled = true;

  setTimeout(() => {
    window._renderScanResult({
      contradictions: DEMO_PROJECT.contradictions,
      checked_pairs: DEMO_PROJECT.checked_pairs,
      message: '2 potential issues found across 12 document pairs.',
    });
    updateDemoBanner(demoUsage);
  }, 2000);
}

function hijackInboxPanel() {
  const dropzone = document.getElementById('upload-dropzone');
  const fileInput = document.getElementById('file-input');
  if (fileInput) {
    const newInput = fileInput.cloneNode(true);
    fileInput.parentNode.replaceChild(newInput, fileInput);
    newInput.addEventListener('change', function () {
      if (!canUse('uploads')) {
        const list = document.getElementById('upload-list');
        if (list) {
          const gate = document.createElement('div');
          gate.innerHTML = renderGatePrompt('uploads');
          list.appendChild(gate);
          wireGatePrompt(() => navigate('/login'));
          updateDemoBanner(demoUsage);
        }
        this.value = '';
        return;
      }
      use('uploads');
      // Simulate upload
      const list = document.getElementById('upload-list');
      const item = document.createElement('div');
      item.className = 'flex items-center gap-3 p-3 bg-bp-dark/50 rounded-sm border border-bp-light/20';
      item.innerHTML = `<i class="fas fa-file-alt text-bp-accent text-xs"></i><span class="text-sm text-white flex-1 font-mono">${this.files[0]?.name || 'uploaded.txt'}</span><span class="text-xs text-safe-green font-mono">DEMO — INDEXED</span>`;
      list.appendChild(item);
      updateDemoBanner(demoUsage);
      this.value = '';
    });
  }
}

// ---- Chat UI helpers (mirrored from query-panel.js) ----
function addChatBubble(text, sender) {
  const container = document.getElementById('chat-history');
  if (!container) return;
  const div = document.createElement('div');
  div.className = `fade-in ${sender === 'user' ? 'ml-auto bg-bp-accent/20 border-bp-accent/30' : 'bg-bp-dark/50 border-bp-light/20'} p-4 text-sm max-w-[85%] ${sender === 'user' ? 'max-w-[70%]' : ''} border rounded-sm`;
  if (sender === 'ai') {
    div.innerHTML = `<p class="font-mono text-xs text-bp-accent mb-1">AGENT RESPONSE</p>` + text.replace(/\n/g, '<br>');
  } else {
    div.innerHTML = text.replace(/\n/g, '<br>');
  }
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

function addContradictionBubble(contradictions) {
  const container = document.getElementById('chat-history');
  if (!container) return;
  const div = document.createElement('div');
  div.className = 'fade-in max-w-[85%]';
  div.innerHTML = `<div class="p-3 rounded-sm bg-safe-red/5 border border-safe-red/30 text-safe-red text-sm font-mono"><i class="fas fa-exclamation-triangle mr-2"></i>${contradictions.length} CONTRADICTIONS DETECTED — REVIEW REQUIRED</div>`;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

let typingEl = null;
function showTyping() {
  const container = document.getElementById('chat-history');
  if (!container) return;
  typingEl = document.createElement('div');
  typingEl.className = 'p-4 text-sm flex items-center gap-2 bg-bp-dark/50 border border-bp-light/20 rounded-sm font-mono text-neutral-500';
  typingEl.innerHTML = 'INSPECTING DOCUMENTS<span class="animate-pulse">...</span>';
  container.appendChild(typingEl);
  container.scrollTop = container.scrollHeight;
}
function hideTyping() {
  if (typingEl) { typingEl.remove(); typingEl = null; }
}

function renderSources(sources) {
  const panel = document.getElementById('sources-panel');
  if (!panel) return;
  if (!sources.length) {
    panel.innerHTML = '<p class="text-sm text-neutral-600 italic font-mono">No sources retrieved.</p>';
    return;
  }
  panel.innerHTML = sources.map((s, i) => `
    <div class="p-3 rounded-sm fade-in border border-bp-light/20 bg-bp-dark/30" style="animation-delay:${i * 0.1}s">
      <div class="flex items-center justify-between mb-1">
        <span class="text-xs font-medium text-bp-accent font-mono">${s.doc_name}</span>
        <span class="text-xs text-neutral-600 font-mono">${Math.round((s.score || 0.95) * 100)}% MATCH</span>
      </div>
      <p class="text-xs text-neutral-400 line-clamp-3">${s.text}</p>
      <span class="inline-block mt-1 text-[10px] px-2 py-0.5 rounded-sm bg-bp-mid text-neutral-500 font-mono border border-bp-light/20">${s.doc_type}</span>
    </div>
  `).join('');
}

function renderContradictions(data) {
  const out = document.getElementById('contradictions-output');
  if (!out) return;
  const items = data.contradictions || [];
  if (!items.length) {
    out.innerHTML = `
      <div class="p-6 text-center">
        <i class="fas fa-check-circle text-safe-green text-3xl mb-2"></i>
        <p class="text-neutral-300 font-medium font-mono">${data.message || 'NO CONTRADICTIONS FOUND'}</p>
        <p class="text-sm text-neutral-600 mt-1 font-mono">CHECKED ${data.checked_pairs || 0} DOCUMENT PAIRS</p>
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
            <span class="text-xs text-neutral-600 font-mono">CONFIDENCE: ${Math.round((c.confidence || 0) * 100)}%</span>
          </div>
          <p class="text-sm text-white font-medium mb-3">${c.issue || 'Contradiction detected'}</p>
          <div class="grid md:grid-cols-2 gap-3">
            <div class="bg-bp-dark/50 rounded-sm p-3 border-l-2 border-bp-accent">
              <p class="text-xs text-bp-accent font-medium mb-1 font-mono">${c.spec_doc || 'SPEC'}</p>
              <p class="text-xs text-neutral-400">${c.spec_text || ''}</p>
            </div>
            <div class="bg-bp-dark/50 rounded-sm p-3 border-l-2 border-safe-orange">
              <p class="text-xs text-safe-orange font-medium mb-1 font-mono">${c.drawing_doc || 'DRAWING'}</p>
              <p class="text-xs text-neutral-400">${c.drawing_text || ''}</p>
            </div>
          </div>
          ${c.impact ? `<p class="text-xs text-safe-orange mt-2 font-mono"><i class="fas fa-dollar-sign mr-1"></i>ESTIMATED IMPACT: ${c.impact}</p>` : ''}
        </div>
      `).join('')}
    </div>`;
}
