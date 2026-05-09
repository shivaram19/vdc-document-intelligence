/**
 * step-2-upload.js — Step 2: Add Documents
 *
 * SRP: Renders upload panel and simulated connector fallback.
 * ISP: Only importers of upload functionality need this module.
 */

import { SOURCES, ALLOWED_EXTS, FORMAT_GUIDANCE } from '../../data/connector-sources.js';

function renderFileRow(file, progress) {
  const ext = file.name.slice(file.name.lastIndexOf('.')).toLowerCase();
  const isAllowed = ALLOWED_EXTS.includes(ext);
  const icon = isAllowed ? 'fa-file text-bp-accent' : 'fa-exclamation-triangle text-warn-yellow';

  let statusHtml = '';
  if (progress === 'uploading') statusHtml = `<span class="text-[10px] text-warn-yellow font-mono">UPLOADING...</span>`;
  else if (progress === 'done') statusHtml = `<span class="text-[10px] text-safe-green font-mono"><i class="fas fa-check mr-1"></i>INDEXED</span>`;
  else if (progress === 'error') statusHtml = `<span class="text-[10px] text-hazard-red font-mono">FAILED</span>`;
  else if (typeof progress === 'number') statusHtml = `<span class="text-[10px] text-bp-accent font-mono">${progress}%</span>`;

  return `
    <div class="flex items-center justify-between py-2 border-b border-bp-light/10 last:border-0">
      <div class="flex items-center gap-2">
        <i class="fas ${icon} text-xs"></i>
        <span class="text-xs ${isAllowed ? 'text-neutral-300' : 'text-warn-yellow'}">${file.name}</span>
        ${!isAllowed ? `<span class="text-[10px] text-hazard-red font-mono">NOT SUPPORTED</span>` : ''}
      </div>
      ${statusHtml}
    </div>
  `;
}

function renderFormatGuidance() {
  const badges = [
    { icon: 'fa-file-pdf', color: 'safe-green', label: 'PDF' },
    { icon: 'fa-file-word', color: 'safe-green', label: 'DOCX' },
    { icon: 'fa-file-alt', color: 'safe-green', label: 'TXT / MD' },
    { icon: 'fa-drafting-compass', color: 'warn-yellow', label: 'DWG', tip: FORMAT_GUIDANCE['.dwg'] },
    { icon: 'fa-cube', color: 'warn-yellow', label: 'RVT', tip: FORMAT_GUIDANCE['.rvt'] },
    { icon: 'fa-building', color: 'warn-yellow', label: 'IFC', tip: FORMAT_GUIDANCE['.ifc'] },
  ];

  const cells = badges.map((b) => `
    <div class="text-center py-2 bg-${b.color}/5 border border-${b.color}/20 rounded ${b.tip ? 'cursor-help' : ''}" title="${b.tip || ''}">
      <i class="fas ${b.icon} text-${b.color} text-xs mb-1"></i>
      <p class="text-[10px] text-${b.color} font-mono">${b.label}</p>
    </div>
  `).join('');

  return `<div class="mt-4 grid grid-cols-2 md:grid-cols-3 gap-2">${cells}</div>`;
}

function renderUploadPanel(source, files, uploadProgress, uploading) {
  const fileList = files.length
    ? files.map((f) => renderFileRow(f, uploadProgress[f.name])).join('')
    : `<p class="text-xs text-neutral-600 font-mono text-center py-4">NO FILES SELECTED</p>`;

  return `
    <div>
      <div class="flex items-center justify-between mb-6">
        <div>
          <h2 class="text-xl font-bold text-white">Upload from ${source.name}</h2>
          <p class="text-xs text-neutral-500">Drag & drop or click to select files</p>
        </div>
        <button data-back class="text-xs text-neutral-500 hover:text-white transition font-mono">
          <i class="fas fa-arrow-left mr-1"></i>BACK
        </button>
      </div>

      <div id="dropzone" class="border-2 border-dashed border-bp-light/30 rounded-lg p-8 text-center cursor-pointer hover:border-bp-accent transition bg-bp-dark/30">
        <i class="fas fa-cloud-upload-alt text-3xl text-bp-accent mb-3"></i>
        <p class="text-sm text-neutral-400 mb-2">Drop PDFs, Word docs, or text files here</p>
        <p class="text-[10px] text-neutral-600 font-mono">MAX 50 MB PER FILE • AUTO-DETECTS DOC TYPE</p>
        <input type="file" id="file-input" multiple class="hidden" accept=".pdf,.docx,.doc,.txt,.md">
      </div>

      ${renderFormatGuidance()}

      <div class="mt-4 card-structural border-bp-light/20">
        <div class="flex items-center justify-between mb-2">
          <span class="text-[10px] text-neutral-500 font-mono">SELECTED FILES</span>
          <span class="text-[10px] text-neutral-500 font-mono">${files.length} FILE(S)</span>
        </div>
        <div class="max-h-48 overflow-y-auto">${fileList}</div>
      </div>

      <div class="mt-6 flex gap-3">
        <button data-upload class="btn-inspect font-mono text-sm flex-1" ${files.length === 0 || uploading ? 'disabled' : ''}>
          ${uploading ? '<i class="fas fa-spinner fa-spin mr-2"></i>INDEXING...' : '<i class="fas fa-rocket mr-2"></i>INDEX DOCUMENTS'}
        </button>
        <button data-skip class="btn-outline font-mono text-sm">SKIP</button>
      </div>
    </div>
  `;
}

function renderSimulatedConnector(source) {
  return `
    <div>
      <div class="flex items-center justify-between mb-6">
        <div>
          <h2 class="text-xl font-bold text-white">Connect to ${source.name}</h2>
          <p class="text-xs text-neutral-500">${source.subtitle}</p>
        </div>
        <button data-back class="text-xs text-neutral-500 hover:text-white transition font-mono">
          <i class="fas fa-arrow-left mr-1"></i>BACK
        </button>
      </div>

      <div class="card-structural border-warn-yellow/30 bg-warn-yellow/5">
        <div class="flex items-start gap-4">
          <div class="w-10 h-10 rounded-sm bg-warn-yellow/20 flex items-center justify-center text-warn-yellow flex-shrink-0">
            <i class="fas fa-tools"></i>
          </div>
          <div>
            <h3 class="text-sm font-bold text-white mb-1">${source.status === 'beta' ? 'Beta Access' : 'Coming Soon'}</h3>
            <p class="text-xs text-neutral-400 leading-relaxed mb-3">
              The ${source.name} connector is ${source.status === 'beta' ? 'in beta' : 'under development'}.
              ${source.status === 'beta'
                ? 'Request beta access and our team will configure the connection within 24 hours.'
                : 'Expected release: Q2 2026. Request early access to be notified when it launches.'}
            </p>
            <div class="flex gap-3">
              <button data-request class="btn-inspect font-mono text-xs">
                <i class="fas fa-paper-plane mr-2"></i>REQUEST ${source.status === 'beta' ? 'BETA ACCESS' : 'EARLY ACCESS'}
              </button>
              <button data-use-upload class="btn-outline font-mono text-xs">USE LOCAL UPLOAD INSTEAD</button>
            </div>
          </div>
        </div>
      </div>

      <div class="mt-4 text-xs text-neutral-600 font-mono">
        <i class="fas fa-info-circle mr-1"></i>
        In the meantime, export drawings to PDF and use Local Files upload.
        All documents will migrate automatically when the connector is live.
      </div>
    </div>
  `;
}

export function renderStep2(sourceId, files, uploadProgress, uploading) {
  const source = SOURCES.find((s) => s.id === sourceId);
  if (!source) return '';
  return source.id !== 'upload'
    ? renderSimulatedConnector(source)
    : renderUploadPanel(source, files, uploadProgress, uploading);
}
