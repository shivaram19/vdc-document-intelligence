/**
 * inbox-panel.js — Document Upload Panel
 *
 * SOLID: SRP — only file dropzone, upload list, and type selector.
 */

import { state } from '../../state.js';

export function renderInboxPanelHTML() {
  return `
    <div class="card-glass rounded-2xl p-6">
      <h3 class="font-semibold text-white mb-4"><i class="fas fa-inbox mr-2 text-blue-400"></i>Document Inbox</h3>
      <p class="text-sm text-slate-400 mb-4">
        Drop files here or use the file picker. The document parser agent (node-e) will automatically
        ingest, chunk, and embed them. Files are moved to <code class="bg-slate-800 px-1 rounded">picocloth/shared/project/vdc/inbox/</code>.
      </p>
      <div class="border-2 border-dashed border-slate-600 rounded-xl p-8 text-center mb-6 hover:border-blue-500 transition cursor-pointer" id="upload-dropzone">
        <i class="fas fa-cloud-upload-alt text-4xl text-slate-500 mb-3"></i>
        <p class="text-white font-medium">Click to upload or drag and drop</p>
        <p class="text-sm text-slate-400 mt-1">PDF, DOCX, TXT supported</p>
        <input id="file-input" type="file" multiple accept=".pdf,.docx,.txt,.md" class="hidden">
      </div>
      <div class="grid md:grid-cols-2 gap-4 mb-4">
        <div>
          <label class="text-sm text-slate-400 block mb-1">Document Type</label>
          <select id="upload-type" class="w-full bg-slate-800 border border-slate-600 text-white text-sm rounded-lg px-3 py-2">
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
    item.className = 'flex items-center gap-3 p-3 bg-slate-800/50 rounded-lg';
    item.innerHTML = `<i class="fas fa-file-alt text-blue-400"></i><span class="text-sm text-white flex-1">${file.name}</span><span class="text-xs text-slate-500">Uploading to inbox...</span>`;
    list.appendChild(item);

    try {
      const form = new FormData();
      form.append('file', file);
      const resp = await fetch('/inbox', { method: 'POST', body: form });
      if (!resp.ok) throw new Error(await resp.text());
      item.innerHTML = `<i class="fas fa-check text-emerald-400"></i><span class="text-sm text-white flex-1">${file.name}</span><span class="text-xs text-emerald-400">In inbox — agent will process</span>`;
    } catch (e) {
      item.innerHTML = `<i class="fas fa-times text-red-400"></i><span class="text-sm text-white flex-1">${file.name}</span><span class="text-xs text-red-400">${e.message}</span>`;
    }
  }
  input.value = '';
}
