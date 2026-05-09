/**
 * step-3-verify.js — Step 3: Verify & Connect
 *
 * SRP: Renders ONLY the confirmation/success step.
 */

import { SOURCES } from '../../data/connector-sources.js';

export function renderStep3(sourceId, files, uploadProgress) {
  const source = SOURCES.find((s) => s.id === sourceId);
  const doneCount = Object.values(uploadProgress).filter((s) => s === 'done').length;

  return `
    <div>
      <div class="text-center mb-8">
        <div class="w-16 h-16 rounded-full bg-safe-green/20 flex items-center justify-center mx-auto mb-4">
          <i class="fas fa-check text-2xl text-safe-green"></i>
        </div>
        <h2 class="text-2xl font-bold text-white mb-2">Connection Established</h2>
        <p class="text-sm text-neutral-400">
          ${doneCount} of ${files.length} documents indexed from ${source?.name || 'Local Files'}.
          Your project is ready for inspection.
        </p>
      </div>

      <div class="grid md:grid-cols-2 gap-4 mb-8">
        <div class="card-structural text-center">
          <div class="text-3xl font-bold text-white mb-1">${doneCount}</div>
          <p class="text-[10px] text-neutral-500 font-mono">DOCUMENTS INDEXED</p>
        </div>
        <div class="card-structural text-center">
          <div class="text-3xl font-bold text-bp-accent mb-1">~${doneCount * 180}</div>
          <p class="text-[10px] text-neutral-500 font-mono">CHUNKS EMBEDDED</p>
        </div>
      </div>

      <div class="card-structural border-bp-accent/30 bg-bp-accent/5 mb-6">
        <h3 class="text-sm font-bold text-white mb-2"><i class="fas fa-magic mr-2 text-bp-accent"></i>WHAT HAPPENS NEXT?</h3>
        <ul class="space-y-2 text-xs text-neutral-400">
          <li class="flex items-start gap-2">
            <i class="fas fa-search text-bp-accent mt-0.5"></i>
            <span><strong>Contradiction Scan:</strong> Medha is scanning your documents for inconsistencies between specs and drawings.</span>
          </li>
          <li class="flex items-start gap-2">
            <i class="fas fa-brain text-bp-accent mt-0.5"></i>
            <span><strong>Semantic Index:</strong> Every paragraph is embedded for instant semantic search.</span>
          </li>
          <li class="flex items-start gap-2">
            <i class="fas fa-bell text-bp-accent mt-0.5"></i>
            <span><strong>Real-Time Alerts:</strong> You'll be notified when contradictions are found.</span>
          </li>
        </ul>
      </div>

      <div class="flex gap-3">
        <button data-go-dashboard class="btn-inspect font-mono text-sm flex-1">
          <i class="fas fa-rocket mr-2"></i>GO TO DASHBOARD
        </button>
        <button data-add-more class="btn-outline font-mono text-sm">ADD MORE DOCUMENTS</button>
      </div>
    </div>
  `;
}
