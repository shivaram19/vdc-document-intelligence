/**
 * connector-onboard.js — Friction-Reduced Connector Onboarding Orchestrator
 *
 * SRP: ONLY state management + step dispatch. Rendering delegated.
 * DIP: Depends on abstract renderers, not DOM details.
 * OCP: Add steps by extending STEPS map without modifying orchestration logic.
 */

import { navigate } from '../router.js';
import { renderStep1, renderStep2, renderStep3 } from '../components/connector/step-renderers.js';
import { filterValidFiles, simulateUpload } from '../services/connector-upload.js';

/* ─────────── STATE ─────────── */
let st = { step: 1, source: null, files: [], uploading: false, progress: {}, samplePreloaded: false };

/* ─────────── STEP REGISTRY ─────────── */
const STEPS = {
  1: () => renderStep1(),
  2: () => renderStep2(st.source, st.files, st.progress, st.uploading),
  3: () => renderStep3(st.source, st.files, st.progress),
};

/* ─────────── PUBLIC API ─────────── */
export function renderConnectorOnboard(container) {
  container.innerHTML = `
    <div class="min-h-screen blueprint-bg">
      ${renderHeader()}
      <main class="max-w-4xl mx-auto px-6 py-10">
        ${renderProgress()}
        <div id="onboard-step-content" class="mt-8"></div>
      </main>
    </div>
  `;
  refreshStep();
  wireGlobalEvents();
}

/* ─────────── HEADER ─────────── */
function renderHeader() {
  return `
    <header class="border-b border-bp-light/30 bg-bp-dark/80 backdrop-blur-sm sticky top-0 z-50">
      <div class="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-sm bg-bp-accent flex items-center justify-center text-white font-bold">M</div>
          <div>
            <h1 class="font-bold text-white font-mono">MEDHA</h1>
            <p class="text-xs text-gray-500 font-mono">CONNECT YOUR PROJECT</p>
          </div>
        </div>
        <button data-skip class="text-xs text-gray-500 hover:text-white transition font-mono">SKIP FOR NOW</button>
      </div>
    </header>
  `;
}

/* ─────────── PROGRESS BAR ─────────── */
function renderProgress() {
  const labels = ['CHOOSE SOURCE', 'ADD DOCUMENTS', 'VERIFY & CONNECT'];
  const items = labels.map((label, i) => {
    const n = i + 1;
    const done = st.step > n || (n === 1 && st.step === 1);
    const active = st.step === n;
    const circle = done
      ? `<div class="w-8 h-8 rounded-full bg-safe-green flex items-center justify-center text-bp-dark font-bold text-sm"><i class="fas fa-check"></i></div>`
      : active
        ? `<div class="w-8 h-8 rounded-full bg-bp-accent flex items-center justify-center text-white font-bold text-sm">${n}</div>`
        : `<div class="w-8 h-8 rounded-full bg-bp-light/20 flex items-center justify-center text-gray-500 font-bold text-sm">${n}</div>`;
    const cls = active ? 'text-white' : done ? 'text-safe-green' : 'text-gray-600';
    return `<div class="flex items-center gap-3">${circle}<span class="text-xs font-mono ${cls}">${label}</span></div>`;
  }).join(`<div class="flex-1 h-px bg-bp-light/20 mx-3"></div>`);
  return `<div class="flex items-center justify-between mb-2">${items}</div>`;
}

/* ─────────── STEP DISPATCH ─────────── */
function refreshStep() {
  const el = document.getElementById('onboard-step-content');
  if (!el) return;
  el.innerHTML = STEPS[st.step]?.() || '';
  wireStepEvents();
}

/* ─────────── EVENT WIRING ─────────── */
function wireGlobalEvents() {
  document.querySelectorAll('[data-skip]').forEach((el) => {
    el.addEventListener('click', () => navigate('/demo'));
  });
}

function wireStepEvents() {
  /* Step 1 */
  document.querySelectorAll('.source-card').forEach((el) => {
    el.addEventListener('click', () => { st.source = el.dataset.source; st.step = 2; refreshStep(); });
  });
  document.querySelectorAll('[data-sample]').forEach((el) => {
    el.addEventListener('click', () => { st.samplePreloaded = true; navigate('/demo'); });
  });

  /* Step 2: Upload */
  const dz = document.getElementById('dropzone');
  const fi = document.getElementById('file-input');
  if (dz && fi) {
    dz.addEventListener('click', () => fi.click());
    dz.addEventListener('dragover', (e) => { e.preventDefault(); dz.classList.add('border-bp-accent'); });
    dz.addEventListener('dragleave', () => dz.classList.remove('border-bp-accent'));
    dz.addEventListener('drop', (e) => { e.preventDefault(); dz.classList.remove('border-bp-accent'); handleFiles(e.dataTransfer.files); });
    fi.addEventListener('change', (e) => handleFiles(e.target.files));
  }

  document.querySelectorAll('[data-back]').forEach((el) => {
    el.addEventListener('click', () => { st.step = Math.max(1, st.step - 1); if (st.step === 1) st.source = null; refreshStep(); });
  });

  document.querySelectorAll('[data-upload]').forEach((el) => {
    el.addEventListener('click', performUpload);
  });

  document.querySelectorAll('[data-request]').forEach((el) => {
    el.addEventListener('click', () => alert('Beta access request sent. Our team will contact you within 24 hours. Use Local Files upload in the meantime.'));
  });

  document.querySelectorAll('[data-use-upload]').forEach((el) => {
    el.addEventListener('click', () => { st.source = 'upload'; refreshStep(); });
  });

  /* Step 3 */
  document.querySelectorAll('[data-go-dashboard]').forEach((el) => {
    el.addEventListener('click', () => navigate('/dashboard'));
  });
  document.querySelectorAll('[data-add-more]').forEach((el) => {
    el.addEventListener('click', () => { st.step = 2; refreshStep(); });
  });
}

/* ─────────── FILE & UPLOAD HANDLERS ─────────── */
function handleFiles(fileList) {
  const valid = filterValidFiles(fileList, (msg, name) => console.warn(`[CONNECTOR] ${name}: ${msg}`));
  st.files = [...st.files, ...valid];
  refreshStep();
}

async function performUpload() {
  const valid = st.files.filter((f) => {
    const ext = f.name.slice(f.name.lastIndexOf('.')).toLowerCase();
    return ['.pdf', '.docx', '.doc', '.txt', '.md'].includes(ext);
  });
  if (!valid.length) { alert('No supported files to upload. Please add PDF, DOCX, TXT, or MD files.'); return; }

  st.uploading = true;
  refreshStep();

  await simulateUpload(valid, {
    onStart: (f) => { st.progress[f.name] = 'uploading'; refreshStep(); },
    onProgress: (f, pct) => { st.progress[f.name] = pct; refreshStep(); },
    onDone: (f) => { st.progress[f.name] = 'done'; refreshStep(); },
    onError: (f) => { st.progress[f.name] = 'error'; refreshStep(); },
  });

  st.uploading = false;
  st.step = 3;
  refreshStep();
}
