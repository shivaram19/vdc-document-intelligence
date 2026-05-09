import { navigate } from '../router.js';

/*
 * research-portal.js — Password-gated research document hub
 *
 * [CITE: Bakaus2026] Anti-monoculture: no card nesting, purposeful spacing.
 * [CITE: Ware2021] Dark surfaces reduce glare for long-form reading.
 * [CITE: ADR-006] Tinted neutrals only — no pure grays.
 * [CITE: ADR-008] Motion uses ease-out for UI, linear for continuous.
 */

// SHA-256 of default password "trelo-labs-research-2026"
// Change this hash if you change the password.
const PASSWORD_HASH = 'c672a608fd73a800423a3a4e5ad8b04ef9c4417f8dc03125c61d56d3a2072d03';
const SESSION_KEY = 'research_auth';

let manifest = [];
let categories = [];

async function sha256(text) {
  const encoder = new TextEncoder();
  const data = encoder.encode(text);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

function isAuthenticated() {
  return sessionStorage.getItem(SESSION_KEY) === 'true';
}

function setAuthenticated(v) {
  if (v) sessionStorage.setItem(SESSION_KEY, 'true');
  else sessionStorage.removeItem(SESSION_KEY);
}

export async function renderResearchPortal(container) {
  container.innerHTML = `
    <div class="min-h-screen blueprint-bg">
      <header class="border-b border-bp-light/20">
        <div class="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-sm bg-bp-accent flex items-center justify-center text-white font-bold text-sm">M</div>
            <div>
              <h1 class="text-sm font-bold text-white font-display tracking-tight">RESEARCH PORTAL</h1>
              <p class="text-[10px] text-neutral-500 font-mono tracking-widest">MEDHA.TRELOLABS.COM</p>
            </div>
          </div>
          <button id="research-logout" class="text-xs text-neutral-500 hover:text-neutral-300 transition font-mono hidden">
            <i class="fas fa-lock mr-1"></i>LOCK
          </button>
        </div>
      </header>

      <main id="research-main" class="max-w-6xl mx-auto px-6 py-10">
        <!-- Injected by auth state -->
      </main>
    </div>
  `;

  const main = document.getElementById('research-main');

  if (!isAuthenticated()) {
    renderGate(main);
  } else {
    renderGrid(main);
  }

  document.getElementById('research-logout')?.addEventListener('click', () => {
    setAuthenticated(false);
    renderResearchPortal(container);
  });
}

function renderGate(main) {
  main.innerHTML = `
    <div class="max-w-sm mx-auto pt-16">
      <div class="text-center mb-8">
        <div class="w-16 h-16 rounded-full bg-bp-accent/10 border border-bp-accent/30 flex items-center justify-center mx-auto mb-5">
          <i class="fas fa-lock text-bp-accent text-xl"></i>
        </div>
        <h2 class="text-xl font-bold text-white font-display mb-2">Research Vault</h2>
        <p class="text-sm text-neutral-500">Enter the password to access internal research documents.</p>
      </div>

      <div class="space-y-4">
        <div>
          <label class="block text-[10px] font-mono text-neutral-500 uppercase tracking-wider mb-2">Password</label>
          <input id="research-password" type="password"
            class="w-full bg-bp-dark border border-bp-light/40 text-white text-sm rounded-sm px-4 py-3 focus:outline-none focus:border-bp-accent font-mono transition"
            placeholder="••••••••"
            autocomplete="off">
        </div>
        <button id="research-unlock" class="w-full px-4 py-3 bg-bp-accent hover:bg-blue-500 text-white font-semibold rounded-sm transition font-mono text-sm">
          <i class="fas fa-arrow-right mr-2"></i>UNLOCK
        </button>
        <p id="research-error" class="text-xs text-safe-red text-center hidden font-mono"></p>
      </div>

      <div class="mt-8 pt-6 border-t border-bp-light/20 text-center">
        <p class="text-[10px] text-neutral-600 font-mono">25 DOCUMENTS · UPDATED MAY 2026</p>
      </div>
    </div>
  `;

  const input = document.getElementById('research-password');
  const btn = document.getElementById('research-unlock');
  const err = document.getElementById('research-error');

  async function tryUnlock() {
    const val = input.value.trim();
    if (!val) return;
    const hash = await sha256(val);
    if (hash === PASSWORD_HASH) {
      setAuthenticated(true);
      renderGrid(main);
      document.getElementById('research-logout')?.classList.remove('hidden');
    } else {
      err.textContent = 'Incorrect password. Access denied.';
      err.classList.remove('hidden');
      input.value = '';
      input.focus();
    }
  }

  btn.addEventListener('click', tryUnlock);
  input.addEventListener('keypress', (e) => { if (e.key === 'Enter') tryUnlock(); });
  input.focus();
}

async function renderGrid(main) {
  document.getElementById('research-logout')?.classList.remove('hidden');

  if (manifest.length === 0) {
    try {
      const res = await fetch('research/manifest.json');
      manifest = await res.json();
      categories = [...new Set(manifest.map(m => m.category))];
    } catch (e) {
      main.innerHTML = `<p class="text-safe-red text-sm font-mono text-center py-20">Failed to load manifest.</p>`;
      return;
    }
  }

  const categoryOptions = [`<option value="all">All Categories</option>`,
    ...categories.map(c => `<option value="${c}">${c}</option>`)
  ].join('');

  main.innerHTML = `
    <div class="mb-8 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h2 class="text-lg font-bold text-white font-display">Research Documents</h2>
        <p class="text-sm text-neutral-500 mt-1">Internal research corpus — ${manifest.length} files</p>
      </div>
      <div class="flex items-center gap-3">
        <select id="research-filter" class="bg-bp-dark border border-bp-light/40 text-neutral-300 text-xs rounded-sm px-3 py-2 font-mono focus:outline-none focus:border-bp-accent">
          ${categoryOptions}
        </select>
        <input id="research-search" type="text" placeholder="Search..."
          class="bg-bp-dark border border-bp-light/40 text-white text-xs rounded-sm px-3 py-2 font-mono focus:outline-none focus:border-bp-accent w-44">
      </div>
    </div>

    <div id="research-grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
      <!-- Grid injected here -->
    </div>
  `;

  const grid = document.getElementById('research-grid');
  const filter = document.getElementById('research-filter');
  const search = document.getElementById('research-search');

  function drawGrid() {
    const cat = filter.value;
    const q = search.value.trim().toLowerCase();
    const filtered = manifest.filter(m => {
      const matchCat = cat === 'all' || m.category === cat;
      const matchQ = !q || m.title.toLowerCase().includes(q) || m.badge.toLowerCase().includes(q);
      return matchCat && matchQ;
    });

    if (filtered.length === 0) {
      grid.innerHTML = `
        <div class="col-span-full text-center py-16">
          <i class="fas fa-search text-neutral-700 text-2xl mb-3"></i>
          <p class="text-sm text-neutral-500 font-mono">No documents match your criteria.</p>
        </div>
      `;
      return;
    }

    grid.innerHTML = filtered.map((m, i) => `
      <button data-slug="${m.id}"
        class="research-tile group text-left w-full p-4 border border-bp-light/25 bg-bp-mid/40 hover:bg-bp-mid/70 hover:border-bp-accent/40 rounded-sm transition-all duration-200"
        style="animation: fadeInUp 0.3s ease-out ${i * 0.03}s both;">
        <div class="flex items-start justify-between mb-3">
          <span class="inline-block px-2 py-1 text-[9px] font-mono font-semibold tracking-wider uppercase bg-bp-accent/10 text-bp-accent border border-bp-accent/20 rounded-sm">
            ${m.badge}
          </span>
          <i class="fas fa-arrow-up-right-from-square text-neutral-600 group-hover:text-bp-accent transition text-xs opacity-0 group-hover:opacity-100"></i>
        </div>
        <h3 class="text-sm font-semibold text-neutral-100 group-hover:text-white transition leading-snug mb-1">${m.title}</h3>
        <p class="text-[11px] text-neutral-500 font-mono">${m.category}</p>
      </button>
    `).join('');

    grid.querySelectorAll('.research-tile').forEach(btn => {
      btn.addEventListener('click', () => {
        navigate(`/research/${btn.dataset.slug}`);
      });
    });
  }

  filter.addEventListener('change', drawGrid);
  search.addEventListener('input', drawGrid);
  drawGrid();
}
