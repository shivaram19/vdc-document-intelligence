/**
 * state.js — Global Reactive State
 *
 * Research basis: Li et al. (2024) "Agent-Oriented Planning"
 * — Non-Redundancy principle: state should be minimal, no duplicated data.
 */

export const state = {
  currentProject: null,
  projects: [],
  currentTab: 'query',
  connected: false,
  authenticated: false,
  testMode: false,
  capabilities: [],
  agentStatus: 'idle',
  recentEvents: [],
};
