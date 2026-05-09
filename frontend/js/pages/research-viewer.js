import { navigate } from '../router.js';

/*
 * research-viewer.js — Markdown document reader
 *
 * [CITE: Bakaus2026] Typography: distinct font pairing, modular scale.
 * [CITE: Ware2021] Dark surfaces reduce glare for long-form reading.
 * [CITE: ADR-006] Tinted neutrals only — never pure gray on colored bg.
 */

let manifest = [];

export async function renderResearchViewer(container, params) {
  const slug = params?.slug;

  if (!manifest.length) {
    try {
      const res = await fetch('research/manifest.json');
      manifest = await res.json();
    } catch (e) {
      container.innerHTML = `<p class="text-safe-red text-sm font-mono text-center py-20">Failed to load manifest.</p>`;
      return;
    }
  }

  const doc = manifest.find(m => m.id === slug);
  if (!doc) {
    container.innerHTML = `
      <div class="min-h-screen blueprint-bg flex items-center justify-center">
        <div class="text-center">
          <p class="text-safe-red font-mono text-sm mb-3">Document not found.</p>
          <button id="viewer-back" class="px-4 py-2 bg-bp-accent text-white text-xs font-mono rounded-sm">
            <i class="fas fa-arrow-left mr-2"></i>BACK TO PORTAL
          </button>
        </div>
      </div>
    `;
    document.getElementById('viewer-back')?.addEventListener('click', () => navigate('/research'));
    return;
  }

  container.innerHTML = `
    <div class="min-h-screen blueprint-bg">
      <!-- Top bar -->
      <div class="sticky top-0 z-50 border-b border-bp-light/20 bg-bp-dark/90 backdrop-blur-md">
        <div class="max-w-4xl mx-auto px-6 py-3 flex items-center justify-between">
          <button id="viewer-back" class="flex items-center gap-2 text-xs text-neutral-400 hover:text-white transition font-mono">
            <i class="fas fa-arrow-left"></i>
            <span class="hidden sm:inline">RESEARCH PORTAL</span>
          </button>
          <div class="flex items-center gap-3">
            <span class="text-[10px] font-mono text-neutral-600 uppercase tracking-wider">${doc.badge}</span>
            <span class="text-neutral-700">|</span>
            <span class="text-[10px] font-mono text-neutral-500">${doc.category}</span>
          </div>
        </div>
      </div>

      <!-- Document header -->
      <div class="max-w-4xl mx-auto px-6 pt-10 pb-6">
        <span class="inline-block px-2 py-1 text-[9px] font-mono font-semibold tracking-wider uppercase bg-bp-accent/10 text-bp-accent border border-bp-accent/20 rounded-sm mb-4">
          ${doc.badge}
        </span>
        <h1 class="text-2xl sm:text-3xl font-bold text-white font-display leading-tight mb-3">${doc.title}</h1>
        <div class="flex items-center gap-3 text-[11px] text-neutral-500 font-mono">
          <span><i class="far fa-file-alt mr-1"></i>${doc.path}</span>
          <span class="text-neutral-700">·</span>
          <span id="viewer-wordcount">Loading...</span>
        </div>
      </div>

      <!-- TOC + Content -->
      <div class="max-w-4xl mx-auto px-6 pb-20">
        <div class="flex flex-col lg:flex-row gap-8">
          <!-- TOC sidebar -->
          <aside class="lg:w-56 lg:flex-shrink-0">
            <div class="lg:sticky lg:top-20">
              <p class="text-[10px] font-mono text-neutral-600 uppercase tracking-widest mb-3">On this page</p>
              <nav id="viewer-toc" class="space-y-1 max-h-[70vh] overflow-y-auto pr-2">
                <!-- TOC injected -->
              </nav>
            </div>
          </aside>

          <!-- Main content -->
          <article id="viewer-content" class="flex-1 min-w-0 research-markdown">
            <div class="text-neutral-400 text-sm font-mono">Loading document...</div>
          </article>
        </div>
      </div>
    </div>
  `;

  document.getElementById('viewer-back')?.addEventListener('click', () => navigate('/research'));

  // Fetch and render markdown
  try {
    const res = await fetch(`research/${doc.path}`);
    if (!res.ok) throw new Error('Not found');
    const text = await res.text();

    // Word count
    const words = text.trim().split(/\s+/).length;
    const wcEl = document.getElementById('viewer-wordcount');
    if (wcEl) wcEl.textContent = `${words.toLocaleString()} words`;

    // Render markdown
    const contentEl = document.getElementById('viewer-content');
    if (typeof marked !== 'undefined') {
      marked.setOptions({
        gfm: true,
        breaks: false,
        headerIds: true,
        mangle: false
      });
      contentEl.innerHTML = marked.parse(text);
    } else {
      // Fallback: render as preformatted text
      contentEl.innerHTML = `<pre class="text-sm text-neutral-300 font-mono whitespace-pre-wrap">${escapeHtml(text)}</pre>`;
    }

    // Build TOC from rendered headings
    buildTOC(contentEl);

    // Smooth scroll for anchor links
    contentEl.querySelectorAll('a[href^="#"]').forEach(a => {
      a.addEventListener('click', (e) => {
        e.preventDefault();
        const target = document.querySelector(a.getAttribute('href'));
        if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    });

  } catch (e) {
    document.getElementById('viewer-content').innerHTML = `
      <p class="text-safe-red text-sm font-mono">Failed to load document: ${e.message}</p>
    `;
  }
}

function buildTOC(contentEl) {
  const headings = contentEl.querySelectorAll('h1, h2, h3');
  const tocEl = document.getElementById('viewer-toc');
  if (!tocEl || headings.length === 0) {
    if (tocEl) tocEl.innerHTML = '<p class="text-xs text-neutral-600 font-mono">No headings found.</p>';
    return;
  }

  tocEl.innerHTML = Array.from(headings).map(h => {
    const level = parseInt(h.tagName[1]);
    const indent = level === 1 ? '' : level === 2 ? 'pl-3' : 'pl-6';
    const size = level === 1 ? 'text-xs font-semibold' : 'text-[11px]';
    const color = level === 1 ? 'text-neutral-300' : 'text-neutral-500';
    const id = h.id || slugify(h.textContent);
    h.id = id;
    return `
      <a href="#${id}" class="block ${indent} ${size} ${color} hover:text-bp-accent transition font-mono truncate py-0.5">
        ${h.textContent}
      </a>
    `;
  }).join('');

  tocEl.querySelectorAll('a').forEach(a => {
    a.addEventListener('click', (e) => {
      e.preventDefault();
      const target = document.querySelector(a.getAttribute('href'));
      if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });
}

function slugify(text) {
  return text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
