/**
 * landing.js — Landing Page Orchestrator
 * SOLID: SRP — composes sections, delegates rendering.
 */

import { renderHeroSection } from '../components/landing/hero-section.js';
import { renderFeaturesSection } from '../components/landing/features-section.js';
import { renderFleetSection, wireFleetEvents } from '../components/landing/fleet-section.js';
import { renderResearchSection } from '../components/landing/research-section.js';
import { renderCTASection } from '../components/landing/cta-section.js';
import { navigate } from '../router.js';

export function renderLanding(container) {
  container.innerHTML = `
    <main id="landing-page" class="blueprint-bg">
      <div id="hero-mount"></div>
      <div id="features-mount"></div>
      <div id="fleet-mount"></div>
      <div id="research-mount"></div>
      <div id="cta-mount"></div>
      <footer class="py-8 text-center text-xs text-gray-600 font-mono border-t border-bp-light/10">
        <p>Medha Document Intelligence — Research-Backed · Agent-Native · Construction-Aligned</p>
        <p class="mt-1">Built with PicoCloth mesh · 3-factor auth · Cryptographic audit trail</p>
      </footer>
    </main>
  `;

  container.querySelector('#hero-mount').outerHTML = renderHeroSection();
  container.querySelector('#features-mount').outerHTML = renderFeaturesSection();
  container.querySelector('#fleet-mount').outerHTML = renderFleetSection();
  container.querySelector('#research-mount').outerHTML = renderResearchSection();
  container.querySelector('#cta-mount').outerHTML = renderCTASection();

  if (typeof document !== 'undefined') {
    wireEvents();
    wireFleetEvents();
  }
}

function wireEvents() {
  document.querySelectorAll('[data-nav]').forEach((el) => {
    el.addEventListener('click', () => navigate(el.dataset.nav));
  });
}
