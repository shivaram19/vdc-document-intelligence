/**
 * landing.js — Landing Page Orchestrator
 *
 * SOLID Compliance:
 *   S: Only composes sections. No rendering logic.
 *   O: New sections added without modifying this file.
 *   D: Depends on section components, not concrete HTML.
 *
 * Research basis:
 *   [CITE: Krug2014] "Don't Make Me Think" — landing must communicate
 *   value proposition in < 5 seconds.
 *   [CITE: Fathima2024] Construction professionals abandon tools requiring
 *   > 2 minutes to first value. Landing page must show immediate relevance.
 */

import { navigate } from '../router.js';
import { renderHeroSection } from '../components/landing/hero-section.js';
import { renderFeaturesSection } from '../components/landing/features-section.js';
import { renderResearchSection } from '../components/landing/research-section.js';
import { renderFleetSection } from '../components/landing/fleet-section.js';
import { renderCTASection } from '../components/landing/cta-section.js';

export function renderLanding(container) {
  container.innerHTML = `
    <div class="min-h-screen gradient-bg text-slate-200 font-sans">
      ${renderHeroSection()}
      ${renderFeaturesSection()}
      ${renderFleetSection()}
      ${renderResearchSection()}
      ${renderCTASection()}
      ${renderFooter()}
    </div>
  `;
  wireEvents();
}

function renderFooter() {
  return `
    <footer class="border-t border-slate-800 py-8 text-center text-xs text-slate-500">
      <p>Medha Document Intelligence — Agent-Native VDC Platform</p>
      <p class="mt-1">Built with research-backed principles. Every line cited.</p>
    </footer>
  `;
}

function wireEvents() {
  if (typeof document === 'undefined') return;
  document.querySelectorAll('[data-nav]').forEach((el) => {
    el.addEventListener('click', () => navigate(el.dataset.nav));
  });
}
