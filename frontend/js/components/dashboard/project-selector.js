/**
 * project-selector.js — Project Selector + Modal
 * SOLID: SRP — only project selection and creation UI.
 */

import { state } from '../../state.js';
import { createProject } from '../../ws.js';

export function renderProjectSelectorHTML() {
  return `
    <div class="card-structural mb-4">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <div class="flex items-center gap-4">
          <label class="text-sm text-neutral-500 font-mono">PROJECT:</label>
          <select id="project-select" class="bg-bp-dark border border-bp-light/50 text-white text-sm rounded-sm px-3 py-2 focus:outline-none focus:border-bp-accent min-w-[200px] font-mono">
            <option value="">No projects</option>
          </select>
          <button id="btn-new-project" class="text-sm px-3 py-2 bg-bp-mid hover:bg-bp-light/30 rounded-sm text-neutral-300 transition border border-bp-light/30 font-mono">
            <i class="fas fa-plus mr-1"></i> NEW
          </button>
        </div>
        <div class="flex items-center gap-4 text-sm text-neutral-500 font-mono">
          <span id="doc-count">0 DOCUMENTS</span>
          <span id="chunk-count">0 CHUNKS INDEXED</span>
        </div>
      </div>
    </div>
  `;
}

export function renderNewProjectModalHTML() {
  return `
    <div id="new-project-modal" class="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
      <div class="bg-bp-mid rounded-sm max-w-md w-full p-6 border border-bp-light">
        <h3 class="font-semibold text-white mb-4 font-mono">CREATE NEW PROJECT</h3>
        <div class="space-y-4">
          <div>
            <label class="text-sm text-neutral-500 block mb-1 font-mono">PROJECT NAME</label>
            <input id="new-project-name" type="text" class="w-full bg-bp-dark border border-bp-light/50 text-white rounded-sm px-3 py-2 font-mono" placeholder="e.g., Downtown Office Tower">
          </div>
          <div>
            <label class="text-sm text-neutral-500 block mb-1 font-mono">CLIENT NAME</label>
            <input id="new-project-client" type="text" class="w-full bg-bp-dark border border-bp-light/50 text-white rounded-sm px-3 py-2 font-mono" placeholder="e.g., ABC Development Corp">
          </div>
          <div class="flex gap-3">
            <button id="submit-new-project" class="flex-1 px-4 py-2 bg-bp-accent hover:bg-blue-500 text-white rounded-sm transition font-mono">CREATE</button>
            <button id="close-new-project" class="flex-1 px-4 py-2 bg-bp-mid hover:bg-bp-light/30 text-neutral-300 rounded-sm transition border border-bp-light/30 font-mono">CANCEL</button>
          </div>
        </div>
      </div>
    </div>
  `;
}

export function wireProjectSelector() {
  document.getElementById('btn-new-project')?.addEventListener('click', () => {
    console.log('[project] Opening modal');
    document.getElementById('new-project-modal')?.classList.remove('hidden');
  });
  document.getElementById('close-new-project')?.addEventListener('click', () => {
    document.getElementById('new-project-modal')?.classList.add('hidden');
  });
  document.getElementById('submit-new-project')?.addEventListener('click', submitNewProject);
}

async function submitNewProject() {
  const nameInput = document.getElementById('new-project-name');
  const clientInput = document.getElementById('new-project-client');
  const name = nameInput?.value.trim();
  const client = clientInput?.value.trim() || '';
  if (!name) {
    alert('Project name is required.');
    return;
  }
  console.log('[project] Creating:', name);
  // Test mode: mock project creation without server round-trip
  if (state.testMode) {
    const mockProject = { id: 'test_' + Date.now(), name, client, docs: [], document_count: 0, chunk_count: 0 };
    state.projects.push(mockProject);
    selectProject(mockProject.id);
    document.getElementById('new-project-modal')?.classList.add('hidden');
    nameInput.value = '';
    clientInput.value = '';
    return;
  }
  try {
    const result = await createProject(name, client);
    console.log('[project] Result:', result);
    if (result.error) {
      alert('Failed: ' + result.error);
      return;
    }
    document.getElementById('new-project-modal')?.classList.add('hidden');
    nameInput.value = '';
    clientInput.value = '';
    // Optimistically add to local state
    if (result.project) {
      state.projects.push(result.project);
      selectProject(result.project.id);
    }
  } catch (e) {
    console.error('[project] Error:', e);
    alert('Failed: ' + (e.message || 'Unknown error'));
  }
}

export function selectProject(id) {
  state.currentProject = id;
  const sel = document.getElementById('project-select');
  if (sel) sel.value = id;
  const p = state.projects.find((x) => x.id === id);
  if (p) {
    const docCount = p.docs?.length || p.document_count || 0;
    const chunkCount = p.docs?.reduce((a, d) => a + (d.chunk_count || 0), 0) || p.chunk_count || 0;
    document.getElementById('doc-count').textContent = `${docCount} DOCUMENTS`;
    document.getElementById('chunk-count').textContent = `${chunkCount} CHUNKS INDEXED`;
  }
}
