/**
 * state.js — Global Reactive State
 *
 * Research basis: Li et al. (2024) "Agent-Oriented Planning" (arXiv:2410.02189)
 * — Non-Redundancy principle: state should be minimal, no duplicated data.
 * All derived values (doc counts, auth status) are computed from this single
 * source of truth, not stored redundantly.
 *
 * Language principle (JS): Object.freeze not used because Vue/React-style
 * reactivity is not present; mutation is acceptable with disciplined access
 * through this module only.
 */

export const state = {
  currentProject: null,
  projects: [],
  currentTab: 'query',
  connected: false,
  authenticated: false,
  capabilities: [],
  agentStatus: 'idle',
  recentEvents: [],
};
