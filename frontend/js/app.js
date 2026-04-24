/**
 * app.js — Application Bootstrapper
 *
 * SOLID Compliance:
 *   S: Only bootstraps. No business logic.
 *   O: New routes added via register() without modifying this file.
 *   D: Depends on router abstraction, not concrete pages.
 *
 * Research basis:
 *   [CITE: Nielsen1994] Visibility of system status — real-time connection
 *   state must be visible to user at all times.
 *   [CITE: Mondal2015] Trust function must be initialized at session start
 *   and updated on EVERY subsequent action.
 *   [CITE: Li2024] Role specialization (Solvability principle) — app.js
 *   ONLY bootstraps; all logic delegated to specialized modules.
 */

import { register, navigate, renderCurrentRoute } from './router.js';
import { connect, onWsEvent } from './ws.js';
import { state } from './state.js';
import { createFingerprint } from './auth/index.js';

// Page imports — each page is a single-responsibility module
import { renderLanding } from './pages/landing.js';
import { renderLogin } from './pages/login.js';
import { renderDashboard } from './pages/dashboard.js';

// ---------------------------------------------------------------------------
// Route Registration (Open/Closed: add routes without touching core logic)
// ---------------------------------------------------------------------------
register('/', renderLanding);
register('/login', renderLogin);
register('/dashboard', renderDashboard);

const fingerprint = createFingerprint();

function init() {
  // Start behavioral fingerprinting BEFORE auth (baseline collection)
  fingerprint.start();

  // Start WebSocket connection
  connect();

  // Listen for all agent events and update reactive state
  onWsEvent(handleWsEvent);

  // Route based on hash
  const hash = window.location.hash || '#/'; // default to landing, not login
  navigate(hash.replace('#', ''));
}

function handleWsEvent(ev) {
  switch (ev.type) {
    case 'ws_connected':
      state.connected = true;
      break;
    case 'ws_disconnected':
      state.connected = false;
      state.authenticated = false;
      break;
    case 'auth_success':
      state.authenticated = true;
      state.capabilities = ev.capabilities || [];
      addAgentLog('🔐', 'Authenticated via knowledge proof');
      break;
    case 'auth_failed':
      state.authenticated = false;
      addAgentLog('❌', `Auth failed: ${ev.reason || 'Unknown'}`);
      break;
    case 'rechallenge_required':
      state.authenticated = false;
      addAgentLog('⚠️', `Re-authentication required: ${ev.reason || 'Anomaly detected'}`);
      break;
    case 'state_snapshot':
      state.projects = ev.state?.projects || [];
      updateProjectSelector();
      break;
    case 'project_created':
      state.projects.push(ev.project);
      updateProjectSelector();
      addAgentLog('📁', `Project created: ${ev.project?.name}`);
      break;
    case 'document_ingested':
      addAgentLog('📄', `Ingested ${ev.doc_name} (${ev.chunk_count} chunks)`);
      break;
    case 'query_result':
      state.agentStatus = 'idle';
      if (window._renderQueryResult) window._renderQueryResult(ev);
      break;
    case 'rfi_result':
      state.agentStatus = 'idle';
      if (window._renderRFIResult) window._renderRFIResult(ev);
      break;
    case 'scan_result':
      state.agentStatus = 'idle';
      if (window._renderScanResult) window._renderScanResult(ev);
      break;
    case 'command_received':
      state.agentStatus = 'working';
      addAgentLog('⚙️', `${ev.action} on ${ev.project}`);
      break;
    case 'workflow_complete':
      state.agentStatus = 'idle';
      addAgentLog('✅', `${ev.workflow} complete (${ev.duration_sec}s)`);
      break;
    case 'error':
      state.agentStatus = 'error';
      addAgentLog('❌', `Error: ${ev.error}`);
      break;
  }
  updateStatusIndicator();
}

// ---------------------------------------------------------------------------
// UI Utilities (Single Responsibility: state reflection only)
// ---------------------------------------------------------------------------
function updateProjectSelector() {
  const sel = document.getElementById('project-select');
  if (!sel) return;
  if (state.projects.length === 0) {
    sel.innerHTML = '<option value="">No projects</option>';
    return;
  }
  sel.innerHTML = state.projects.map((p) => {
    const docCount = p.docs?.length || p.document_count || 0;
    return `<option value="${p.id}">${p.name} (${docCount} docs)</option>`;
  }).join('');
  if (state.currentProject) sel.value = state.currentProject;
}

function updateStatusIndicator() {
  const el = document.getElementById('agent-status');
  if (!el) return;

  if (!state.connected) {
    el.innerHTML = statusBadge('red', 'Agent Mesh Offline');
    el.className = statusClass('red');
  } else if (!state.authenticated) {
    el.innerHTML = statusBadge('amber', 'Auth Required');
    el.className = statusClass('amber');
  } else if (state.agentStatus === 'working') {
    el.innerHTML = statusBadge('amber', 'Agent Working...', true);
    el.className = statusClass('amber');
  } else {
    el.innerHTML = statusBadge('emerald', 'Agent Mesh Online', true);
    el.className = statusClass('emerald');
  }
}

function statusBadge(color, text, pulse = false) {
  return `<span class="w-2 h-2 rounded-full bg-${color}-400${pulse ? ' animate-pulse' : ''}"></span>${text}`;
}

function statusClass(color) {
  return `flex items-center gap-2 text-xs px-3 py-1 rounded-full bg-${color}-500/10 text-${color}-400 border border-${color}-500/20`;
}

function addAgentLog(icon, text) {
  state.recentEvents.unshift({ icon, text, time: new Date().toLocaleTimeString() });
  if (state.recentEvents.length > 50) state.recentEvents.pop();
  const logEl = document.getElementById('agent-log');
  if (logEl) {
    logEl.innerHTML = state.recentEvents.map((e) =>
      `<div class="flex items-center gap-2 text-xs text-slate-400 py-1 border-b border-slate-800/50">
        <span>${e.icon}</span><span class="flex-1">${e.text}</span><span class="text-slate-600">${e.time}</span>
      </div>`
    ).join('');
  }
}

init();
