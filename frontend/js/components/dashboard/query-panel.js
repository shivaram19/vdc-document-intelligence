/**
 * query-panel.js — Query Chat Interface
 * SOLID: SRP — only query input, chat history, and sources display.
 */

import { state } from '../../state.js';
import { sendCommand } from '../../ws.js';

export function renderQueryPanelHTML() {
  return `
    <div class="grid lg:grid-cols-3 gap-4">
      <div class="lg:col-span-2 card-structural flex flex-col" style="min-height: 500px;">
        <div id="chat-history" class="flex-1 overflow-y-auto space-y-4 mb-4 pr-2" style="max-height: 500px;">
          <div class="p-4 text-sm border border-bp-light/20 rounded-sm bg-bp-dark/50">
            <p class="font-medium text-bp-accent mb-1 flex items-center gap-2 font-mono text-xs">
              <i class="fas fa-robot"></i> AGENT FLEET — FINDER + LIBRARIAN
            </p>
            <p class="text-gray-400">Ask anything about your project documents. Sources are cited with every answer.</p>
            <div class="mt-3 flex flex-wrap gap-2">
              <button class="quick-query-btn text-xs px-2 py-1 rounded-sm bg-bp-mid hover:bg-bp-light/30 text-gray-400 transition border border-bp-light/20 font-mono" data-q="What is the HVAC temperature setpoint for office spaces?">HVAC setpoints?</button>
              <button class="quick-query-btn text-xs px-2 py-1 rounded-sm bg-bp-mid hover:bg-bp-light/30 text-gray-400 transition border border-bp-light/20 font-mono" data-q="What are the fire protection sprinkler requirements?">Fire sprinkler specs?</button>
              <button class="quick-query-btn text-xs px-2 py-1 rounded-sm bg-bp-mid hover:bg-bp-light/30 text-gray-400 transition border border-bp-light/20 font-mono" data-q="What is the concrete strength for columns?">Column concrete psi?</button>
              <button class="quick-query-btn text-xs px-2 py-1 rounded-sm bg-bp-mid hover:bg-bp-light/30 text-gray-400 transition border border-bp-light/20 font-mono" data-q="What are the live loads for mechanical rooms?">Mechanical room loads?</button>
            </div>
          </div>
        </div>
        <div class="flex gap-3">
          <input id="query-input" type="text" placeholder="Ask about your project documents..."
            class="flex-1 bg-bp-dark border border-bp-light/50 text-white text-sm rounded-sm px-4 py-3 focus:outline-none focus:border-bp-accent font-mono">
          <button id="send-btn" class="px-5 py-3 bg-bp-accent hover:bg-blue-500 text-white rounded-sm transition">
            <i class="fas fa-paper-plane"></i>
          </button>
        </div>
      </div>
      <div class="card-structural">
        <h3 class="font-semibold text-white mb-4 text-sm flex items-center gap-2 font-mono">
          <i class="fas fa-book-open text-bp-accent text-xs"></i> RETRIEVED SOURCES
        </h3>
        <div id="sources-panel" class="space-y-3">
          <p class="text-sm text-gray-600 italic font-mono">Sources will appear here after you ask a question.</p>
        </div>
      </div>
    </div>
  `;
}

export function wireQueryPanel() {
  document.getElementById('send-btn')?.addEventListener('click', sendQuery);
  document.getElementById('query-input')?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendQuery();
  });
  document.querySelectorAll('.quick-query-btn').forEach((btn) => {
    btn.addEventListener('click', () => quickQuery(btn.dataset.q));
  });

  window._renderQueryResult = (ev) => {
    hideTyping();
    if (ev.contradictions?.length > 0) addContradictionBubble(ev.contradictions);
    addChatBubble(ev.answer || 'No answer found.', 'ai');
    renderSources(ev.sources || []);
  };
}

function sendQuery() {
  const input = document.getElementById('query-input');
  const query = input.value.trim();
  if (!query || !state.currentProject) return;
  addChatBubble(query, 'user');
  input.value = '';
  showTyping();
  sendCommand('query', { project: state.currentProject, query, top_k: 5 }, false);
}

function quickQuery(q) {
  document.getElementById('query-input').value = q;
  sendQuery();
}

function addChatBubble(text, sender) {
  const container = document.getElementById('chat-history');
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
  const div = document.createElement('div');
  div.className = 'fade-in max-w-[85%]';
  div.innerHTML = `<div class="p-3 rounded-sm bg-safe-red/5 border border-safe-red/30 text-safe-red text-sm font-mono"><i class="fas fa-exclamation-triangle mr-2"></i>${contradictions.length} CONTRADICTIONS DETECTED — REVIEW REQUIRED</div>`;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

let typingEl = null;
function showTyping() {
  const container = document.getElementById('chat-history');
  typingEl = document.createElement('div');
  typingEl.className = 'p-4 text-sm flex items-center gap-2 bg-bp-dark/50 border border-bp-light/20 rounded-sm font-mono text-gray-500';
  typingEl.innerHTML = 'INSPECTING DOCUMENTS<span class="animate-pulse">...</span>';
  container.appendChild(typingEl);
  container.scrollTop = container.scrollHeight;
}
function hideTyping() {
  if (typingEl) { typingEl.remove(); typingEl = null; }
}

function renderSources(sources) {
  const panel = document.getElementById('sources-panel');
  if (!sources.length) {
    panel.innerHTML = '<p class="text-sm text-gray-600 italic font-mono">No sources retrieved.</p>';
    return;
  }
  panel.innerHTML = sources.map((s, i) => `
    <div class="p-3 rounded-sm fade-in border border-bp-light/20 bg-bp-dark/30" style="animation-delay:${i * 0.1}s">
      <div class="flex items-center justify-between mb-1">
        <span class="text-xs font-medium text-bp-accent font-mono">${s.doc_name}</span>
        <span class="text-xs text-gray-600 font-mono">${Math.round(s.score * 100)}% MATCH</span>
      </div>
      <p class="text-xs text-gray-400 line-clamp-3">${s.text}</p>
      <span class="inline-block mt-1 text-[10px] px-2 py-0.5 rounded-sm bg-bp-mid text-gray-500 font-mono border border-bp-light/20">${s.doc_type}</span>
    </div>
  `).join('');
}
