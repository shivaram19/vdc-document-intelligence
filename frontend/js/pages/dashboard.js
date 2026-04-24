/**
 * dashboard.js — Dashboard Orchestrator
 * SOLID: SRP — composes sections, wires events.
 */

import { clearApiKey } from '../config.js';
import { state } from '../state.js';
import { navigate } from '../router.js';
import { TokenManager } from '../auth/token_manager.js';

import { renderHeaderHTML } from '../components/dashboard/header.js';
import { renderDashboardHeroHTML } from '../components/dashboard/hero.js';
import { renderAuthMeshStatusHTML, updateAuthMeshStatus } from '../components/dashboard/auth-mesh-status.js';
import { renderProjectSelectorHTML, renderNewProjectModalHTML, wireProjectSelector, selectProject } from '../components/dashboard/project-selector.js';
import { renderTabsHTML, wireTabs } from '../components/dashboard/tabs.js';
import { renderQueryPanelHTML, wireQueryPanel } from '../components/dashboard/query-panel.js';
import { renderRFIPanelHTML, wireRFIPanel } from '../components/dashboard/rfi-panel.js';
import { renderContradictionPanelHTML, wireContradictionPanel } from '../components/dashboard/contradiction-panel.js';
import { renderInboxPanelHTML, wireInboxPanel } from '../components/dashboard/inbox-panel.js';

export function renderDashboard(container) {
  container.innerHTML = `
    <div class="min-h-screen blueprint-bg text-gray-200 font-sans">
      ${renderHeaderHTML()}
      ${renderDashboardHeroHTML()}
      ${renderAuthMeshStatusHTML()}
      <section id="demo" class="max-w-7xl mx-auto px-6 pb-16">
        ${renderProjectSelectorHTML()}
        ${renderTabsHTML()}
        <div id="panel-query" class="tab-panel">${renderQueryPanelHTML()}</div>
        <div id="panel-rfi" class="tab-panel hidden">${renderRFIPanelHTML()}</div>
        <div id="panel-contradictions" class="tab-panel hidden">${renderContradictionPanelHTML()}</div>
        <div id="panel-upload" class="tab-panel hidden">${renderInboxPanelHTML()}</div>
      </section>
      ${renderNewProjectModalHTML()}
    </div>
  `;
  wireDashboardEvents();
  initDashboard();
}

function wireDashboardEvents() {
  if (typeof document === 'undefined') return;
  document.getElementById('logout-btn')?.addEventListener('click', () => {
    TokenManager.clear();
    clearApiKey();
    navigate('/login');
    window.location.reload();
  });
  wireTabs();
  wireProjectSelector();
  wireQueryPanel();
  wireRFIPanel();
  wireContradictionPanel();
  wireInboxPanel();
  updateAuthMeshStatus();
}

function initDashboard() {
  const p = state.projects[0];
  if (p) selectProject(p.id);
  updateAuthMeshStatus();
}
