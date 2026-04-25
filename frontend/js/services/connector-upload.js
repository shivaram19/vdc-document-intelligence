/**
 * connector-upload.js — Upload Simulation Service
 *
 * SRP: Handles ONLY file validation and upload orchestration.
 * DIP: Depends on abstractions (callbacks), not DOM or UI details.
 * OCP: Swap simulateUpload for real fetch() without changing callers.
 */

import { isAllowedExt, getGuidance } from '../data/connector-sources.js';

/**
 * Filter valid files, log guidance for rejected ones.
 * @param {FileList} fileList
 * @param {Function} onGuidance — callback(guidanceText, filename)
 * @returns {File[]}
 */
export function filterValidFiles(fileList, onGuidance) {
  return Array.from(fileList).filter((f) => {
    if (isAllowedExt(f.name)) return true;
    const guidance = getGuidance(f.name);
    if (guidance && onGuidance) onGuidance(guidance, f.name);
    return false;
  });
}

/**
 * Simulate upload + indexing with per-file progress callbacks.
 * @param {File[]} files
 * @param {Object} callbacks — { onStart(file), onProgress(file, percent), onDone(file), onError(file) }
 * @returns {Promise<void>}
 */
export async function simulateUpload(files, callbacks = {}) {
  for (const file of files) {
    if (callbacks.onStart) callbacks.onStart(file);

    const steps = [
      { pct: 25, delay: 400 + Math.random() * 400 },
      { pct: 60, delay: 300 + Math.random() * 300 },
      { pct: 90, delay: 200 + Math.random() * 200 },
      { pct: 100, delay: 150 + Math.random() * 150 },
    ];

    for (const step of steps) {
      await sleep(step.delay);
      if (callbacks.onProgress) callbacks.onProgress(file, step.pct);
    }

    if (Math.random() < 0.05) {
      if (callbacks.onError) callbacks.onError(file);
    } else {
      if (callbacks.onDone) callbacks.onDone(file);
    }
  }
}

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}
