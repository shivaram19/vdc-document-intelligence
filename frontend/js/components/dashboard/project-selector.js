/**
 * project-selector.js — Project Selector + Modal
 * SOLID: SRP — only project selection and creation UI.
 */

import { state } from '../../state.js';
import { createProject } from '../../ws.js';

export function renderProjectSelectorHTML() {
  return `
    <div class="card-glass rounded-2xl p-6 mb-6">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <div class="flex items-center gap-4">
          <label class="text-sm text-slate-400">Project:</label>
          <select id="project-select" class="bg-slate-800 border border-slate-600 text-white text-sm rounded-lg px-3 py-2 focus:outline-none focus:border-blue-500 min-w-[200px]">
            <option value="">No projects</option>
          </select>
          <button id="btn-new-project" class="text-sm px-3 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-white transition">
            <i class="fas fa-plus mr-1"></i> New
          </button>
        </div>
        <div class="flex items-center gap-4 text-sm text-slate-400">
          <span id="doc-count">0 documents</span>
          <span id="chunk-count">0 chunks indexed</span>
        </div>
      </div>
    </div>
  `;
}

export function renderNewProjectModalHTML() {
  return `
    <div id="new-project-modal" class="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
      <div class="bg-slate-800 rounded-2xl max-w-md w-full p-6 border border-slate-700">
        <h3 class="font-semibold text-white mb-4">Create New Project</h3>
        <div class="space-y-4">
          <div>
            <label class="text-sm text-slate-400 block mb-1">Project Name</label>
            <input id="new-project-name" type="text" class="w-full bg-slate-900 border border-slate-600 text-white rounded-lg px-3 py-2" placeholder="e.g., Downtown Office Tower">
          </div>
          <div>
            <label class="text-sm text-slate-400 block mb-1">Client Name</label>
            <input id="new-project-client" type="text" class="w-full bg-slate-900 border border-slate-600 text-white rounded-lg px-3 py-2" placeholder="e.g., ABC Development Corp">
          </div>
          <div class="flex gap-3">
            <button id="submit-new-project" class="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg">Create</button>
            <button id="close-new-project" class="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg">Cancel</button>
          </div>
        </div>
      </div>
    </div>
  `;
}

export function wireProjectSelector() {
  document.getElementById('btn-new-project')?.addEventListener('click', () => {
    document.getElementById('new-project-modal')?.classList.remove('hidden');
  });
  document.getElementById('close-new-project')?.addEventListener('click', () => {
    document.getElementById('new-project-modal')?.classList.add('hidden');
  });
  document.getElementById('submit-new-project')?.addEventListener('click', submitNewProject);
}

async function submitNewProject() {
  const name = document.getElementById('new-project-name').value;
  const client = document.getElementById('new-project-client').value;
  if (!name) return;
  try {
    await createProject(name, client);
    document.getElementById('new-project-modal')?.classList.add('hidden');
  } catch (e) {
    alert('Failed: ' + e.message);
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
    document.getElementById('doc-count').textContent = `${docCount} documents`;
    document.getElementById('chunk-count').textContent = `${chunkCount} chunks indexed`;
  }
}
