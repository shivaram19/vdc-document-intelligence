/**
 * target-card.js — Single Outreach Target Card Renderer (Enriched)
 *
 * Displays per-contact:
 * - LinkedIn search link (exact URLs not publicly discoverable per research)
 * - Connection request note (150-250 chars, research-backed)
 * - Enrichment: conferences, publications, affiliations, media
 *
 * RESEARCH BASIS:
 * [CITE: PostKing2026] PostKing.io A/B test (4,200+ requests). Notes referencing specific content = 48% acceptance. https://postking.io/blog/linkedin-connection-request-templates-sales
 * LinkedIn robots.txt blocks search-engine indexing of individual profiles.
 */

const STAGE_STYLES = {
  identified: ['bg-gray-700/50', 'text-gray-500', 'IDENTIFIED'],
  contacted: ['bg-bp-accent/20', 'text-bp-accent', 'CONTACTED'],
  demo: ['bg-warn-yellow/20', 'text-warn-yellow', 'DEMO'],
  pilot: ['bg-safe-orange/20', 'text-safe-orange', 'PILOT'],
  customer: ['bg-safe-green/20', 'text-safe-green', 'CUSTOMER'],
};

function renderEnrichment(contact) {
  if (!contact.enrichment) return '';
  const e = contact.enrichment;
  const sections = [];

  if (e.conferences?.length) {
    const items = e.conferences.map((c) => `
      <a href="${c.url}" target="_blank" class="block text-[10px] text-bp-accent hover:text-white transition truncate">
        <i class="fas fa-microphone mr-1"></i>${c.name}
      </a>
    `).join('');
    sections.push(`<div class="mb-1"><p class="text-[10px] text-gray-600 font-mono mb-0.5">CONFERENCES</p>${items}</div>`);
  }

  if (e.publications?.length) {
    const items = e.publications.map((p) => `
      <a href="${p.url}" target="_blank" class="block text-[10px] text-bp-accent hover:text-white transition truncate">
        <i class="fas fa-book mr-1"></i>${p.title}
      </a>
    `).join('');
    sections.push(`<div class="mb-1"><p class="text-[10px] text-gray-600 font-mono mb-0.5">PUBLICATIONS</p>${items}</div>`);
  }

  if (e.affiliations?.length) {
    const items = e.affiliations.map((a) => `
      <a href="${a.url || '#'}" target="_blank" class="block text-[10px] text-gray-500 hover:text-white transition truncate">
        <i class="fas fa-university mr-1"></i>${a.org} — ${a.role}
      </a>
    `).join('');
    sections.push(`<div class="mb-1"><p class="text-[10px] text-gray-600 font-mono mb-0.5">AFFILIATIONS</p>${items}</div>`);
  }

  if (e.media?.length) {
    const items = e.media.map((m) => `
      <a href="${m.url}" target="_blank" class="block text-[10px] text-gray-500 hover:text-white transition truncate">
        <i class="fas fa-play-circle mr-1"></i>${m.title}
      </a>
    `).join('');
    sections.push(`<div class="mb-1"><p class="text-[10px] text-gray-600 font-mono mb-0.5">MEDIA</p>${items}</div>`);
  }

  if (e.research_note) {
    sections.push(`<p class="text-[10px] text-gray-600 italic mt-1">${e.research_note}</p>`);
  }

  if (!sections.length) return '';

  return `
    <details class="group/enrich mt-2">
      <summary class="text-[10px] text-gray-600 font-mono cursor-pointer list-none flex items-center gap-1 hover:text-gray-400 transition">
        <i class="fas fa-chevron-right text-[8px] group-open/enrich:rotate-90 transition-transform"></i>
        RESEARCH ENRICHMENT (${sections.length} DIMENSIONS)
      </summary>
      <div class="mt-1 pl-3 border-l border-bp-light/20 space-y-1">
        ${sections.join('')}
      </div>
    </details>
  `;
}

export function renderTargetCard(t) {
  const badge = STAGE_STYLES[t.stage] || STAGE_STYLES.identified;

  const contactCards = t.contacts.map((c) => `
    <div class="bg-bp-dark/30 border border-bp-light/10 rounded p-2 mb-2">
      <div class="flex items-start justify-between mb-1">
        <div>
          <p class="text-xs text-white font-semibold">${c.name}</p>
          <p class="text-[10px] text-gray-500">${c.role}</p>
          <p class="text-[10px] text-gray-600 font-mono">${c.location}</p>
        </div>
      </div>

      <div class="mb-2">
        <p class="text-[10px] text-gray-600 font-mono mb-1">CONNECTION NOTE</p>
        <div class="bg-bp-dark/50 border border-bp-light/20 rounded p-2 text-xs text-gray-400 font-mono leading-relaxed">${c.note}</div>
        <div class="flex gap-2 mt-1">
          <a href="${c.linkedin}" target="_blank" class="text-[10px] text-bp-accent hover:text-white transition font-mono">
            <i class="fab fa-linkedin mr-1"></i>FIND ON LINKEDIN
          </a>
          <button data-copy="${encodeURIComponent(c.note)}" class="text-[10px] text-gray-500 hover:text-white transition font-mono copy-msg-btn">
            <i class="fas fa-copy mr-1"></i>COPY NOTE
          </button>
        </div>
      </div>

      ${renderEnrichment(c)}
    </div>
  `).join('');

  return `
    <div class="card-structural border-bp-light/30 hover:border-bp-accent/50 transition">
      <div class="flex items-start justify-between mb-2">
        <div>
          <h4 class="text-sm font-bold text-white">${t.name}</h4>
          <p class="text-[10px] text-gray-500 font-mono">${t.location}</p>
        </div>
        <span class="px-2 py-1 rounded-sm text-[10px] font-mono font-bold ${badge[0]} ${badge[1]}">${badge[2]}</span>
      </div>
      <div class="mb-2">
        <p class="text-[10px] text-gray-600 font-mono mb-1">COMPANY PAIN</p>
        <p class="text-xs text-gray-400 leading-relaxed">${t.pain}</p>
      </div>
      <div>
        <p class="text-[10px] text-gray-600 font-mono mb-1">CONTACTS (${t.contacts.length})</p>
        ${contactCards}
      </div>
    </div>
  `;
}
