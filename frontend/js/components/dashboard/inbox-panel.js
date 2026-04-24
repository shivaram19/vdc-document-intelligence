/**
 * inbox-panel.js — Document Upload Panel
 * SOLID: SRP — only file dropzone, upload list, and type selector.
 */

import { state } from '../../state.js';

export function renderInboxPanelHTML() {
  return `
    <div class="card-structural">
      <h3 class="font-semibold text-white mb-4 flex items-center gap-2 font-mono text-sm">
        <i class="fas fa-inbox text-bp-accent text-xs"></i> DOCUMENT INBOX
      </h3>
      <p class="text-sm text-gray-500 mb-4">
        Drop files here or use the file picker. Librarian Agent (node-e) will automatically
        ingest, chunk, and embed them for inspection.
      </p>
      <div class="border-2 border-dashed border-bp-light/40 rounded-sm p-8 text-center mb-6 hover:border-bp-accent transition cursor-pointer" id="upload-dropzone">
        <i class="fas fa-cloud-upload-alt text-4xl text-gray-600 mb-3"></i>
        <p class="text-white font-medium font-mono text-sm">CLICK TO UPLOAD OR DRAG AND DROP</p>
        <p class="text-sm text-gray-600 mt-1 font-mono">PDF, DOCX, TXT SUPPORTED</p>
        <input id="file-input" type="file" multiple accept=".pdf,.docx,.txt,.md" class="hidden">
      </div>
      <div class="grid md:grid-cols-2 gap-4 mb-4">
        <div>
          <label class="text-sm text-gray-500 block mb-1 font-mono">DOCUMENT TYPE</label>
          <select id="upload-type" class="w-full bg-bp-dark border border-bp-light/50 text-white text-sm rounded-sm px-3 py-2 font-mono">
            <option value="drawing">Drawing / Plan</option>
            <option value="spec">Specification</option>
            <option value="rfi">RFI / Correspondence</option>
            <option value="submittal">Submittal</option>
            <option value="addendum">Addendum</option>
          </select>
        </div>
      </div>
      <div id="upload-list" class="space-y-2"></div>
    </div>
  `;
}

export function wireInboxPanel() {
  document.getElementById('upload-dropzone')?.addEventListener('click', () => {
    document.getElementById('file-input')?.click();
  });
  document.getElementById('file-input')?.addEventListener('change', function () {
    handleFileUpload(this);
  });
}

async function handleFileUpload(input) {
  if (!state.currentProject) {
    alert('Please select or create a project first.');
    return;
  }
  const files = input.files;
  const type = document.getElementById('upload-type').value;
  const list = document.getElementById('upload-list');

  for (const file of files) {
    const item = document.createElement('div');
    item.className = 'flex items-center gap-3 p-3 bg-bp-dark/50 rounded-sm border border-bp-light/20';
    item.innerHTML = `<i class="fas fa-file-alt text-bp-accent text-xs"></i><span class="text-sm text-white flex-1 font-mono">${file.name}</span><span class="text-xs text-gray-600 font-mono">UPLOADING...</span>`;
    list.appendChild(item);

    try {
      const form = new FormData();
      form.append('file', file);
      const resp = await fetch('/inbox', { method: 'POST', body: form });
      if (!resp.ok) throw new Error(await resp.text());
      item.innerHTML = `<i class="fas fa-check text-safe-green text-xs"></i><span class="text-sm text-white flex-1 font-mono">${file.name}</span><span class="text-xs text-safe-green font-mono">IN INBOX — AGENT WILL PROCESS</span>`;
    } catch (e) {
      item.innerHTML = `<i class="fas fa-times text-safe-red text-xs"></i><span class="text-sm text-white flex-1 font-mono">${file.name}</span><span class="text-xs text-safe-red font-mono">${e.message}</span>`;
    }
  }
  input.value = '';
}
