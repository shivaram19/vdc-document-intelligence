/**
 * connectors.js — Integration Ecosystem Page
 *
 * WHY: Construction firms use 11 different software platforms (Autodesk 2022).
 * Replacing them is impossible. Medha is an inspection layer that reads from
 * existing tools, adds intelligence, and writes back actionable alerts.
 *
 * [CITE: JBKnowledge2021] Only 23% of construction apps integrate.
 * Medha bridges the gap without requiring migration.
 */

import { navigate } from '../router.js';

const CONNECTORS = [
  {
    name: 'Autodesk Construction Cloud',
    category: 'Document Management',
    status: 'available',
    desc: 'Read drawings, specs, and RFIs from ACC. Post contradictions and RFI drafts back.',
    icon: 'fa-building',
  },
  {
    name: 'Procore',
    category: 'Project Management',
    status: 'available',
    desc: 'Sync project metadata, pull submittals, push inspection results to daily logs.',
    icon: 'fa-hard-hat',
  },
  {
    name: 'SharePoint / OneDrive',
    category: 'File Storage',
    status: 'available',
    desc: 'Index documents from any SharePoint library. Support for .pdf, .dwg, .docx.',
    icon: 'fa-cloud',
  },
  {
    name: 'Autodesk Revit',
    category: 'BIM / Design',
    status: 'beta',
    desc: 'Extract model metadata, compare spec values against parametric families. Coming Q3 2026.',
    icon: 'fa-cube',
  },
  {
    name: 'Navisworks',
    category: 'Clash Detection',
    status: 'planned',
    desc: 'Feed Medha contradictions into Navisworks clash reports for unified issue tracking.',
    icon: 'fa-exclamation-triangle',
  },
  {
    name: 'Newforma',
    category: 'Project Information',
    status: 'planned',
    desc: 'Sync project email and transmittal history for richer contradiction context.',
    icon: 'fa-envelope',
  },
];

export function renderConnectors(container) {
  const cards = CONNECTORS.map((c) => renderConnector(c)).join('');

  container.innerHTML = `
    <div class="min-h-screen blueprint-bg">
      <header class="border-b border-bp-light/30 bg-bp-dark/80 backdrop-blur-sm sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-sm bg-bp-accent flex items-center justify-center text-white font-bold">M</div>
            <div>
              <h1 class="font-bold text-white font-mono">MEDHA</h1>
              <p class="text-xs text-neutral-500 font-mono">INTEGRATIONS</p>
            </div>
          </div>
          <button data-nav="/" class="text-xs text-neutral-500 hover:text-white transition font-mono">
            <i class="fas fa-arrow-left mr-1"></i>BACK
          </button>
        </div>
      </header>

      <main class="max-w-6xl mx-auto px-6 py-16">
        <div class="text-center mb-14">
          <h2 class="text-3xl font-bold text-white mb-3">Works With Your Stack</h2>
          <p class="text-neutral-400 max-w-2xl mx-auto">
            Medha does not replace your tools. It inspects what they contain and alerts 
            you to what they missed. 
            <span class="text-bp-accent">Why?</span> Because replacing 11 tools is a 
            18-month change management project. Adding an inspection layer takes 20 minutes.
          </p>
          <div class="mt-4 inline-flex items-center gap-2 text-xs text-neutral-500 font-mono">
            <i class="fas fa-plug text-neutral-600"></i>
            3 integrations live. 3 more in development.
          </div>
        </div>

        <div class="grid md:grid-cols-3 gap-4">
          ${cards}
        </div>

        <div class="mt-16 card-structural">
          <h3 class="text-lg font-semibold text-white mb-4 font-mono">WHY "INSPECTION LAYER" NOT "PLATFORM"?</h3>
          <div class="grid md:grid-cols-2 gap-6 text-sm text-neutral-400">
            <div>
              <p class="text-white font-semibold mb-2">The Sunk Cost Trap</p>
              <p class="leading-relaxed">
                Construction firms have invested years in Procore workflows, ACC permissions, 
                and Revit standards. Asking them to abandon these triggers organizational resistance.
                <span class="text-bp-accent">[CITE: Autodesk2022]</span> 67% cite "data silos" 
                as top frustration, but only 12% are willing to migrate platforms.
              </p>
            </div>
            <div>
              <p class="text-white font-semibold mb-2">The Medha Approach</p>
              <p class="leading-relaxed">
                Read from existing systems. Add intelligence. Write alerts back. 
                No migration. No retraining. No change management. 
                Value delivered in minutes, not quarters.
              </p>
            </div>
          </div>
        </div>

        <div class="mt-8 flex gap-3">
          <button data-nav="/connect" class="btn-inspect font-mono text-sm">
            <i class="fas fa-plug mr-2"></i>CONNECT YOUR DRAWINGS
          </button>
          <button data-nav="/pricing" class="btn-outline font-mono text-sm">
            <i class="fas fa-tag mr-2"></i>VIEW PRICING
          </button>
        </div>

        <div class="mt-6 card-structural">
          <h3 class="text-lg font-semibold text-white mb-3 font-mono">CUSTOM INTEGRATION REQUEST</h3>
          <p class="text-sm text-neutral-400 mb-4">
            Don't see your tool? We add integrations based on customer demand.
            Enterprise plans include custom connector development.
          </p>
          <button data-nav="/pricing" class="btn-outline font-mono text-sm">
            <i class="fas fa-rocket mr-2"></i>VIEW ENTERPRISE OPTIONS
          </button>
        </div>
      </main>
    </div>
  `;

  wireEvents();
}

function renderConnector(c) {
  const badgeColor = c.status === 'available' ? 'bg-safe-green/20 text-safe-green'
    : c.status === 'beta' ? 'bg-warn-yellow/20 text-warn-yellow'
    : 'bg-neutral-700/50 text-neutral-500';
  const badgeText = c.status === 'available' ? 'LIVE'
    : c.status === 'beta' ? 'BETA'
    : 'PLANNED';

  return `
    <div class="card-structural border-bp-light/30">
      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-sm bg-bp-light/10 flex items-center justify-center text-bp-accent">
            <i class="fas ${c.icon}"></i>
          </div>
          <div>
            <h3 class="text-sm font-bold text-white">${c.name}</h3>
            <p class="text-[10px] text-neutral-500 font-mono">${c.category.toUpperCase()}</p>
          </div>
        </div>
        <span class="px-2 py-1 rounded-sm text-[10px] font-mono font-bold ${badgeColor}">${badgeText}</span>
      </div>
      <p class="text-sm text-neutral-400 leading-relaxed">${c.desc}</p>
    </div>
  `;
}

function wireEvents() {
  document.querySelectorAll('[data-nav]').forEach((el) => {
    el.addEventListener('click', () => navigate(el.dataset.nav));
  });
}
