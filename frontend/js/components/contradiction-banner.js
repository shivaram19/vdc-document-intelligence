/**
 * Contradiction Banner Component
 * Renders a collapsible warning when query-aware contradiction detection finds conflicts.
 */

export function renderContradictionBanner(contradictions) {
  if (!contradictions || contradictions.length === 0) return '';
  
  const cx = contradictions[0];
  const docList = cx.documents.slice(0, 3).join(', ');
  const moreDocs = cx.documents.length > 3 ? ` +${cx.documents.length - 3} more` : '';
  
  return `
    <div class="contradiction-banner mb-3 rounded-xl border border-amber-500/30 bg-amber-500/5 overflow-hidden">
      <button class="contradiction-toggle w-full px-4 py-3 flex items-center gap-3 text-left hover:bg-amber-500/10 transition">
        <i class="fas fa-exclamation-triangle text-amber-400"></i>
        <div class="flex-1">
          <p class="text-sm font-medium text-amber-300">
            Potential contradiction detected
          </p>
          <p class="text-xs text-amber-400/70">
            ${cx.unit.toUpperCase()}: ${cx.values.join(' vs ')} across ${docList}${moreDocs}
          </p>
        </div>
        <i class="fas fa-chevron-down text-amber-400/50 text-xs contradiction-chevron transition-transform"></i>
      </button>
      <div class="contradiction-details hidden px-4 pb-4">
        ${contradictions.map(c => `
          <div class="mt-3 pt-3 border-t border-amber-500/20">
            <p class="text-xs font-medium text-amber-300 mb-2">
              ${c.unit.toUpperCase()}: conflicting values found
            </p>
            <div class="space-y-2">
              ${c.details.map(d => `
                <div class="bg-slate-900/60 rounded-lg p-2.5">
                  <div class="flex items-center gap-2 mb-1">
                    <span class="text-xs font-bold text-white">${d.value} ${c.unit}</span>
                    <span class="text-[10px] text-slate-400">in ${d.documents.join(', ')}</span>
                  </div>
                  <p class="text-[11px] text-slate-400 italic">"...${d.contexts[0]}..."</p>
                </div>
              `).join('')}
            </div>
            ${c.query_relevance !== null ? `<p class="text-[10px] text-slate-500 mt-1">Query relevance: ${Math.round(c.query_relevance * 100)}% · Context similarity: ${Math.round(c.context_similarity * 100)}%</p>` : ''}
          </div>
        `).join('')}
        <p class="text-[10px] text-amber-400/60 mt-3">
          <i class="fas fa-info-circle mr-1"></i>
          The AI has noted this conflict in its answer. Please verify against official specifications before acting.
        </p>
      </div>
    </div>
  `;
}

export function attachContradictionListeners(container) {
  container.querySelectorAll('.contradiction-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
      const details = btn.nextElementSibling;
      const chevron = btn.querySelector('.contradiction-chevron');
      if (details.classList.contains('hidden')) {
        details.classList.remove('hidden');
        chevron.style.transform = 'rotate(180deg)';
      } else {
        details.classList.add('hidden');
        chevron.style.transform = 'rotate(0deg)';
      }
    });
  });
}
