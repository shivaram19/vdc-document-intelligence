/**
 * shared.js — Connector Onboarding Shared UI Helpers
 *
 * SRP: Only shared rendering utilities. No step logic.
 */

export function renderStatusBadge(status) {
  const map = {
    live: ['bg-safe-green/20', 'text-safe-green', 'LIVE'],
    beta: ['bg-warn-yellow/20', 'text-warn-yellow', 'BETA'],
    planned: ['bg-gray-700/50', 'text-gray-500', 'SOON'],
  };
  const [bg, text, label] = map[status] || map.planned;
  return `<span class="px-2 py-1 rounded-sm text-[10px] font-mono font-bold ${bg} ${text}">${label}</span>`;
}
