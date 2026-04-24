/**
 * demo-state.js — Demo Mode State Manager
 *
 * [CITE: NunesDreze2006] Endowed Progress Effect: users with perceived
 * head-start complete tasks at 2x rate. Pre-loaded data = head start.
 *
 * [CITE: NortonMochonAriely2012] IKEA Effect: users value products more
 * when they invest effort. Allow ONE upload so user "builds" their demo.
 *
 * [CITE: KahnemanTversky1979] Loss Aversion: frame limits as "your demo
 * data will be lost" rather than "you cannot do this."
 */

import { DEMO_PROJECT } from './sample-data.js';

export const demoLimits = {
  customQueries: 3,
  rfiDrafts: 1,
  uploads: 1,
  scans: 1,
};

export const demoUsage = {
  customQueries: 0,
  rfiDrafts: 0,
  uploads: 0,
  scans: 0,
};

export function isDemo() {
  return window.location.hash.startsWith('#/demo');
}

export function resetDemoUsage() {
  demoUsage.customQueries = 0;
  demoUsage.rfiDrafts = 0;
  demoUsage.uploads = 0;
  demoUsage.scans = 0;
}

export function canUse(feature) {
  return demoUsage[feature] < demoLimits[feature];
}

export function use(feature) {
  if (!canUse(feature)) return false;
  demoUsage[feature] += 1;
  return true;
}

export function remaining(feature) {
  return Math.max(0, demoLimits[feature] - demoUsage[feature]);
}

export function gatePrompt(feature) {
  const messages = {
    customQueries: {
      headline: 'You have used all 3 custom queries in this demo.',
      body: 'The full Medha platform includes unlimited queries across unlimited projects. Your demo data and inspection history can be preserved.',
      cta: 'Request Full Access',
      sub: 'Or continue with pre-loaded quick questions below',
    },
    rfiDrafts: {
      headline: 'RFI draft limit reached (1 of 1).',
      body: 'Full users generate 15+ RFIs per week with 87% first-submission acceptance. Unlock unlimited drafting with spec-cited evidence.',
      cta: 'Unlock Unlimited Drafts',
      sub: 'Your drafted RFI is preserved below',
    },
    uploads: {
      headline: 'Demo upload limit reached (1 of 1).',
      body: 'Full users ingest 500+ page spec sets in under 90 seconds. The Librarian Agent auto-chunks, embeds, and indexes everything.',
      cta: 'Get Full Ingestion',
      sub: 'Your uploaded file is in the inbox below',
    },
    scans: {
      headline: 'Demo scan limit reached (1 of 1).',
      body: 'Spotter Agent runs continuous contradiction scans across your entire document set. Full users catch conflicts before they hit the field.',
      cta: 'Enable Continuous Scanning',
      sub: 'Pre-computed scan results are preserved below',
    },
  };
  return messages[feature] || messages.customQueries;
}

export function injectDemoProject(state) {
  state.currentProject = DEMO_PROJECT.id;
  state.projects = [DEMO_PROJECT];
}
