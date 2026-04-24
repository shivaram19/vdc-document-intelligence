/**
 * agent.js — Individual Agent Detail Page
 * SOLID: SRP — only agent profile rendering.
 */

import { getAgent } from '../data/agents.js';
import { navigate } from '../router.js';

export function renderAgent(container) {
  const path = window.location.hash.replace('#', '') || '/';
  const slug = path.replace('/agent/', '');
  const agent = getAgent(slug);

  if (!agent) {
    container.innerHTML = `
      <div class="min-h-screen blueprint-bg flex items-center justify-center">
        <div class="text-center">
          <p class="text-gray-500 font-mono mb-4">AGENT NOT FOUND</p>
          <button data-nav="/" class="btn-inspect font-mono">BACK TO FLEET</button>
        </div>
      </div>
    `;
    wireAgentEvents();
    return;
  }

  container.innerHTML = `
    <div class="min-h-screen blueprint-bg">
      <header class="border-b border-bp-light/30 bg-bp-dark/80 backdrop-blur-sm sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-sm bg-${agent.color}/10 flex items-center justify-center">
              <i class="fas ${agent.icon} text-${agent.color} text-sm"></i>
            </div>
            <div>
              <h1 class="font-bold text-white font-mono">${agent.name.toUpperCase()}</h1>
              <p class="text-xs text-gray-500 font-mono">${agent.role.toUpperCase()}</p>
            </div>
          </div>
          <button data-nav="/" class="text-xs text-gray-500 hover:text-white transition font-mono">
            <i class="fas fa-arrow-left mr-1"></i>BACK TO FLEET
          </button>
        </div>
      </header>

      <main class="max-w-4xl mx-auto px-6 py-12">
        <div class="mb-10">
          <p class="text-2xl font-bold text-white mb-2">${agent.tagline}</p>
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-sm bg-${agent.color}/10 text-${agent.color} text-xs font-mono border border-${agent.color}/30">
            <i class="fas ${agent.icon}"></i> ${agent.metric}
          </div>
        </div>

        <div class="grid md:grid-cols-3 gap-4 mb-12">
          <div class="card-structural border-l-2 border-safe-red">
            <p class="text-[10px] font-mono text-gray-500 mb-2 uppercase">The Problem</p>
            <p class="text-sm text-gray-300 leading-relaxed">${agent.problem}</p>
          </div>
          <div class="card-structural border-l-2 border-bp-accent">
            <p class="text-[10px] font-mono text-gray-500 mb-2 uppercase">The Solution</p>
            <p class="text-sm text-gray-300 leading-relaxed">${agent.solution}</p>
          </div>
          <div class="card-structural border-l-2 border-safe-green">
            <p class="text-[10px] font-mono text-gray-500 mb-2 uppercase">What It Adds</p>
            <p class="text-sm text-gray-300 leading-relaxed">${agent.adds}</p>
          </div>
        </div>

        <div class="card-structural mb-8">
          <h2 class="text-lg font-semibold text-white mb-4 flex items-center gap-2 font-mono">
            <i class="fas fa-dumbbell text-${agent.color} text-xs"></i> CAPABILITY & STRENGTH
          </h2>
          <p class="text-sm text-gray-400 leading-relaxed mb-4">${agent.strength}</p>
          <div class="flex items-center gap-3">
            <span class="badge-pass text-[10px]"><i class="fas fa-check mr-1"></i>PRODUCTION-READY</span>
            <span class="badge-info text-[10px]"><i class="fas fa-chart-line mr-1"></i>${agent.metric}</span>
          </div>
        </div>

        <div class="text-center">
          <button data-nav="/login" class="btn-inspect font-mono">
            <i class="fas fa-clipboard-check mr-2"></i>RUN DOCUMENT INSPECTION
          </button>
        </div>
      </main>
    </div>
  `;

  wireAgentEvents();
}

function wireAgentEvents() {
  document.querySelectorAll('[data-nav]').forEach((el) => {
    el.addEventListener('click', () => navigate(el.dataset.nav));
  });
}
