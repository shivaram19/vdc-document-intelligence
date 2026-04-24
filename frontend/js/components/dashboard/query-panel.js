/**
 * query-panel.js — Query Chat Interface
 *
 * SOLID: SRP — only query input, chat history, and sources display.
 *
 * [CITE: Nielsen1994] Visibility of system status — show typing indicator
 * while agent is working.
 * [CITE: Papaioannou2023] LLM outputs must cite sources to prevent
 * hallucination distrust.
 */

import { state } from '../../state.js';
import { sendCommand } from '../../ws.js';

export function renderQueryPanelHTML() {
  return `
    <div class="grid lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 card-glass rounded-2xl p-6 flex flex-col" style="min-height: 500px;">
        <div id="chat-history" class="flex-1 overflow-y-auto space-y-4 mb-4 pr-2" style="max-height: 500px;">
          <div class="chat-bubble-ai p-4 text-sm">
            <p class="font-medium text-blue-400 mb-1"><i class="fas fa-robot mr-1"></i> Medha (Agent Mesh)</p>
            <p>I'm the agent fleet's curiosity brain. Ask me anything about your project documents.</p>
            <div class="mt-3 flex flex-wrap gap-2">
              <button class="quick-query-btn text-xs px-2 py-1 rounded bg-slate-700 hover:bg-slate-600 text-slate-300 transition" data-q="What is the HVAC temperature setpoint for office spaces?">HVAC setpoints?</button>
              <button class="quick-query-btn text-xs px-2 py-1 rounded bg-slate-700 hover:bg-slate-600 text-slate-300 transition" data-q="What are the fire protection sprinkler requirements?">Fire sprinkler specs?</button>
              <button class="quick-query-btn text-xs px-2 py-1 rounded bg-slate-700 hover:bg-slate-600 text-slate-300 transition" data-q="What is the concrete strength for columns?">Column concrete psi?</button>
              <button class="quick-query-btn text-xs px-2 py-1 rounded bg-slate-700 hover:bg-slate-600 text-slate-300 transition" data-q="What are the live loads for mechanical rooms?">Mechanical room loads?</button>
            </div>
          </div>
        </div>
        <div class="flex gap-3">
          <input id="query-input" type="text" placeholder="Ask about your project documents..."
            class="flex-1 bg-slate-800 border border-slate-600 text-white text-sm rounded-lg px-4 py-3 focus:outline-none focus:border-blue-500">
          <button id="send-btn" class="px-5 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition">
            <i class="fas fa-paper-plane"></i>
          </button>
        </div>
      </div>
      <div class="card-glass rounded-2xl p-6">
        <h3 class="font-semibold text-white mb-4 text-sm"><i class="fas fa-book-open mr-2 text-blue-400"></i>Retrieved Sources</h3>
        <div id="sources-panel" class="space-y-3">
          <p class="text-sm text-slate-500 italic">Sources will appear here after you ask a question.</p>
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
  div.className = `fade-in ${sender === 'user' ? 'chat-bubble-user ml-auto' : 'chat-bubble-ai'} p-4 text-sm max-w-[85%] ${sender === 'user' ? 'max-w-[70%]' : ''}`;
  div.innerHTML = text.replace(/\n/g, '<br>');
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

function addContradictionBubble(contradictions) {
  const container = document.getElementById('chat-history');
  const div = document.createElement('div');
  div.className = 'fade-in max-w-[85%]';
  // Note: renderContradictionBanner imported at dashboard level to avoid circular deps
  div.innerHTML = `<div class="contradiction-banner"><strong>⚠️ Contradictions detected:</strong> ${contradictions.length} potential conflicts found.</div>`;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

let typingEl = null;
function showTyping() {
  const container = document.getElementById('chat-history');
  typingEl = document.createElement('div');
  typingEl.className = 'chat-bubble-ai p-4 text-sm flex items-center gap-2';
  typingEl.innerHTML = '<span class="typing-dot w-2 h-2 bg-slate-400 rounded-full"></span><span class="typing-dot w-2 h-2 bg-slate-400 rounded-full"></span><span class="typing-dot w-2 h-2 bg-slate-400 rounded-full"></span>';
  container.appendChild(typingEl);
  container.scrollTop = container.scrollHeight;
}
function hideTyping() {
  if (typingEl) { typingEl.remove(); typingEl = null; }
}

function renderSources(sources) {
  const panel = document.getElementById('sources-panel');
  if (!sources.length) {
    panel.innerHTML = '<p class="text-sm text-slate-500 italic">No sources retrieved.</p>';
    return;
  }
  panel.innerHTML = sources.map((s, i) => `
    <div class="source-card p-3 rounded-lg fade-in" style="animation-delay:${i * 0.1}s">
      <div class="flex items-center justify-between mb-1">
        <span class="text-xs font-medium text-blue-400">${s.doc_name}</span>
        <span class="text-xs text-slate-500">${Math.round(s.score * 100)}% match</span>
      </div>
      <p class="text-xs text-slate-300 line-clamp-3">${s.text}</p>
      <span class="inline-block mt-1 text-[10px] px-2 py-0.5 rounded bg-slate-700 text-slate-400">${s.doc_type}</span>
    </div>
  `).join('');
}
